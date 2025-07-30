#include <Python.h>
#include <frameobject.h>
#include <sys/types.h>
#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>

#include "mpack/mpack.h"

////////////////////////////////////////////////////////////////////////////////
// Prototypes
////////////////////////////////////////////////////////////////////////////////
static int     Fprofile_FunctionTrace(PyObject* obj, PyFrameObject* frame, int what, PyObject* arg);

////////////////////////////////////////////////////////////////////////////////
// Globals
////////////////////////////////////////////////////////////////////////////////
// This key is used to fetch the thread local instance of the `Writer`
// structure.
static pthread_key_t Tss_Key = 0;

// The exposed apis of the Rust extension.
static struct {
    pthread_key_t (*set_config)(int (*functiontrace)(PyObject*, PyFrameObject*, int, PyObject*));
}* rust;

////////////////////////////////////////////////////////////////////////////////
// Misc
////////////////////////////////////////////////////////////////////////////////

// Given a PyObject (likely `co_name` or similar), return a UTF-8
// representation.
static inline const char* Fprofile_UnicodeToUtf8(PyObject* obj) {
    if (obj == NULL) {
        return "<NULL>";
    }

    if (PyUnicode_Check(obj)) {
        const char* utf8 = PyUnicode_AsUTF8(obj);

        return utf8 != NULL ? utf8 : "<DECODE ERROR>";
    } else if (obj == Py_None) {
        return "<NONE>";
    } else {
        return "<UNKNOWN>";
    }
}

////////////////////////////////////////////////////////////////////////////////
// Callbacks
////////////////////////////////////////////////////////////////////////////////
static int Fprofile_FunctionTrace(PyObject* obj, PyFrameObject* frame, int what, PyObject* arg) {
    struct timespec    tsc = { 0 };

    // This is called from the Rust code, which has already checked that
    // everything is configured to send messages.
    mpack_writer_t* writer = pthread_getspecific(Tss_Key);

    clock_gettime(CLOCK_MONOTONIC, &tsc);

    switch (what) {
        case PyTrace_CALL:
            mpack_start_array(writer, 5);
            mpack_write_cstr(writer, "Call");

            mpack_start_array(writer, 2);
            mpack_write_u32(writer, tsc.tv_sec);
            mpack_write_u32(writer, tsc.tv_nsec);
            mpack_finish_array(writer);

            {
                PyCodeObject* code = PyFrame_GetCode(frame);
                int lineno = PyFrame_GetLineNumber(frame);

#if PY_VERSION_HEX >= 0x030b00a0
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_qualname));
#else
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_name));
#endif
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_filename));
                mpack_write_u32(writer, lineno);

                Py_DECREF(code);
            }
            mpack_finish_array(writer);
            break;
        case PyTrace_RETURN:
            mpack_start_array(writer, 3);
            mpack_write_cstr(writer, "Return");

            mpack_start_array(writer, 2);
            mpack_write_u32(writer, tsc.tv_sec);
            mpack_write_u32(writer, tsc.tv_nsec);
            mpack_finish_array(writer);

            {
                PyCodeObject* code = PyFrame_GetCode(frame);

#if PY_VERSION_HEX >= 0x030b00a0
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_qualname));
#else
                mpack_write_cstr(writer, Fprofile_UnicodeToUtf8(code->co_name));
#endif

                Py_DECREF(code);
            }
            mpack_finish_array(writer);
            break;
        default:
            perror("Impossible C case");
            break;
    }

    return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Module Initialization
////////////////////////////////////////////////////////////////////////////////

// The set of methods exposed by this module to Python.
static PyMethodDef methods[] = {
    [0] = {NULL, NULL, 0, NULL}
};

static PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_functiontrace",
    "",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__functiontrace(void) {
    // Setup our janky Rust dlopen alternative so we can use Rust code.
    PyObject* rust_mod = PyImport_ImportModule("_functiontrace_rs");

    // Verify that the rust extension loads if we're using it.
    if (rust_mod == NULL) {
        perror("Failed to load internal Rust extension");
        exit(-1);
    }

    // This returns a pointer to the C API exposed by the Rust module.
    PyObject* py_c_api = PyObject_GetAttrString(rust_mod, "c_api");
    if (py_c_api == NULL) {
        perror("Failed to initialize FunctionTrace Rust<->C interface");
        exit(-1);
    }
    PyObject* c_api = PyObject_CallFunctionObjArgs(py_c_api, NULL);

    // Save the Rust vtable so everyone can access it
    rust = PyLong_AsVoidPtr(c_api);

    // Share our globals with Rust
    Tss_Key = rust->set_config(Fprofile_FunctionTrace);

    return PyModule_Create(&module);
}
