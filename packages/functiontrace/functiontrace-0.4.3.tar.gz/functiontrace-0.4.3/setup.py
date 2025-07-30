from setuptools import setup, Extension


if __name__ == "__main__":
    setup(
        py_modules=["functiontrace"],
        ext_modules=[
            Extension(
                "_functiontrace",
                ["_functiontrace.c", "mpack/mpack.c"],
                extra_compile_args=["-std=c11", "-O2"],
            )
        ],
    )
