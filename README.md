# Balparda's Base Library

Balparda's base library of util methods and classes.

Started in January/2023, by Daniel Balparda.

## License

Copyright 2025 Daniel Balparda (balparda@gmail.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Setup

```bash
brew install git uv python@3.13

git clone https://github.com/balparda/baselib.git baselib
cd baselib

uv venv --python 3.13
source .venv/bin/activate
uv pip install --upgrade pip
uv pip install -r requirements.txt

pytest

deactivate
```

Docs for crypto: https://cryptography.io/en/latest/

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
