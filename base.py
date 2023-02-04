#!/usr/bin/python3 -O
#
# Copyright 2023 Daniel Balparda (balparda@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License 3 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/gpl-3.0.txt.
#
"""Balparda's base library of util methods and classes."""

import bz2
import functools
import logging
import os
import os.path
import pickle  # nosec - this is a dangerous module!
# import pdb
import time
import sys
from typing import Any, Callable, Literal, Optional


__author__ = 'balparda@gmail.com (Daniel Balparda)'
__version__ = (1, 0)


# log format string
LOG_FORMAT = '%(asctime)-15s: %(module)s/%(funcName)s/%(lineno)d: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)  # set this as default

# advanced log formats
_LOG_FORMATS = (
    '%(asctime)s.%(msecs)03d%(levelname)08s[%(funcName)s]: %(message)s',  # without process name
    '%(asctime)s.%(msecs)03d%(levelname)08s[%(processName)s.%(funcName)s]: %(message)s',  # with prc
    '%Y%m%d.%H:%M:%S',  # date format
)
# example '20220209.14:16:47.667    INFO[SomeMethodName]: Some message'

# user directory
USER_DIRECTORY = os.path.expanduser('~/')
PRIVATE_DIR = lambda p: '~/' + p[len(USER_DIRECTORY):] if p.startswith(USER_DIRECTORY) else p

# time utils
INT_TIME = lambda: int(time.time())
_TIME_FORMAT = '%Y/%b/%d-%H:%M:%S'
STD_TIME_STRING = lambda t: time.strftime(_TIME_FORMAT, time.gmtime(t))  # cspell:disable-line


class Error(Exception):
  """Base exception."""


def StartStdErrLogging(level: int = logging.INFO, log_process: bool = False) -> None:
  """Start logging to stderr.

  Should be called only once like  `if __name__ == '__main__': lib.StartStdErrLogging(); main()`.

  Args:
    level: (default logging.INFO) logging level to use
    log_process: (default False) If True will add process names to log strings (as in the process
        `multiprocessing.Process(name=[some_name])` call)
  """
  logger = logging.getLogger()
  logger.setLevel(level)
  handler = logging.StreamHandler(sys.stdout)
  handler.setLevel(level)
  formatter = logging.Formatter(
      fmt=_LOG_FORMATS[1] if log_process else _LOG_FORMATS[0],
      datefmt=_LOG_FORMATS[2])
  handler.setFormatter(formatter)
  logger.addHandler(handler)


def HumanizedBytes(inp_sz: int) -> str:
  """Return human-readable byte sizes.

  Args:
    inp: A bytes length

  Returns:
    human-readable length for inp_sz
  """
  if inp_sz < 0:
    raise AttributeError('Input should be >=0 and got %d' % inp_sz)
  if inp_sz < 1024:
    return '%db' % inp_sz
  if inp_sz < 1024 * 1024:
    return '%0.2fkb' % (inp_sz / 1024.0)
  if inp_sz < 1024 * 1024 * 1024:
    return '%0.2fMb' % (inp_sz / (1024.0 * 1024.0))
  if inp_sz < 1024 * 1024 * 1024 * 1024:
    return '%0.2fGb' % (inp_sz / (1024.0 * 1024.0 * 1024.0))
  return '%0.2fTb' % (inp_sz / (1024.0 * 1024.0 * 1024.0 * 1024.0))


def HumanizedDecimal(inp_sz: int) -> str:
  """Return human-readable decimal-measured sizes.

  Args:
    inp: A length from a measure to be converted by multiples of 1000, like Megapixel.

  Returns:
    human-readable length of decimal inp_sz
  """
  if inp_sz < 0:
    raise AttributeError('Input should be >=0 and got %d' % inp_sz)
  if inp_sz < 1000:
    return '%d' % inp_sz
  if inp_sz < 1000 * 1000:
    return '%0.2fk' % (inp_sz / 1000.0)
  if inp_sz < 1000 * 1000 * 1000:
    return '%0.2fM' % (inp_sz / (1000.0 * 1000.0))
  if inp_sz < 1000 * 1000 * 1000 * 1000:
    return '%0.2fG' % (inp_sz / (1000.0 * 1000.0 * 1000.0))
  return '%0.2fT' % (inp_sz / (1000.0 * 1000.0 * 1000.0 * 1000.0))


def HumanizedSeconds(inp_secs: int) -> str:
  """Return human-readable time.

  Args:
    inp: An amount of time, in seconds

  Returns:
    human-readable time from the give number of seconds (inp_secs)
  """
  if inp_secs < 0:
    raise AttributeError('Input should be >=0 and got %d' % inp_secs)
  if inp_secs < 60:
    return '%d secs' % inp_secs
  if inp_secs < 60 * 60:
    return '%0.1f mins' % (inp_secs / 60.0)
  if inp_secs < 24 * 60 * 60:
    return '%0.1f hours' % (inp_secs / (60.0 * 60.0))
  return '%0.1f days' % (inp_secs / (24.0 * 60.0 * 60.0))


