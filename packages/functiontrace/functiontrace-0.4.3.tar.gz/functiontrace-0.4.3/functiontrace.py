import argparse
import os
import shutil
import sys
import tempfile
from importlib import machinery, util

import _functiontrace  # noqa: F401 - this import is load bearing since we need to run code on import
import _functiontrace_rs as rust

PYTHON_TEMPLATE = """#!/bin/sh

# The location of this wrapper, which must be in the path.
FUNCTIONTRACE_WRAPPER_PATH=$(dirname $(which {python}))

# Remove the wrapper directory from PATH, allowing us to find the real Python.
PATH=$(echo "$PATH" | sed -e "s#$FUNCTIONTRACE_WRAPPER_PATH:##")

exec $(which {python}) -m functiontrace "$@"
"""


def setup_dependencies():
    # We need the functiontrace-server installed and locatable in order to
    # trace anything.
    if shutil.which("functiontrace-server") is None:
        print(
            "Unable to find `functiontrace-server` in the current $PATH.",
            file=sys.stderr,
        )
        print(
            "See https://functiontrace.com#installation for installation instructions.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate a temp directory to store our wrappers in.  We'll temporarily
    # add this directory to our path.
    tempdir = tempfile.mkdtemp(prefix="py-functiontrace")
    os.environ["PATH"] = tempdir + os.pathsep + os.environ["PATH"]

    # Generate wrappers for the various Python versions we support to ensure
    # they're included in our PATH.
    wrap_pythons = ["python", "python3"] + [
        "python3.{}".format(minor) for minor in range(6, 13)
    ]
    for python in wrap_pythons:
        with open(os.path.join(tempdir, python), "w") as f:
            f.write(PYTHON_TEMPLATE.format(python=python))
            os.chmod(f.name, 0o755)


def main():
    parser = argparse.ArgumentParser(description="Trace a script's execution.")
    parser.add_argument(
        "--trace-memory",
        "--trace_memory",
        action="store_true",
        help="Trace memory allocations/frees when enabled.  This may add tracing overhead, so is disabled by default.",
    )
    parser.add_argument(
        "--output-dir",
        "--output_dir",
        type=str,
        default=os.getcwd(),
        help="The directory to output trace files to",
    )
    parser.add_argument(
        "--no-compression",
        "--no_compression",
        action="store_true",
        help="Disable compression of traces, which can be unnecessarily slow if filesize is not a concern.",
    )
    parser.add_argument("-v", "--version", action="version", version=rust.__version__)
    parser.add_argument("script", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if len(args.script) == 0:
        print("Can't profile without a target")
        parser.print_help()
        sys.exit(1)

    # Ignore ourselves, keeping sys.argv looking reasonable as the child script
    # will expect it to be sane.
    sys.argv[:] = args.script

    # Read in the script to be executed and compile their code, then ensure it
    # appears to be a normal module.
    #
    # NOTE: This is pretty sketchy and requires some care to make work properly
    # in all cases.  In particular, use of `__file__` and
    # `multiprocessing.Pool` are good sanity checks if this is modified.
    target_file = sys.argv[0]
    sys.path.insert(0, os.path.dirname(target_file))
    with open(target_file, "rb") as fp:
        code = compile(fp.read(), target_file, "exec")

    # Load the file as __main__ and insert it into the set of modules.  This
    # won't do anything useful on its own, but is necessary for the exec() call
    # below, which needs to operate in the context of our new module.
    # NOTE: We use SourceFileLoader, rather than allowing importlib to infer
    # the proper loader, in order to support files without a .py extension.
    spec = util.spec_from_loader(
        "__main__", machinery.SourceFileLoader("__main__", target_file)
    )
    mod = util.module_from_spec(spec)
    sys.modules.update({"__main__": mod})

    # Ensure we're setup to be able to run.
    setup_dependencies()

    # Setup our tracing environment, including configuring tracing features.
    if args.no_compression:
        os.environ["FUNCTIONTRACE_COMPRESSION"] = "false"
    if args.trace_memory:
        rust.enable_tracememory()
    rust.begin_tracing(args.output_dir)

    # Run their code now that we're tracing.  This must be done in the context
    # of the __main__ module we've created.
    exec(code, mod.__dict__)


def trace():
    # Make sure we're set up to work properly, then begin tracing.
    setup_dependencies()
    rust.begin_tracing(os.getcwd())


if __name__ == "__main__":
    main()
