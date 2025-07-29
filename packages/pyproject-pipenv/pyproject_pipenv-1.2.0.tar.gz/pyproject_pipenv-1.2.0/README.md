# pyproject-pipenv

[![ci](https://github.com/fopina/pyproject-pipenv/actions/workflows/publish-main.yml/badge.svg)](https://github.com/fopina/pyproject-pipenv/actions/workflows/publish-main.yml)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pyproject-pipenv.svg)](https://pypi.python.org/pypi/pyproject-pipenv/)
[![PyPI version](https://badge.fury.io/py/pyproject-pipenv.svg)](https://badge.fury.io/py/pyproject-pipenv)
[![Very popular](https://img.shields.io/pypi/dm/pyproject-pipenv)](https://pypistats.org/packages/pyproject-pipenv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Sync properties from Pipfile to pyproject.toml.

Never need again to change dependencies manually in pyproject.toml (or forget to do it and publish a broken package), and enjoy the same dependency locking or semantic versioning.

Also allows just checking to be used as part of CI lint/format steps.

## Install

```
# in your project virtualenv (or globally / pipx)
$ pip install pyproject-pipenv
...
```

## Usage

Check:

```
$ pyproject-pipenv
Dependencies out of sync:
- tomlkit<2.0.0
+ tomlkit<1.0.0
pyproject.toml NEEDS UPDATE!
```

Apply:

```
$ pyproject-pipenv --fix
Dependencies out of sync:
- tomlkit<2.0.0
+ tomlkit<1.0.0
pyproject.toml UPDATED!
```

## Features

* Syncs
  * Dependencies
  * Python version required


## ToDo

* ~~Handle markers and all that extra crap besides version~~
* Sync more fields

## Context

For some reason, neither pyproject nor pipenv interact with each other:
* You use `pipenv` (and `Pipfile`) while developing, because it's great
* You add all the package details to `pyproject.toml`
* You work on the code and add new dependencies
* Then you publish the new version only to notice you forgot to add the dependencies *also* to pyproject `dependencies` entry...

[dephell](https://github.com/dephell/dephell) seemed to be a solution but it is dead. Forking it sounds too much, as it supports many different things than I need.

[pipenv-setup](https://github.com/Madoshakalaka/pipenv-setup/) seems to be the same but for `setup.py` instead of `pyproject.toml`. Probably a good source for inspiration after this initial version.