class Timer:
  """A chronometer context.

  Use with auto-logging, like:
      with Timer(log='Foo'):
        # do something
      # here it will log to info: 'Timed: Foo: X.XX min'

  Or use with manual access, like:
      with Timer() as tm:
        # do something
        print(tm.partial)  # will print '10.3 min' for example
        # do more
      time_delta_in_seconds = tm.delta
      print(tm.readable)  # will print '1.56 hours' for example

  See also the Timed() decorator below.
  """

  def __init__(self, log: Optional[str] = None) -> None:
    """Construct.

    Args:
      log: (default None) If given as string will logging.info a log upon __exit__
          like '%s: %s' % (log, execution_time)
    """
    self._start: Optional[float] = None
    self._end: Optional[float] = None
    self._log = log

  def __enter__(self) -> Any:
    """Enter Timed context. Starts the timer."""
    self._start = time.time()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb) -> Literal[False]:
    """Exit Timed context. Will stop the timer and will log if necessary."""
    _ = self.partial
    return False  # do not stop exceptions from propagating!

  @property
  def delta(self) -> float:
    """The time, in seconds. Cannot be called before some end is stored.

    Returns:
      delta, if any

    Raises:
      Error: chronometer is not set yet
    """
    if not self._start or not self._end:
      raise Error('Cannot get time from this chronometer yet.')
    return self._end - self._start

  @property
  def readable(self) -> str:
    """A readable string for the delta, in 'sec', 'min' or 'hours'."""
    d = self.delta
    if d > 7200.0:
      return '%0.3f hours' % (d / 3600.0)
    return '%0.3f min' % (d / 60.0) if d > 120.0 else '%0.3f sec' % d

  @property
  def partial(self) -> str:
    """Stores an end time (and will log if necessary)."""
    self._end = time.time()
    readable = self.readable
    if self._log is not None:
      logging.info('%s: %s', self._log, readable)
    return readable


def Timed(log: Optional[str] = None) -> Callable:
  """Make any call print its execution time, to be used as a decorator.

  Args:
    log: (default None) If given: The message to be displayed with the time;
        if not given will use the decorated method name for a simple message
  """

  def _Timed(func: Callable) -> Callable:

    @functools.wraps(func)
    def _wrapped_call(*args, **kwargs):
      log_message = '%r execution time' % (func.__name__ + '()') if log is None else log
      with Timer(log=log_message):
        return func(*args, **kwargs)

    return _wrapped_call

  return _Timed


def BinSerialize(obj: Any, file_path: Optional[str] = None) -> bytes:
  """Serialize a Python object into a BLOB.

  Args:
    obj: Any serializable Python object
    file_path: (default None) File full path to optionally save the data to;
        IO failures will be logged and ignored

  Returns:
    Serialized binary data (bytes) corresponding to obj
  """
  # serialize
  s_obj = pickle.dumps(obj, protocol=-1)
  c_obj = bz2.compress(s_obj, 9)
  logging.info(
      'serialization of obj; %s serial; %s compressed',
      HumanizedBytes(len(s_obj)), HumanizedBytes(len(c_obj)))
  # optionally save to disk
  if file_path is not None:
    try:
      with open(file_path, 'wb') as f:
        f.write(c_obj)
        logging.info('Bin file saved: %s', file_path)
    except IOError as err:
      logging.warning('Could not save bin file %r, error: %s', file_path, err)
  return c_obj


def BinDeSerialize(data: Optional[bytes] = None, file_path: Optional[str] = None) -> Any:
  """De-Serializes a BLOB back to a Python object.

  Args:
    data: (default None) BLOB (binary data string)
    file_path: (default None) File full path to optionally load the data from;
        If you use this option, then `data` WILL BE IGNORED and errors will be fatal,
        except non-existence of the file, which is checked for, and will make the method
        return None

  Returns:
    De-Serialized Python object corresponding to data; None if `file_name` is
    given and does not exist in config dir
  """
  # decompress from data or from disk
  len_disk_data = 0
  if file_path is None:
    if data is None:
      return None
    s_obj = bz2.decompress(data)
  else:
    if os.path.exists(file_path):
      logging.info('Reading bin file: %s', file_path)
      try:
        with open(file_path, 'rb') as f:
          disk_data = f.read()
          len_disk_data = len(disk_data)
          s_obj = bz2.decompress(disk_data)
      except IOError as err:
        logging.warning('Could not load bin file %r, error: %s', file_path, err)
        return None
    else:
      logging.warning('No bin file found: %s', file_path)
      return None
  # create the object
  obj = pickle.loads(s_obj)  # nosec - this is dangerous!
  logging.info(
      'serialization of obj; %s serial; %s compressed',
      HumanizedBytes(len(s_obj)),
      HumanizedBytes(len_disk_data if data is None else len(data)))
  return obj
