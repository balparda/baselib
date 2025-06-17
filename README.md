# Balparda's Base Library

Balparda's base library of util methods and classes.

Started in January/2023, by Daniel Balparda.

## License

Copyright 2025 Daniel Balparda ([balparda@github.com](mailto:balparda@github.com))

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a [copy of the License here](http://www.apache.org/licenses/LICENSE-2.0).

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Setup

If you want to develop for this project, first install
[Poetry](https://python-poetry.org/docs/cli/), but make
sure it is like this:

```sh
brew uninstall poetry
python3.13 -m pip install --user pipx
python3.13 -m pipx ensurepath
# re-open terminal
poetry self add poetry-plugin-export@^1.8  # allows export to requirements.txt (see below)
poetry config virtualenvs.in-project true  # creates venv inside project directory
```

Now install the project:

```sh
brew install python@3.13 git
# or on Ubuntu/Debian: sudo apt-get install python3.13 python3.13-venv git

git clone https://github.com/balparda/baselib.git baselib
cd baselib

poetry env use python3.13  # creates the venv
poetry install --sync      # HONOR the project's poetry.lock file, uninstalls stray pkgs
poetry env info            # no-op: just to check

poetry run pytest
# or any command as:
poetry run <any-command>
```

To activate like a regular environment do:

```sh
poetry env activate
# will print activation command which you next execute, or you can do:
source .env/bin/activate                         # if .env is local to the project
source "$(poetry env info --path)/bin/activate"  # for other paths

pytest

deactivate
```

To update `poetry.lock` file to more current versions:

```sh
poetry update  # ignores current lock, updates, rewrites `poetry.lock` file
poetry run pytest
```

To add a new dependency you should:

```sh
poetry add "pkg>=1.2.3"  # regenerates lock, updates env
# also: "pkg@^1.2.3" = latest 1.* ; "pkg@~1.2.3" = latest 1.2.* ; "pkg@1.2.3" exact
poetry export --format requirements.txt --without-hashes --output requirements.txt
```

If you added a dependency to `pyproject.toml`:

```sh
poetry lock     # re-lock your dependencies, so `poetry.lock` is regenerated
poetry install  # sync your virtualenv to match the new lock file
poetry export --format requirements.txt --without-hashes --output requirements.txt
```

To update a version do:

```sh
# bump the version!
poetry version minor  # updates 1.6 to 1.7, for example
# or:
poetry version patch  # updates 1.6 to 1.6.1
# or:
poetry version <version-number>
# (also updates `pyproject.toml` and `poetry.lock`)

# publish to GIT, including a TAG
git commit -a -m "release version 1.7"
git tag 1.7
git push
git push --tags

# prepare package for PyPI
poetry build
poetry publish
```

To remove an environment from your machine:

```sh
poetry env list
# see name of environment
poetry env remove <name-of-environment>
```

## Usage

Import into your project and use the utilities. Just by importing
you will set logging at `info` level to `stderr`. Some usage examples:

```python
import getpass
from baselib import base

@base.Timed('Total main() method execution time')
def main():
  # will automatically time execution of this decorated method,
  # and upon exit will log to info, using the message given

  # decimal numbers humanized string conversion, from zero to Tera:
  print(base.HumanizedDecimal(11))              # will print '1'
  print(base.HumanizedDecimal(12100))           # will print '12.10k'
  print(base.HumanizedDecimal(13200000))        # will print '13.20M'
  print(base.HumanizedDecimal(15400000000000))  # will print '15.40T'

  # byte lengths humanized string conversion, from zero to Terabytes:
  print(base.HumanizedBytes(10))              # will print '10b'
  print(base.HumanizedBytes(10000))           # will print '9.77kb'
  print(base.HumanizedBytes(10000000))        # will print '9.54Mb'
  print(base.HumanizedBytes(10000000000000))  # will print '9.09Tb'

  # time lengths (in seconds) humanized string conversion, from milliseconds to days:
  print(base.HumanizedSeconds(0.00456789))  # will print '4.568 msecs'
  print(base.HumanizedSeconds(10))          # will print '10.00 secs'
  print(base.HumanizedSeconds(5000))        # will print '1.39 hours'
  print(base.HumanizedSeconds(100000))      # will print '1.16 days'

  # serialization (ATTENTION: serialization is dangerous, and should be used with care!):
  base.BinSerialize({'a': 1, 'b': 2}, '~/file1.db')   # will save the dict to `file1`, compressed
  data = base.BinDeSerialize(file_path='~/file1.db')  # will load the dict from `file1`

  # more serialization (ATTENTION: cryptography is dangerous, and should be used with care!):
  str_password = getpass.getpass(prompt='Password: ')
  key = base.DeriveKeyFromStaticPassword(str_password)
  base.BinSerialize([1, 2], '~/file2.db', compress=False, key=key)             # save list to `file2`, encrypted
  data = base.BinDeSerialize(file_path='~/file2.db', compress=False, key=key)  # load list from `file2`
```
