# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Changed

- The output format of `pyodide auditwheel show` has been simplified to be more `ldd`-like. It also shows the location of the dependencies in the wheel
  using the runtime path of the shared libraries.

- `pyodide auditwheel show` now accepts `-r`, `--with-runtime-paths` option to show the runtime paths of the shared libraries in the wheel.

- `auditwheel.show()` function now returns the runtime paths of the shared libraries in the wheel as well.

## [0.1.0] - 2025-04-04

### Changed

- `auditwheel repair` command now updates the DYLINK RPATH section of the wasm module.
  ([#41](https://github.com/pyodide/auditwheel-emscripten/pull/41))

## [0.0.16] - 2024-07-05

### Fixed

- Fixed incorrect extra dependency for typer
  ([#32](https://github.com/pyodide/auditwheel-emscripten/pull/32))

## [0.0.15] - 2024-06-17

### Fixed

- Support Pyodide>=0.26.0 wheels that has "pyodide" platform tag.
  ([#31](https://github.com/pyodide/auditwheel-emscripten/pull/31))

## [0.0.14] - 2023-12-23

### Changed

- Changed the behavior of the `repair` command. It does not update `needed` section anymore
  and only copies the shared libraries to the wheel.
  Also, `copy` command is deprecated in favor of `repair`.
  ([#25](https://github.com/pyodide/auditwheel-emscripten/pull/25))

## [0.0.13] - 2023.06.08

- Added py.typed file.
  ([#16](https://github.com/pyodide/auditwheel-emscripten/pull/16))

## [0.0.12] - 2023.02.13

### Fixed

- Added license file to the distribution.
  ([#10](https://github.com/pyodide/auditwheel-emscripten/pull/10))

## [0.0.11] - 2023.02.06

### Added

- Added `--show-type` option to `exports` and `imports` command, which will
  show the type of the functions in the output.
  ([#9](https://github.com/pyodide/auditwheel-emscripten/pull/9))

## [0.0.10] - 2023.01.26

### Changed

- Removed extra message from CLI commands.
  ([#8](https://github.com/pyodide/auditwheel-emscripten/pull/8))
- Changed the output format of `exports` and `imports` CLI command in order to
  make it easier to parse with `grep`.
  ([#8](https://github.com/pyodide/auditwheel-emscripten/pull/8))

## [0.0.9] - 2022.12.20

### Fixed

- `pyodide auditwheel show` now will work on modules with .wasm suffix
([#7](https://github.com/pyodide/auditwheel-emscripten/pull/7))

### Changed

 - Changed the CLI entry point name from `pyodide audit` to `pyodide auditwheel`
 ([#5](https://github.com/pyodide/auditwheel-emscripten/pull/5))
