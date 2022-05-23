# fish-jit

A just-in-time compiling interpreter for the [><>](https://esolangs.org/wiki/Fish) programming language, to be built with the RPython Toolchain.

Download the latest [pypy source](https://www.pypy.org/download.html#source), and build as follows:

`python2 /path/to/pypy3.9-v7.3.9-src/rpython/bin/rpython --opt=jit fish-jit.py`

Build dependencies are listed separately: https://doc.pypy.org/en/latest/build.html#install-build-time-dependencies

The resulting executable will be named fish-jit-c or similar in the current working directory. Note that the version of python/pypy used for the build must be 2.7.
It can also be built without JIT support by removing the `--opt=jit` option. Build time will be shorter, and the resulting executable smaller.

The interpreter differs from the reference implementation on the following points:

 - Division

   This result is stored internally as an arbitrary precision rational. When displayed, if the value is integer it will be displayed as such, otherwise as a float. This allows for arbitrary precision arithmetic without removing floating point division.

 - Stack Operations

   - `{` and `}`

     With zero items on the stack these will have no effect, rather than crashing.
