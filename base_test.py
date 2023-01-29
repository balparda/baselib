#!/usr/bin/python3 -bb
#
# Copyright 2023 Daniel Balparda (balparda@gmail.com)
#
"""base.py unittest."""

import os.path
# import pdb
import tempfile
import time
import unittest
# from unittest import mock

import base

__author__ = 'balparda@gmail.com (Daniel Balparda)'
__version__ = (1, 0)


class TestBase(unittest.TestCase):
  """Tests for base.py."""

  def test_HumanizedBytes(self):
    """Test."""
    self.assertEqual(base.HumanizedBytes(0), '0b')
    self.assertEqual(base.HumanizedBytes(10), '10b')
    self.assertEqual(base.HumanizedBytes(10000), '9.77kb')
    self.assertEqual(base.HumanizedBytes(10000000), '9.54Mb')
    self.assertEqual(base.HumanizedBytes(10000000000), '9.31Gb')
    self.assertEqual(base.HumanizedBytes(10000000000000), '9.09Tb')
    self.assertEqual(base.HumanizedBytes(10000000000000000), '9094.95Tb')
    with self.assertRaises(AttributeError):
      base.HumanizedBytes(-1)

  def test_HumanizedSeconds(self):
    """Test."""
    self.assertEqual(base.HumanizedSeconds(0), '0 secs')
    self.assertEqual(base.HumanizedSeconds(10), '10 secs')
    self.assertEqual(base.HumanizedSeconds(135), '2.2 mins')
    self.assertEqual(base.HumanizedSeconds(5000), '1.4 hours')
    self.assertEqual(base.HumanizedSeconds(100000), '1.2 days')
    with self.assertRaises(AttributeError):
      base.HumanizedSeconds(-1)

  def test_Serialize(self):
    """Test."""
    # do memory serialization test
    serial = base.BinSerialize(({1: 2, 3: 4}, []))
    obj = base.BinDeSerialize(serial)
    self.assertTupleEqual(obj, ({1: 2, 3: 4}, []))
    # do disk serialization test
    with tempfile.TemporaryDirectory() as tmpdir:
      tmp_file = os.path.join(tmpdir, 'base_test.test_Serialize.%d' % int(time.time()))
      base.BinSerialize(({4: 3, 2: 1}, [None, 7]), file_path=tmp_file)
      self.assertTupleEqual(
          base.BinDeSerialize(file_path=tmp_file), ({4: 3, 2: 1}, [None, 7]))

  def test_Timed(self):
    """Test."""
    with base.Timer() as tm:
      with self.assertRaises(base.Error):
        _ = tm.delta
    tm._start, tm._end = 1455237912.5451021, 1455237944.955657
    self.assertEqual(tm.readable, '32.411 sec')
    tm._end = tm._start + 1000
    self.assertEqual(tm.readable, '16.667 min')
    tm._end = tm._start + 10000
    self.assertEqual(tm.readable, '2.778 hours')

    @base.Timed('empty method')
    def _tm():
      pass

    _tm()


SUITE = unittest.TestLoader().loadTestsFromTestCase(TestBase)


if __name__ == '__main__':
  unittest.main()
