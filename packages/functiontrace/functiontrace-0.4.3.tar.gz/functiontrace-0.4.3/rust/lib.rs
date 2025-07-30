#[pyo3::pymodule]
mod _functiontrace_rs {
    use color_eyre::eyre::{eyre, OptionExt, Result, WrapErr};
    use functiontrace_server::function_trace;
    use pyo3::prelude::*; // TODO: What's in here?
    use serde::Serialize;
    use std::borrow::Cow;
    use std::ffi::{c_void, CStr, OsString};
    use std::io::Write;
    use std::os::unix::net::UnixStream;
    use std::sync::atomic::{AtomicBool, AtomicU32, Ordering};
    use std::sync::OnceLock;
    use std::time::Duration;

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Core Types
    ////////////////////////////////////////////////////////////////////////////////////////////////
    /// The size of messagepack buffers.  This is picked somewhat arbitrarily, but should be
    /// reasonably small since we'll need one per thread, and should be large enough that we
    /// can fit many messages in before needing to do expensive UnixStream syscalls.
    const MPACK_BUFFER: usize = 1 << 17;

    /// Storage specific to each thread used for buffering/transmitting data.
    type ThreadState = MpackWriter;

    /// A `mpack_writer_t` struct, which `mpack.h` will use to pass us our per-thread context in.
    ///
    /// NOTE: This must directly match the `mpack_writer_t` definition in C, since we're going to
    /// be creating and modifying it ourselves!
    #[repr(C)]
    pub struct MpackWriter {
        flush: extern "C" fn(writer: *const MpackWriter, buffer: *const u8, bytes: usize),
        error_fn: *const (),
        teardown: *const (),
        context: *mut UnixStream,

        buffer: *mut u8,
        current: *mut u8,
        end: *mut u8,

        // XXX: This is an enum that we never use.  Since it doesn't have a clearly-defined size,
        // we allocate 8 bytes for it.  We MUST NOT access this field!
        _error: u64,
    }

    impl Write for MpackWriter {
        /// A small [`Write`] implementation that allows us to write to an
        /// `mpack_writer_t`'s interior buffer while keeping its state consistent.
        fn write(&mut self, src: &[u8]) -> std::io::Result<usize> {
            if !STARTED.load(Ordering::Relaxed) {
                // We haven't started yet, so we shouldn't write anything out.  This avoids logging
                // various internal setup things before we're ready.
                return Ok(src.len());
            }

            let len = unsafe {
                // SAFETY: writer.(current|end) are both within writer.buffer.
                self.end.offset_from(self.current)
            }
            .try_into()
            .expect("end > current");

            let bytes = src.len();

            if bytes > len {
                if bytes >= MPACK_BUFFER {
                    // We'll never be able to fit this much.
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::StorageFull,
                        "mpack buffer too small",
                    ));
                }

                // We can't fit any more data, so need to flush.  The caller should retry after
                // this.
                self.flush()?;

                return Err(std::io::Error::new(
                    std::io::ErrorKind::Interrupted,
                    "mpack buffer is full, flushing",
                ));
            }

            let buf = unsafe { std::slice::from_raw_parts_mut(self.current, len) };

            buf[..bytes].copy_from_slice(src);

            unsafe {
                // SAFETY: end = current + len, and bytes < len, so current + bytes < end
                self.current = self.current.add(bytes)
            };

