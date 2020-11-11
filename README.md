# fish-jit

A just-in-time compiling interpreter for the [><>](https://esolangs.org/wiki/Fish) programming language, to be built with the RPython Toolchain.

Download the latest [pypy source](https://www.pypy.org/download.html#source), and build as follows:

`python /path/to/pypy3.7-v7.3.2-src/rpython/bin/rpython --opt=jit bf-jit.py`

The resulting executable will be named fish-jit-c or similar in the current working directory. Note that the version of python/pypy used for the build must be 2.7.
It can also be built without JIT support by removing the `--opt=jit` option. Build time will be shorter, and the resulting executable smaller.
