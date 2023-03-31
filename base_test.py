#!/usr/bin/python3 -bb
#
# Copyright 2023 Daniel Balparda (balparda@gmail.com)
#
# pylint: disable=invalid-name,protected-access
"""base.py unittest."""

import os.path
# import pdb
import tempfile
import time
import unittest
# from unittest import mock

from baselib import base

__author__ = 'balparda@gmail.com (Daniel Balparda)'
__version__ = (1, 0)


class TestBase(unittest.TestCase):
  """Tests for base.py."""

  def test_TimeString(self):
    """Test."""
    self.assertEqual(base.STD_TIME_STRING(1675788907), '2023/Feb/07-16:55:07-UTC')

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

  def test_HumanizedDecimal(self):
    """Test."""
    self.assertEqual(base.HumanizedDecimal(0), '0')
    self.assertEqual(base.HumanizedDecimal(11), '11')
    self.assertEqual(base.HumanizedDecimal(12100), '12.10k')
    self.assertEqual(base.HumanizedDecimal(13200000), '13.20M')
    self.assertEqual(base.HumanizedDecimal(14300000000), '14.30G')
    self.assertEqual(base.HumanizedDecimal(15400000000000), '15.40T')
    self.assertEqual(base.HumanizedDecimal(16500000000000000), '16500.00T')
    with self.assertRaises(AttributeError):
      base.HumanizedDecimal(-1)

  def test_HumanizedSeconds(self):
    """Test."""
    self.assertEqual(base.HumanizedSeconds(0), '0 secs')
    self.assertEqual(base.HumanizedSeconds(0.0), '0 secs')
    self.assertEqual(base.HumanizedSeconds(0.00456789), '4.568 msecs')
    self.assertEqual(base.HumanizedSeconds(0.456789), '0.4568 secs')
    self.assertEqual(base.HumanizedSeconds(10), '10.00 secs')
    self.assertEqual(base.HumanizedSeconds(135), '2.25 mins')
    self.assertEqual(base.HumanizedSeconds(5000), '1.39 hours')
    self.assertEqual(base.HumanizedSeconds(100000), '1.16 days')
    with self.assertRaises(AttributeError):
      base.HumanizedSeconds(-1)

  def test_DeriveKeyFromStaticPassword(self):
    """Test."""
    with self.assertRaisesRegex(base.Error, 'Empty passwords'):
      base.DeriveKeyFromStaticPassword(None)  # type: ignore
    with self.assertRaisesRegex(base.Error, 'Empty passwords'):
      base.DeriveKeyFromStaticPassword('  \n ')
    with base.Timer(log='DeriveKeyFromStaticPassword - luke'):
      self.assertEqual(
          base.DeriveKeyFromStaticPassword('luke'),
          b'0rCiyBrqWokX9UNBiYzkvhi9ZsjoIyGeUdtkbPAjzaY=')
    with base.Timer(log='DeriveKeyFromStaticPassword - Ben Star Wars Jedi'):
      self.assertEqual(
          base.DeriveKeyFromStaticPassword('Ben Star Wars Jedi'),
          b'yAK_QpO2RrSqwzzO8relAbl5c_cBgvp_cVPtk1D-Hrw=')  # cspell:disable-line

  def test_Serialize(self):
    """Test."""
    # do memory serialization test
    serial = base.BinSerialize(({1: 2, 3: 4}, []))
    obj = base.BinDeSerialize(serial)
    self.assertTupleEqual(obj, ({1: 2, 3: 4}, []))
    # do uncompressed memory serialization test
    serial = base.BinSerialize(({5: 6, 7: 8}, [9, 10]), compress=False)
    obj = base.BinDeSerialize(serial, compress=False)
    self.assertTupleEqual(obj, ({5: 6, 7: 8}, [9, 10]))
    # do encrypted uncompressed memory serialization test
    crypto_key = b'LRtw2A4U9PAtihUow5p_eQex6IYKM7nUoPlf1fkKPgc='  # cspell:disable-line
    serial = base.BinSerialize(({10: 9, 8: 7}, {6, 5}), compress=False, key=crypto_key)
    obj = base.BinDeSerialize(serial, compress=False, key=crypto_key)
    self.assertTupleEqual(obj, ({10: 9, 8: 7}, {6, 5}))
    # do encrypted and compressed memory serialization test
    serial = base.BinSerialize(({100: 90, 80: 70}, {60, 50}), compress=True, key=crypto_key)
    obj = base.BinDeSerialize(serial, key=crypto_key)
    self.assertTupleEqual(obj, ({100: 90, 80: 70}, {60, 50}))
    # do compressed disk serialization test
    with tempfile.TemporaryDirectory() as tmpdir:
      tmp_file = os.path.join(tmpdir, f'base_test.test_Serialize.{int(time.time())}')
      base.BinSerialize(({4: 3, 2: 1}, [None, 7]), file_path=tmp_file)
      self.assertTupleEqual(
          base.BinDeSerialize(file_path=tmp_file), ({4: 3, 2: 1}, [None, 7]))

  def test_Timed(self):
    """Test."""
    with base.Timer() as tm:
      with self.assertRaises(base.Error):
        _ = tm.delta
    tm._start, tm._end = 1455237912.5451021, 1455237944.955657
    self.assertEqual(tm.readable, '32.41 secs')
    tm._end = tm._start + 1000
    self.assertEqual(tm.readable, '16.67 mins')
    tm._end = tm._start + 10000
    self.assertEqual(tm.readable, '2.78 hours')

    @base.Timed('empty method')
    def _tm():
      pass

    _tm()


SUITE = unittest.TestLoader().loadTestsFromTestCase(TestBase)


if __name__ == '__main__':
  unittest.main()
