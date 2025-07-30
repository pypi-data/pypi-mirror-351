# calculating pi with modern tooling

[![image](https://img.shields.io/pypi/v/picarlo)](https://pypi.org/project/picarlo/)
[![image](https://img.shields.io/pypi/l/picarlo)](https://pypi.org/project/picarlo/)
[![image](https://img.shields.io/pypi/pyversions/picarlo)](https://pypi.org/project/picarlo/)

We need a few things:
1. a CLI tool to specify the number of iterations and the number of cores it runs on:
`picarlo --cores 4 --iterations 10000`
2. a library that can be imported in a notebook


## basic tooling setup (runs on each commit)
1. [x] `uv self update` & `uv sync`
2. [x] linting/format checking: `uv run ruff check`
3. [x] auto-formatting: `uv run ruff format`
4. [x] type checking: `uv run pyright`
<!-- TODO: compare pyright and mypy analysis -->
5. [x] testing: `uv run pytest`, run them in parallel
6. [x] integrate into pre-commit `pre-commit run --all-files`

## Checks
1. check that the package can be installed: `uv run --with picarlo --no-project -- python -c "import picarlo"`

## Goal
1. [ ] run from command-line (uvx)
2. [ ] import lib into notebook (either via pypy or from local dist)
3. [ ] published module

## required
1. [x] split between dev and prod dependencies: `uv add --dev`
2. [x] add a build system, hatchling in [pyproject.toml](pyproject.toml)
3. [x] run a build `uv build`
4. try maturing build backend

## useful stuff
1. create docstrings via LLM
2. create docs from docstrings
3. calculate test coverage
4. tracing
5. [server-sent event via starlette](https://github.com/sysid/sse-starlette)

## more ambitious stuff
* parallelism, e.g. [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) (see prime number example)


## release preparation
1. generate changelog from commit messages
2. update version indicator
3. build package/wheel
4. publish assets

# [vscode extensions](.vscode/extensions.json)
1. Ruff
2. TOML syntax highlighting