            Ok(bytes)
        }

        /// This roughly implements `Mpack_Flush`.
        fn flush(&mut self) -> std::io::Result<()> {
            let len = unsafe {
                // SAFETY: writer.current is within writer.buffer.
                self.current.offset_from(self.buffer)
            }
            .try_into()
            .expect("current > end");

            let data = unsafe { std::slice::from_raw_parts_mut(self.buffer, len) };

            // We're about to send all of the data, so reset our buffer.  Do this now to ensure we
            // don't miss it, since the buffer will be left in an invalid state if this doesn't
            // happen.
            self.current = self.buffer;

            let mut socket = unsafe {
                // SAFETY: `writer` is valid and `writer->context` contains a `UnixStream` emitted from
                // `thread_register`.
                self.context.as_ref().expect("context is non-null")
            };
            socket.write_all(data)
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Global Data
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// The UnixStream address we're using to communicate with the profile server.
    static SOCKADDR: OnceLock<OsString> = OnceLock::new();

    /// The pthread_key we use for accessing [`ThreadState`], acquired from the C extension.
    ///
    /// NOTE: We store this as an atomic rather than use a [`OnceLock`] since we need to access it
    /// in the critical path.  There's some overhead to `OnceLock` acquisitions, while simple loads
    /// and stores of [`AtomicU32`]s have no overhead (at least on x86).
    static TSS_KEY: AtomicU32 = AtomicU32::new(0);

    /// `sys.argv` for our process, which is used when registering new threads.
    static ARGV: OnceLock<String> = OnceLock::new();

    /// True iff we've started tracing and haven't been marked as terminated.  When this is
    /// set, we're allowed to send messages to the profile generation server.
    static STARTED: AtomicBool = AtomicBool::new(false);

    /// The `Fprofile_FunctionTrace` function defined in the C extension.  This is needed to finish
    /// moving setup to the Rust code.
    static TRACEFUNC: OnceLock<pyo3::ffi::Py_tracefunc> = OnceLock::new();

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Rust <-> C Communication
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// We expose all of our C functions in a single struct that's loaded once at the start of the
    /// program, avoiding most of the overhead from the previous `dlopen-esque` interface.
    #[derive(Debug)]
    #[repr(C)]
    struct RustFunctions {
        set_config: usize,
    }

    /// It's easiest to return pointer-sized types over the Python API, so allocate our
    /// [`RustFunctions`] and leak it.  This will be used by the C extension and never freed.
    #[pyfunction]
    fn c_api() -> usize {
        let api = Box::new(RustFunctions {
            set_config: set_config as usize,
        });

        Box::into_raw(api) as usize
    }

    /// Called by the C module to pass the `c_functiontrace` handler to us.
    #[unsafe(no_mangle)]
    extern "C" fn set_config(c_functiontrace: pyo3::ffi::Py_tracefunc) -> libc::pthread_key_t {
        // Allocate a Tss_Key for storing thread state
        let mut tss_key = 0;
        if unsafe {
            // SAFETY: tss_key is live
            libc::pthread_key_create(&raw mut tss_key, Some(c_thread_teardown))
        } != 0
        {
            panic!("Failed to create Tss_Key");
        }

        TRACEFUNC
            .set(c_functiontrace)
            .expect("set_config can only be called once");

        TSS_KEY.store(tss_key, Ordering::Relaxed);

        tss_key
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Utility Functions
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// This effectively fetches the output of RDTSC, making it quick but not very useful on its
    /// own, as there is no meaningful epoch for the time.
    ///
    /// Using `Duration` is a bit weird, but for legacy reasons we're stuck with it.
    #[inline(always)]
    pub fn trace_time() -> Duration {
        let mut time = libc::timespec {
            tv_sec: 0,
            tv_nsec: 0,
        };

        unsafe {
            // SAFETY: `time` is a mutable object that's in scope for this call.
            libc::clock_gettime(libc::CLOCK_MONOTONIC, &raw mut time)
        };

        Duration::new(time.tv_sec as u64, time.tv_nsec as u32)
    }

    /// Return the [`ThreadState`] for the current thread.  This should either be None (during
    /// startup), or a valid [`ThreadState`] that has been allocated on the heap and leaked via
    /// `Box::into_raw`.
    #[inline(always)]
    pub fn thread_state() -> Option<&'static mut ThreadState> {
        // Check that we're able to properly initialize
        let tss_key = TSS_KEY.load(Ordering::Relaxed);

        let state = unsafe {
            // SAFETY: tss_key is a valid `pthread_key_t`
            libc::pthread_getspecific(tss_key) as *mut ThreadState
        };

        if state.is_null() {
            // We shouldn't be asked to reset at thread that hasn't yet been registered.
            return None;
        }

        Some(unsafe {
            // SAFETY: state is a valid pointer to a ThreadState, since we always remove from TLS
            // before freeing.
            state.as_mut().expect("state is non-null")
        })
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Socket Communication
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// Initializes and returns the [`UnixStream`] we'll communicate to `functiontrace-server` on.
    fn message_initialize() -> Box<UnixStream> {
        let sockaddr = SOCKADDR
            .get()
            .expect("Must be initialized before setting up messaging");

        // The functiontrace-server might not be ready to receive connections yet, so we retry for
        // a bit.
        let start = std::time::Instant::now();
        loop {
            match UnixStream::connect(sockaddr) {
                Ok(s) => {
                    break Box::new(s);
                }
                _ => {
                    if start.elapsed() > Duration::from_millis(1000) {
                        panic!("Timed out trying to connect to functiontrace-server");
                    }

                    std::thread::sleep(Duration::from_millis(10));
                }
            }
        }
    }

    /// Flush events to this socket once the given buffer is full according to `mpack`.
    #[unsafe(no_mangle)]
    extern "C" fn Mpack_Flush(writer: *const MpackWriter, buffer: *const u8, bytes: usize) {
        let data = unsafe {
            // SAFETY: `bytes` represents the initialized number of bytes in `buffer` when called
            // by `mpack_writer_flush_message`.
            std::slice::from_raw_parts(buffer, bytes)
        };

        let mut socket = unsafe {
            // SAFETY: `writer` is valid and `writer->context` contains a `UnixStream` emitted from
            // `register_thread`.
            writer
                .as_ref()
                .expect("writer is non-null")
                .context
                .as_ref()
                .expect("context is non-null")
        };
        if let Err(e) = socket.write_all(data) {
            panic!("Socket send failed: {e}");
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Tracing Implementation
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// Initialization code run on this module's import (mostly useful for adding constants)
    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        // Arbitrary code to run at the module initialization
        m.add("__version__", env!("PACKAGE_VERSION"))
            .wrap_err("Failed to expose PACKAGE_VERSION")?;

        color_eyre::install().wrap_err("Failed to install color_eyre")?;

        Ok(())
    }

    /// Setup the initial FunctionTrace configuration, including spawning `functiontrace-server`
    /// and sending an initialization message if necessary.
    #[pyfunction]
    #[pyo3(name = "begin_tracing")]
    #[pyo3(pass_module)]
    fn trace_initialization(
        module: &Bound<'_, PyModule>,
        output_directory: OsString,
    ) -> Result<()> {
        // The name of the env var we use to notify subprocesses that there's a trace in progress.
        const BREADCRUMB: &str = "FUNCTIONTRACE_LIVE";

        // Track whether we've been initialized yet, since that's an invalid state.
        static INITIALIZED: OnceLock<()> = OnceLock::new();

        if INITIALIZED.set(()).is_err() {
            // This can be triggered by running `functiontrace.begin_tracing()` from inside a
            // process that's already being traced.  We'll fail in this situation, but might as
            // well print a mildly helpful error message here.
            return Err(eyre!("FunctionTrace is already initialized!"));
        }

        // Check if we're in a subprocess of a command being run under functiontrace.  If we are,
        // we should connect to the same socket.  Otherwise, we should setup the full profiling
        // configuration ourselves.
        if let Some(existing_sockaddr) = std::env::var_os(BREADCRUMB) {
            // A functiontrace-server is already running and listening.  All we need to do is save
            // the address so we know where to talk to.
            SOCKADDR
                .set(existing_sockaddr)
                .expect("sockaddr is only set in `trace_initialization`");
            return Ok(());
        }

        // Launch the functiontrace-server as a daemon, then record the address of the socket we'll
        // need to communicate with it on.
        let sockaddr = {
            let server = std::process::Command::new("functiontrace-server")
                .arg("--directory")
                .arg(output_directory)
                .spawn()
                .wrap_err("Failed to launch functiontrace-server")?;

            format!("/tmp/functiontrace-server.sock.{}", server.id()).into()
        };

        Python::with_gil(|_| {
            // Register an env var so subprocesses know how to connect to our
            // profile.
            unsafe {
                // SAFETY: `set_var` can only be done while no one else is reading or writing to the
                // environment.  We're holding the GIL, so this _should_ be true, but there's no real
                // way to enforce this.
                //
                // This doesn't seem to blow up in C even when we don't have the GIL, so
                // it's hopefully good enough in practice since there's not really an alternative.
                std::env::set_var(BREADCRUMB, &sockaddr);
            }
        });

        // Store the server's address so our threads know how to talk to it.
        SOCKADDR
            .set(sockaddr)
            .expect("sockaddr is only set in `trace_initialization`");

        // Send an initialization message to the server with some information about us.  This will
        // only be sent once, and all future threads/subprocesses will be associated underneath us.
        let init = {
            let argv = {
                // Parse  args out of `sys.argv`, since it excludes the Python executable and shows
                // the script's path first.  This is much more complicated than using
                // `std::env::args`, but is more practical.
                let args_prefix = Python::with_gil(|py| -> Result<String> {
                    let argv = py
                        .import("sys")
                        .and_then(|sys| sys.getattr("argv"))
                        .wrap_err("Failed to access sys.argv")?;

                    let args = argv
                        .downcast::<pyo3::types::PyList>()
                        .map_err(|e| eyre!("Failed to read sys.argv as list: {}", e))?;

                    let mut full_args = args.iter().fold(String::new(), |s, arg| {
                        // Fetch the next arg as a string if possible.
                        let arg = arg
                            .downcast::<pyo3::types::PyString>()
                            .map_err(|e| eyre!("Failed to read sys.argv[x] as string: {}", e))
                            .and_then(|arg| {
                                arg.to_str()
                                    .wrap_err("Failed to read Rust string out of PyString")
                            })
                            .unwrap_or("<UNKNOWN>");

                        s + " " + arg
                    });

                    // We'll display this in the UI, so ensure it's under (the rather
                    // arbitrary) 100 chars.
                    if full_args.chars().count() > 95 {
                        full_args.truncate(95);
                        full_args.push_str(" ...");
                    }

                    // We'll be cloning this
                    full_args.shrink_to_fit();
                    Ok(full_args)
                })
                .unwrap_or_else(|_err| {
                    // TODO: tracing log that this happened
                    "<UNKNOWN>".into()
                });

                // Store the args, since threads will need it as part of the registration message.
                ARGV.set(args_prefix.clone())
                    .expect("ARGV is only set in `trace_initialization`");

                args_prefix
            };

            let python_version = Python::with_gil(|py| {
                let version = py.version_info();

                format!(
                    "Python {}.{}.{}",
                    version.major, version.minor, version.patch
                )
            });

            let platform = Python::with_gil(|py| -> Result<String> {
                let platform = py
                    .import("sys")
                    .and_then(|sys| sys.getattr("platform"))
                    .wrap_err("Failed to access sys.platform")?;

                Ok(platform
                    .downcast::<pyo3::types::PyString>()
                    .map_err(|e| eyre!("Failed to read sys.platform as string: {}", e))?
                    .to_str()
                    .wrap_err("Failed to read Rust string out of PyString")?
                    .into())
            })
            .unwrap_or_else(|_err| {
                // TODO: tracing log that this happened
                "<UNKNOWN>".into()
            });

            function_trace::TraceInitialization {
                program_name: argv,
                program_version: format!("py-functiontrace {}", env!("PACKAGE_VERSION")),
                lang_version: python_version,
                platform,
                time: trace_time(),
            }
        };

        let mut socket = message_initialize();

        init.serialize(&mut rmp_serde::encode::Serializer::new(&mut socket))
            .wrap_err("Failed to emit TraceInitialization message")?;

        // Close the initialization socket to trigger `functiontrace-server` to
        // read our message, since otherwise it'll wait forever for more data.
        socket
            .shutdown(std::net::Shutdown::Both)
            .wrap_err("Failed to close initialization socket")?;

        ////////////////////////////////////////////////////////////////////////////
        // Teardown Configuration
        ////////////////////////////////////////////////////////////////////////////
        // Ensure we're properly handling teardown scenarios, including flushing data in both
        // single and multi-threaded scenarios, and reseting anything that's needed on forks.

        // Mark that we'll need to forget some information on forks.  In
        // particular, we shouldn't think that we have a thread that's sent any
        // information.
        if unsafe { libc::pthread_atfork(None, None, Some(c_thread_reset)) } != 0 {
            return Err(eyre!("Failed to register pthread_atfork() handler"));
        }

        // Things can get into a weird state during shutdown due to GC
        // (bugs.python.org/issue21512).  Halt our tracing instead to avoid odd behaviour and
        // ensure we've flushed all our data.
        //
        // NOTE: We specifically do this rather than `Py_AtExit`  since we want to run before all
        // the Python teardown occurs.
        Python::with_gil(|py| -> Result<()> {
            py.import("atexit")
                .and_then(|atexit| atexit.getattr("register"))
                .wrap_err("Failed to access atexit.register")?
                .call1((pyo3::types::PyCFunction::new_closure(
                    py,
                    Some(c"trace_terminate"),
                    Some(c"Stop functiontrace recording"),
                    trace_terminate,
                )
                .wrap_err("Failed to convert trace_terminate to closure")?,))
                .wrap_err("Unsuccessful call")?;

            Ok(())
        })
        .wrap_err("Failed to register `atexit` handler")?;

        ////////////////////////////////////////////////////////////////////////////
        // Tracing Configuration
        ////////////////////////////////////////////////////////////////////////////
        // We now have the infrastructure setup to handle tracing.  Let's start capturing traces!

        // Register the current thread for tracing
        thread_register().wrap_err("Failed to register initial FunctionTrace thread")?;

        // Register our tracing functions with Python - both the normal one and the multithreaded
        // setup trampoline.
        unsafe {
            // SAFETY: both parameters are of the proper type.
            pyo3::ffi::PyEval_SetProfile(Some(functiontrace), std::ptr::null_mut())
        };

        Python::with_gil(|py| -> Result<()> {
            py.import("threading")
                .and_then(|threading| threading.getattr("setprofile"))
                .wrap_err("Failed to access threading.setprofile")?
                .call1((module
                    .getattr("_thread_trace_trampoline")
                    .wrap_err("Failed to retrieve trampoline")?,))
                .wrap_err("Failed to call threading.setprofile")?;

            Ok(())
        })
        .wrap_err("Failed to install multithreaded trace trampoline")?;

        // Hook various functions to enhance our logs
        crate::hooks::install().wrap_err("Failed to install Python hooks")?;

        // We're now fully setup and allowed to send messages.
        STARTED.store(true, Ordering::Relaxed);

        Ok(())
    }

    /// Called when the process is shutting down via `atexit`, notifies us to stop tracing and
    /// flush the buffer.  
    ///
    /// NOTE: This is always called on the main thread.
    fn trace_terminate(
        _: &Bound<'_, pyo3::types::PyTuple>,
        _kwargs: Option<&Bound<'_, pyo3::types::PyDict>>,
    ) -> Result<()> {
        // Stop profiling and don't allow further logging, then flush any remaining messages.
        STARTED.store(false, Ordering::Relaxed);

        unsafe {
            // PyEval_SetProfile(NULL, NULL) is the proper way to deregister a profiler.
            pyo3::ffi::PyEval_SetProfile(None, std::ptr::null_mut());
        }

        // TODO: We could easily keep track of all the outstanding Writers and flush them all too.
        if let Some(writer) = thread_state() {
            thread_teardown(writer).wrap_err("Failed to teardown main thread")?;
        }

        Ok(())
    }

    /// Register a new thread, including creating the UnixStream for mpack to log messages for this
    /// thread on.
    ///
    /// A new [`ThreadState`] will be returned, which contains a fully initialized `MpackWriter`.
    /// This state must be returned to Rust code later to be freed.
    fn thread_register() -> Result<()> {
        if thread_state().is_some() {
            // We shouldn't have a ThreadState yet, as we're the ones that create it.
            return Err(eyre!("Thread has already been registered"));
        }

        let register =
            function_trace::FunctionTrace::RegisterThread(function_trace::ThreadRegistration {
                program_name: ARGV
                    .get()
                    .ok_or_eyre(eyre!("sys.argv hasn't been parsed yet"))?
                    .clone(),
                pid: std::process::id() as usize,
                time: trace_time(),
            });

        let mut socket = message_initialize();

        // Write this registration message directly to the socket to ensure we'll record
        // *something* for this thread even in the case where we quickly exit.
        //
        // TODO: We should have a different approach that doesn't require explicit flushing.
        // https://crates.io/crates/iceoryx2 looks like a good option once we're fully in Rust.
        register
            .serialize(&mut rmp_serde::encode::Serializer::new(&mut socket))
            .wrap_err("Failed to emit RegisterThread message")?;

        // Allocate a new buffer for mpack to write messages into.
        // This will be stored in ThreadState, and will need to be freed by Rust code.
        let buf = Box::into_raw(Box::new([0u8; MPACK_BUFFER])) as *mut u8;

        // Initialize the `MpackWriter` for this thread, then associate the socket with it.
        //
        // We'll return this state to the C code, which must pass it back to us to avoid leaking.
        let state = Box::into_raw(Box::new(
            // XXX: This must match `mpack_writer_init`, since mpack.c will be using this structure
            // later!
            MpackWriter {
                context: Box::into_raw(socket),
                flush: Mpack_Flush,

                buffer: buf as _,
                current: buf as _,
                end: unsafe {
                    // SAFETY: buf is an allocated array of MPACK_BUFFER bytes
                    buf.add(MPACK_BUFFER)
                } as _,

                teardown: std::ptr::null(),
                error_fn: std::ptr::null(),
                _error: 0,
            },
        ));

        // Store our state in thread-specific storage so we can find it in the future.
        // Tracing begins for the thread at this point, since we've now published `state` for other
        // functions to start using.
        let tss_key = TSS_KEY.load(Ordering::Relaxed);

        if unsafe {
            // SAFETY: tss_key is a valid `pthread_key_t`, and `state` is a valid pointer to a
            // heap-allocated `ThreadState` object
            libc::pthread_setspecific(tss_key, state as *const _)
        } != 0
        {
            return Err(eyre!("Failed to set tss_key on thread startup"));
        }

        Ok(())
    }

    #[unsafe(no_mangle)]
    extern "C" fn c_thread_teardown(state: *mut c_void) {
        if state.is_null() {
            // We never fully initialized this thread, so skip teardown.
            return;
        }

        let writer = unsafe {
            // SAFETY: writer is a valid pointer to an initialized `MpackWriter`.
            &mut (state as *mut ThreadState)
                .as_mut()
                .expect("state is non-null")
        };

        thread_teardown(writer).expect("Failed to tear down FunctionTrace thread")
    }

    /// Tear down the given thread by flushing any outstanding messages.
    ///
    /// This is called when the thread has shut down, including in multithread/process situations.
    pub fn thread_teardown(writer: &mut MpackWriter) -> Result<()> {
        writer
            .flush()
            .wrap_err("Failed to flush remaining messages")?;

        // TODO: We should tear down the socket to avoid leaking O(# threads) resources.
        // Historically doing this has crashed for some reason...
        //
        // TODO: And we should probably free state since it's pretty large...
        Ok(())
    }

    #[unsafe(no_mangle)]
    extern "C" fn c_thread_reset() {
        thread_reset().expect("Failed to reset FunctionTrace thread state")
    }

    /// We have some existing thread state that we should free and forget about before resuming
    /// logging.
    ///
    /// This is useful when we've just forked and want to ensure we don't reuse an existing socket.
    fn thread_reset() -> Result<()> {
        let tss_key = TSS_KEY.load(Ordering::Relaxed);

        if !STARTED.load(Ordering::Relaxed) {
            // We haven't actually started yet, but are for some reason being asked
            // to fork.  This appears to be OS dependent.
            return Ok(());
        }

        // Load the old state so we can free it.
        let state = thread_state().ok_or_eyre(eyre!("Thread wasn't yet registered"))?;

        // Remove the TLS reference so no one else can load state after we've freed it.
        if unsafe {
            // SAFETY: tss_key is a valid `pthread_key_t`, and `state` is a valid pointer to a
            // heap-allocated `ThreadState` object
            libc::pthread_setspecific(tss_key, std::ptr::null())
        } != 0
        {
            return Err(eyre!("Failed to clear TLS"));
        }

        let buf = unsafe {
            // SAFETY: writer.buffer contains a valid pointer to a boxed buffer
            (state.buffer as *mut [u8; MPACK_BUFFER])
                .as_mut()
                .expect("buffer is initialized when state is and is never modified")
        };

        // Free the thread's mpack state
        unsafe {
            let _ = Box::from_raw(buf);
            let _ = Box::from_raw(state);
        }

        // TODO: Should we free the socket too?

        // Create a new thread for this process.  We don't need to start an entire new trace like
        // with subprocess calls since we were forked and therefore already share our
        // configuration.
        thread_register().wrap_err("Failed to register new thread")?;

        Ok(())
    }

    /// Internal helper that installs FunctionTrace on each new thread's startup.
    ///
    /// This is installed as the setprofile() handler for new threads by threading.setprofile().
    /// On its first execution, it initializes tracing for the thread, including creating the
    /// thread state, before replacing itself with the normal Fprofile_FunctionTrace handler.
    #[pyfunction]
    #[pyo3(name = "_thread_trace_trampoline")]
    fn thread_trace_trampoline(_frame: PyObject, _event: PyObject, _arg: PyObject) -> Result<()> {
        // Register the current thread for tracing
        thread_register().wrap_err("Failed to register new FunctionTrace thread")?;

        // Replace our setprofile() handler with the real one.
        unsafe {
            // SAFETY: both parameters are of the proper type.
            pyo3::ffi::PyEval_SetProfile(Some(functiontrace), std::ptr::null_mut())
        };

        // We previously called into `Fprofile_FunctionTrace` here to manually record this call,
        // but that's both not very interesting as well as causes crashes on startup for some
        // Python versions (due to insufficiently initialized frames), so we don't do that anymore.
        Ok(())
    }

    /// Enable memory tracing for the current program.  This is implemented by attaching wrapper
    /// versions of malloc/free/etc to all of the current allocators.
    ///
    /// NOTE: Memory tracing may have up to 40% overhead on traces with many small allocations, so
    /// is not enabled by default.
    #[pyfunction]
    #[pyo3(name = "enable_tracememory")]
    fn allocations_record() -> Result<()> {
        // True iff we've enabled memory allocations.
        static ENABLE_MEM_TRACING: AtomicBool = AtomicBool::new(false);

        // Mark that memory tracing is enabled if it wasn't already.
        if ENABLE_MEM_TRACING.swap(true, Ordering::Relaxed) {
            // We've already enabled memory tracing, so there's nothing left to do.
            return Ok(());
        }

        // We'll immediately begin recording allocations, even if we haven't started yet, since
        // any logs before `STARTED = true` will be dropped.

        // Hook each of the possible allocators
        for domain in [
            pyo3::ffi::PyMemAllocatorDomain::PYMEM_DOMAIN_RAW,
            pyo3::ffi::PyMemAllocatorDomain::PYMEM_DOMAIN_MEM,
            pyo3::ffi::PyMemAllocatorDomain::PYMEM_DOMAIN_OBJ,
        ] {
            use crate::allocation_wrappers;

            // Fetch the original allocator and leak it, since we'll need to refer back to it.
            let original = Box::into_raw(Box::new(pyo3::ffi::PyMemAllocatorEx {
                ctx: std::ptr::null_mut(),
                malloc: None,
                calloc: None,
                realloc: None,
                free: None,
            }));

            unsafe {
                // SAFETY: `original` is a valid object with a 'static lifetime
                pyo3::ffi::PyMem_GetAllocator(domain, original)
            };

            // Wrap the original allocator in our wrappers which log and then call back into it.
            let mut wrapper = pyo3::ffi::PyMemAllocatorEx {
                ctx: original as *mut _,
                malloc: Some(allocation_wrappers::log_malloc),
                calloc: Some(allocation_wrappers::log_calloc),
                realloc: Some(allocation_wrappers::log_realloc),
                free: Some(allocation_wrappers::log_free),
            };

            unsafe {
                // SAFETY: `wrapper` is a valid object for the lifetime of this call
                pyo3::ffi::PyMem_SetAllocator(domain, &raw mut wrapper)
            };
        }

        Ok(())
    }

    /// The core logging function for FunctionTrace.  Configured by `PyEval_SetProfile`, and used
    /// to record all function calls/returns.
    extern "C" fn functiontrace(
        obj: *mut pyo3::ffi::PyObject,
        frame: *mut pyo3::ffi::PyFrameObject,
        what: i32,
        arg: *mut pyo3::ffi::PyObject,
    ) -> i32 {
        let Some(mut writer) = thread_state() else {
            // No reason to look at the event since we can't log it yet.
            return 0;
        };

        if !STARTED.load(Ordering::Relaxed) {
            // We aren't running (either starting up or shutting down), so shouldn't write
            // anything.
            return 0;
        }

        let time = trace_time();
        let c_functiontrace = *TRACEFUNC.get().expect("tracefunc is set in set_config");

        // Return the function name when we're in a C_* context.
        let c_func_name = || {
            let func = arg as *mut pyo3::ffi::PyCFunctionObject;

            unsafe {
                // SAFETY: In the `C_*` cases, `arg` is a non-NULL `*PyCFunctionObject`, which
                // always contains a valid method.
                let method = (*func).m_ml;
                (*method).ml_name
            }
        };
        // Given a C string sourced from Python, convert it to a Cow that can be serialized.
        let cstr_to_cow = |ptr: *const i8| {
            if !ptr.is_null() {
                unsafe {
                    // SAFETY: `ptr` is non-NULL and contains a valid C string.
                    // TODO: Can this change underneath us?
                    CStr::from_ptr(ptr)
                }
                .to_str()
                .unwrap_or("<invalid string>")
                .into()
            } else {
                Cow::Borrowed("<null>")
            }
        };

        match what {
            pyo3::ffi::PyTrace_CALL | pyo3::ffi::PyTrace_RETURN => {
                // For now we delegate these to the C implementation, since we can't access the
                // `PyCodeObject` fields that we require via Rust.
                unsafe {
                    // SAFETY: tracefunc is a valid function pointer to `Fprofile_FunctionTrace`.
                    return c_functiontrace(obj, frame, what, arg);
                }
            }
            pyo3::ffi::PyTrace_C_CALL => {
                let func = unsafe {
                    // SAFETY: In the `C_CALL` case, `arg` is guaranteed to be a non-NULL pointer
                    // to a `PyCFunctionObject`.
                    &*(arg as *mut pyo3::ffi::PyCFunctionObject)
                };

                let func_name = cstr_to_cow(c_func_name());

                // We either belong to a module or are a method on a class.
                if !func.m_module.is_null() {
                    // NOTE: _Typically_ `m_module` is a PyModule, but there are no requirements on
                    // what type it needs to be!  In practice, we only see PyModules and PyStrings.
                    Python::with_gil(|py| {
                        let m_module = unsafe {
                            // SAFETY: m_module is a non-NULL pointer to a valid Python object.
                            Bound::from_borrowed_ptr(py, func.m_module)
                        };

                        if let Ok(module) = m_module.downcast::<pyo3::types::PyModule>() {
                            // This is a PyModule, so get its name if possible.
                            let name = module.name();
                            let module_name = if let Ok(name) = &name {
                                name.to_cow().unwrap_or(Cow::Borrowed("<invalid string>"))
                            } else {
                                Cow::Borrowed("<unnamed module>")
                            };

                            function_trace::FunctionTrace::NativeCall {
                                module_name,
                                func_name,
                                time,
                            }
                            .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                        } else {
                            let module_name =
                                if let Ok(module) = m_module.downcast::<pyo3::types::PyString>() {
                                    module.to_cow().unwrap_or(Cow::Borrowed("<invalid string>"))
                                } else {
                                    // TODO: tracing log this
                                    Cow::Borrowed("<unknown module>")
                                };
                            function_trace::FunctionTrace::NativeCall {
                                module_name,
                                func_name,
                                time,
                            }
                            .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                        }
                    })
                } else {
                    // We don't belong to a module, so must be a class method.
                    let module_name = if !func.m_self.is_null() {
                        cstr_to_cow(unsafe {
                            // SAFETY: Since `m_self` is non-NULL, it must point to a valid
                            // PyObject, which is required to have a live and fully initialized
                            // `ob_type` member.
                            (*(*func.m_self).ob_type).tp_name
                        })
                    } else {
                        Cow::Borrowed("<unknown module>")
                    };

                    function_trace::FunctionTrace::NativeCall {
                        module_name,
                        func_name,
                        time,
                    }
                    .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                }
                .expect("Failed to emit NativeCall message");
            }
            pyo3::ffi::PyTrace_C_RETURN | pyo3::ffi::PyTrace_C_EXCEPTION => {
                if what == pyo3::ffi::PyTrace_C_EXCEPTION {
                    // C exceptions aren't exposed in a particularly interesting fashion, since they're
                    // done using the `PyErr_*` functions plus a NULL return value.
                    // However, if a `C_EXCEPTION` event is sent, we won't receive the corresponding
                    // `C_RETURN` event, so in practice we treat both of these events the same.
                    //
                    // TODO: Should we try exposing information about them?  We'd probably need to
                    // change the `Exception` format in `functiontrace-server`.
                }

                function_trace::FunctionTrace::NativeReturn {
                    func_name: cstr_to_cow(c_func_name()),
                    time,
                }
                .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                .expect("Failed to emit NativeReturn message");
            }
            pyo3::ffi::PyTrace_EXCEPTION => {
                // TODO: Actually handle exceptions and do something interesting.
                // We unfortunately can't get these from `PyEval_SetProfile`, so we'd need to use a
                // different method to capture them.
            }
            _ => {
                // TODO: this shouldn't be possible - tracing log it so we can handle later.
            }
        };

        0
    }
}

/// Allocation hooks and helpers for tracing Python memory allocator operations.
mod allocation_wrappers {
    use functiontrace_server::function_trace;
    use serde::Serialize;
    use std::ffi::c_void;

    /// Log the given allocation details.
    fn allocation_log<F: FnOnce() -> function_trace::AllocationDetails>(msg: F) {
        if let Some(mut writer) = crate::_functiontrace_rs::thread_state() {
            function_trace::FunctionTrace::Allocation {
                time: crate::_functiontrace_rs::trace_time(),
                details: msg(),
            }
            .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
            .expect("Failed to emit Allocation message");
        }
    }

    /// Given an allocator->ctx for a logging allocator, convert it to point to the original
    /// (wrapped) allocator.
    #[inline(always)]
    fn allocator_ctx(ctx: *mut c_void) -> pyo3::ffi::PyMemAllocatorEx {
        unsafe {
            // SAFETY: ctx is non-NULL and points to a `PyMemAllocatorEx` (checked in
            // `allocations_record`).
            *(ctx as *mut pyo3::ffi::PyMemAllocatorEx)
        }
    }

    #[unsafe(no_mangle)]
    pub extern "C" fn log_malloc(ctx: *mut c_void, bytes: usize) -> *mut c_void {
        let wrapped_allocator = allocator_ctx(ctx);
        let addr = wrapped_allocator
            .malloc
            .map(|malloc| malloc(wrapped_allocator.ctx, bytes))
            .unwrap_or(std::ptr::null_mut());

        allocation_log(|| function_trace::AllocationDetails::Alloc {
            bytes,
            addr: addr as usize,
        });

        addr
    }

    #[unsafe(no_mangle)]
    pub extern "C" fn log_calloc(ctx: *mut c_void, nelems: usize, elsize: usize) -> *mut c_void {
        let wrapped_allocator = allocator_ctx(ctx);
        let addr = wrapped_allocator
            .calloc
            .map(|calloc| calloc(wrapped_allocator.ctx, nelems, elsize))
            .unwrap_or(std::ptr::null_mut());

        allocation_log(|| function_trace::AllocationDetails::Alloc {
            bytes: nelems * elsize,
            addr: addr as usize,
        });

        addr
    }

    #[unsafe(no_mangle)]
    pub extern "C" fn log_realloc(
        ctx: *mut c_void,
        old_addr: *mut c_void,
        new_size: usize,
    ) -> *mut c_void {
        let wrapped_allocator = allocator_ctx(ctx);
        let addr = wrapped_allocator
            .realloc
            .map(|realloc| realloc(wrapped_allocator.ctx, old_addr, new_size))
            .unwrap_or(std::ptr::null_mut());

        allocation_log(|| function_trace::AllocationDetails::Realloc {
            bytes: new_size,
            old_addr: old_addr as usize,
            new_addr: addr as usize,
        });

        addr
    }

    #[unsafe(no_mangle)]
    pub extern "C" fn log_free(ctx: *mut c_void, old_addr: *mut c_void) {
        if old_addr.is_null() {
            // Abort quickly, since `free(NULL)` is surprisingly common and is defined to be a
            // NOOP.
            return;
        }

        let wrapped_allocator = allocator_ctx(ctx);
        if let Some(free) = wrapped_allocator.free {
            free(wrapped_allocator.ctx, old_addr)
        }

        allocation_log(|| function_trace::AllocationDetails::Free {
            old_addr: old_addr as usize,
        });
    }
}

/// Allocation hooks and helpers for tracing Python memory allocator operations.
mod hooks {
    use crate::_functiontrace_rs::trace_time;
    use color_eyre::eyre::{Result, WrapErr};
    use functiontrace_server::function_trace;
    use pyo3::ffi::PyObject;
    use pyo3::prelude::*; // TODO: What's in here?
    use serde::Serialize;
    use std::borrow::Cow;
    use std::sync::OnceLock;

    /// Install all the hooks by generating function capable of overriding an existing Python
    /// function, then attaching enough information about the original function to call it.
    pub fn install() -> Result<()> {
        for hook in HOOKS.iter() {
            Python::with_gil(|py| -> Result<()> {
                let (module_name, method_name) = hook
                    .target
                    .rsplit_once(".")
                    .expect("Each hook is a <module>.<method>");

                // Fetch the target module.method
                let module = py.import(module_name).wrap_err("Failed to import module")?;
                let orig = module
                    .getattr(method_name)
                    .wrap_err("Failed to retrieve module")?
                    .unbind();

                // Save the original method, since we'll need to call it from our wrapper function.
                hook.original
                    .set(orig)
                    .expect("We're the only function that sets the hooks");

                // Create a new Python function and overwrite the old one with it
                let func = pyo3::types::PyCFunction::new_with_keywords(
                    py,
                    hook.wrapper,
                    Box::leak(
                        // The function name must live for as long as it's reachable by Python
                        // (forever).
                        std::ffi::CString::new(method_name)
                            .wrap_err("Failed to convert module name to C-string")?
                            .into_boxed_c_str(),
                    ),
                    c"FunctionTrace internal wrapper for print",
                    Some(&module),
                )
                .wrap_err("Failed to generate PyCFunction")?;
                module
                    .add(method_name, func)
                    .wrap_err("Failed to override method")
            })
            .wrap_err_with(|| format!("Failed to hook {}", hook.target))?;
        }

        Ok(())
    }

    ////////////////////////////////////////////////////////////////////////////
    // Hooking Framework
    ////////////////////////////////////////////////////////////////////////////

    /// Implementation details behind [`hooks`].
    ///
    /// Keep a:
    /// - counter that is incremented for each hook tuple we're passed, allowing us to know the
    ///   index of that hook
    /// - accumulator that gathers the counted hooks, allowing us to emit a single expression at
    ///   the end (an array consisting of all hooks with their index associated)
    ///
    /// NOTE: I suspect this is grosser than it needs to be, but it works and really isn't fun to
    /// modify.
    macro_rules! hook_counter {
        // The accumulator has fully collected all of our hooks, so we can now emit a vec of them.
        ( [$( ($target:literal, $wrapper:ident, $counter:expr) ),*  $(,)?], $_counter:expr) => {
            [$( Hook {
                target: $target,
                wrapper: $wrapper::<{ $counter }>,
                original: OnceLock::new(),
            }),*]
        };
        // Handle the first iteration specifically
        ( [ ], $counter:expr, $target:literal, $wrapper:ident, $($rest:tt),*) => {
            hook_counter!( [
                ($target, $wrapper, $counter)
            ], $counter +1, $($rest),*)
        };
        // Handle the last iteration specifically, since we'll switch out of the normal recursive
        // case and into our accumulator case.
        ( [$($acc:tt),*  $(,)?], $counter:expr, $target:literal, $wrapper:ident) => {
            hook_counter!( [
                $($acc),*, ($target, $wrapper, $counter)
            ], $counter +1)
        };
        // The main recursive case
        ( [ $( $acc:tt ),* $(,)?], $counter:expr, $target:literal, $wrapper:ident, $($rest:tt),*) => {
            hook_counter!( [
                $($acc),*, ($target, $wrapper, $counter)
            ], $counter +1, $($rest),*)
        };
    }

    /// Generate an array of [`Hook`]s.  In particular, we need to generate unique references into
    /// [`HOOKS`] that each wrapper is aware of, meaning we need to use a custom push-down
    /// accumulator and counting macro.
    macro_rules! hooks {
        ($(($target:literal, $wrapper:ident)),* $(,)?) => {
            hook_counter!([], 0, $($target, $wrapper),*)
        };
    }

    /// The set of functions we'll be hooking.
    ///
    /// NOTE: This must be created by [`hooks`], since we actually generate new variants of the
    /// wrapper function for each hook, allowing the function to determine which hook triggered it
    /// at runtime.
    static HOOKS: [Hook; 11] = hooks!(
        ("builtins.print", logging_print),
        ("logging.debug", logging_print),
        ("logging.log", logging_print),
        ("logging.info", logging_print),
        ("logging.warning", logging_print),
        ("logging.error", logging_print),
        ("logging.critical", logging_print),
        ("logging.fatal", logging_print),
        ("logging.exception", logging_print),
        ("multiprocessing.util._exit_function", multiprocessing_exit),
        ("builtins.__import__", logging_import),
    );

    /// Information, used during both runtime and at [`install`] time, about a specific function
    /// that's being hooked.
    struct Hook {
        /// The hooking target, in a `<module>.<method>` format.
        target: &'static str,
        /// The Rust wrapper function, which proxies its arguments to `original` and returns its
        /// result.
        wrapper: extern "C" fn(*mut PyObject, *mut PyObject, *mut PyObject) -> *mut PyObject,
        /// The original Python function that's being wrapped.
        original: OnceLock<Py<PyAny>>,
    }

    /// A generic wrapper that parses out the arguments, calls the given handler function to handle
    /// custom hooking logic, then proxies the arguments out to the original wrapped function.
    fn proxy(
        hook: &Hook,
        handler: impl FnOnce(
            &Bound<'_, pyo3::types::PyTuple>,
        ) -> Option<function_trace::FunctionTrace<'static>>,
        args: *mut PyObject,
        kwargs: *mut PyObject,
    ) -> *mut PyObject {
        let orig = hook
            .original
            .get()
            .expect("Wrapper functions can't be called until hooked");

        Python::with_gil(|py| -> Result<()> {
            if let Some(mut writer) = crate::_functiontrace_rs::thread_state() {
                let args = unsafe {
                    // SAFETY: `args` represents a valid argument tuple
                    Bound::from_borrowed_ptr(py, args)
                };
                let args = args
                    .downcast()
                    .map_err(Into::<PyErr>::into)
                    .wrap_err("Python args must be a tuple")?;

                if let Some(msg) = handler(args) {
                    msg.serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                        .wrap_err("Failed to emit Allocation message")?;
                }
            }

            Ok(())
        })
        .wrap_err_with(|| format!("FunctionTrace proxy logging for {} failed", hook.target))
        // TODO: This shouldn't be catastrophic - we can log it and continue on
        // instead once we introduce `tracing`.
        .expect("Proxying should never fail");

        unsafe {
            // SAFETY: This is a direct translation of the original call we're proxying
            pyo3::ffi::PyObject_Call(orig.as_ptr(), args, kwargs)
        }
    }

    ////////////////////////////////////////////////////////////////////////////
    // Hook Implementations
    ////////////////////////////////////////////////////////////////////////////
    // NOTE: Each hook needs to be able to determine which index of `HOOKS` it corresponds to, so
    // must take a `<const HOOK: usize>` as the only generic argument.

    /// Given a log-like function, emit a [`FunctionTrace::Log`] event for it.
    extern "C" fn logging_print<const HOOK: usize>(
        _self: *mut PyObject,
        args: *mut PyObject,
        kwargs: *mut PyObject,
    ) -> *mut PyObject {
        let hook = &HOOKS[HOOK];

        proxy(
            hook,
            |args| {
                // Logging functions should roughly call `str()` on their arguments
                // TODO: We shouldn't need to explicitly allocate for this.
                let args = args
                    .str()
                    .and_then(|x| x.to_str().map(|x| Cow::Owned(x.to_string())))
                    .unwrap_or(Cow::Borrowed("<invalid string>"));

                Some(function_trace::FunctionTrace::Log {
                    time: trace_time(),
                    log_type: Cow::Borrowed(hook.target),
                    log_value: args,
                })
            },
            args,
            kwargs,
        )
    }

    /// Emit a [`FunctionTrace::Import`] event for `import` calls
    extern "C" fn logging_import<const HOOK: usize>(
        _self: *mut PyObject,
        args: *mut PyObject,
        kwargs: *mut PyObject,
    ) -> *mut PyObject {
        let hook = &HOOKS[HOOK];

        proxy(
            hook,
            |args| {
                // `import` takes rather complicated arguments, but in practice we only care about
                // the first argument (name)
                let module = if let Ok(arg) = args.get_item(0) {
                    arg.downcast()
                        .map_err(Into::into)
                        .and_then(|module| module.to_str())
                        .map(|module| Cow::Owned(module.to_string()))
                        .unwrap_or(Cow::Borrowed("<unknown module>"))
                } else {
                    Cow::Borrowed("<no module specified>")
                };

                Some(function_trace::FunctionTrace::Import {
                    time: trace_time(),
                    module_name: module,
                })
            },
            args,
            kwargs,
        )
    }

    /// Though this is mixed in with the rest of the hooks, this is actually load-bearing for
    /// general FunctionTrace functionality.
    ///
    /// `atexit()` will only run in the main process, so we need to register a separate
    /// multiprocessesing exit hook to do similar teardown on any multiprocessing workers.
    extern "C" fn multiprocessing_exit<const HOOK: usize>(
        _self: *mut PyObject,
        args: *mut PyObject,
        kwargs: *mut PyObject,
    ) -> *mut PyObject {
        let hook = &HOOKS[HOOK];

        if let Some(writer) = crate::_functiontrace_rs::thread_state() {
            crate::_functiontrace_rs::thread_teardown(writer)
                .expect("Multiprocessing teardown should be successful");
        }

        // Directly pass the command on, since we don't need to log/etc for this.
        proxy(hook, |_args| None, args, kwargs)
    }
}
