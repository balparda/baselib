# Balparda's Base Library

Balparda's base library of util methods and classes.

Started in 2023/January, by Daniel Balparda de Carvalho.

# License

Copyright (C) 2023 Daniel Balparda de Carvalho (balparda@gmail.com).
This file is part of Irish Rail Timetable.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see http://www.gnu.org/licenses/gpl-3.0.txt.

# Setup

Just the basics.

```
$ hg clone https://balparda@bitbucket.org/balparda/baselib
$ sudo apt-get install python3-pip pylint3
```

# Usage

Import into your project and use the utilities. Just by importing
you will set logging at `info` level to `stderr`. Some usage examples:

```
from baselib import base

@base.Timed('Total main() method execution time')
def main():
  # will automatically time execution of this decorated method,
  # and upon exit will log to info, using the message given

  print(base.HumanizedLength(58))           # will print '58b'
  print(base.HumanizedLength(3589))         # will print '3.50kb'
  print(base.HumanizedLength(358573489))    # will print '341.96Mb'
  print(base.HumanizedLength(35857345689))  # will print '33.39Gb'

  BinSerialize({'a': 1, 'b': 2}, '~/myfile.db')   # will save the dict to file, compressed
  data = BinDeSerialize(file_path='~/myfile.db')  # will load the dict from file
  # ATTENTION: serialization is dangerous, and should be used with care!
```
