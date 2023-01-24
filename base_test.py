#!/usr/bin/python3 -bb
# pylint: disable=bad-indentation, invalid-name, bad-continuation
# pylint: disable=missing-docstring, protected-access
#
# Copyright 2018 Daniel Balparda (balparda@gmail.com)
#
"""base.py unittest."""

# import pdb
import tempfile
import time
import unittest
from unittest import mock

from baselib import base

__author__ = 'balparda@gmail.com (Daniel Balparda)'
__version__ = (1, 0)


class TestBase(unittest.TestCase):  # pylint: disable=unused-variable

  def test_Serialize(self):
    # do memory serialization test
    serial = base.BinSerialize(({1:2, 3:4}, []))
    obj = base.BinDeSerialize(serial)
    self.assertTupleEqual(obj, ({1:2, 3:4}, []))
    # do disk serialization test; monkey-path CONFIG_DIR temporarily for this
    # with tempfile.TemporaryDirectory() as tmpdir:
    #   tmp_file = 'base.TestBase.test_Serialize.%d' % int(time.time())
    #   original_config = base.CONFIG_DIR
    #   base.CONFIG_DIR = tmpdir
    #   try:
    #     base.BinSerialize(({4:3, 2:1}, [None, 7]), file_name=tmp_file)
    #     self.assertTupleEqual(
    #         base.BinDeSerialize(file_name=tmp_file), ({4:3, 2:1}, [None, 7]))
    #   finally:
    #     base.CONFIG_DIR = original_config

  def test_Timed(self):
    with base.Timer() as tm:
      with self.assertRaises(base.Error):
        _ = tm.delta
    tm._start, tm._end = 1455237912.5451021, 1455237944.955657
    self.assertEqual(tm.readable, '32.411 sec')
    tm._end = tm._start + 1000
    self.assertEqual(tm.readable, '16.667 min')
    tm._end = tm._start + 10000
    self.assertEqual(tm.readable, '2.778 hours')


if __name__ == '__main__':
  unittest.main()
