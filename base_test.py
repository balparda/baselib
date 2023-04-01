#!/usr/bin/python3 -bb
#
# Copyright 2023 Daniel Balparda (balparda@gmail.com)
#
# pylint: disable=invalid-name,protected-access
"""base.py unittest."""

import base64
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

  def test_BasicCrypto(self):
    """Test."""
    crypto_key = b'LRtw2A4U9PAtihUow5p_eQex6IYKM7nUoPlf1fkKPgc='  # cspell:disable-line
    plaintext = 'the force will be with you... always'.encode('utf-8')
    cipher = base.Encrypt(plaintext, crypto_key)
    self.assertEqual(base.Decrypt(cipher, crypto_key), plaintext)
    self.assertEqual(len(cipher), 105)
    with self.assertRaises(base.bin_fernet.InvalidToken):
      base.Decrypt(cipher, b'0rCiyBrqWokX9UNBiYzkvhi9ZsjoIyGeUdtkbPAjzaY=')  # wrong key
    with self.assertRaises(base.bin_fernet.InvalidToken):
      base.Decrypt(cipher[5:], crypto_key)  # truncated ciphertext
    with self.assertRaises(ValueError):
      base.Encrypt(plaintext, crypto_key[10:])  # invalid key format

  def test_BlockEncoder256(self):
    """Test."""
    crypto_key = b'LRtw2A4U9PAtihUow5p_eQex6IYKM7nUoPlf1fkKPgc='  # cspell:disable-line
    digest = 'a771d3bd9b432b720b2bcebd3c4675d6d27d5868c5ce05261728ec9844b78a70'
    crypt_digest = 'd2ffc6e722eb0ae2db38b52796f4a13b0f1ace0befab9cdf265771951f9f89d6'
    bin_digest = bytes.fromhex(digest)
    encoder = base.BlockEncoder256(base64.urlsafe_b64decode(crypto_key))
    bin_cipher = encoder.EncryptBlock256(bin_digest)
    self.assertEqual(bin_cipher.hex(), crypt_digest)
    self.assertEqual(encoder.DecryptBlock256(bin_cipher), bin_digest)
    hex_cipher = encoder.EncryptHexdigest256(digest)
    self.assertEqual(hex_cipher, crypt_digest)
    self.assertEqual(encoder.DecryptHexdigest256(hex_cipher), digest)
    with self.assertRaises(base.Error):
      base.BlockEncoder256(b'abcd')
    with self.assertRaises(base.Error):
      encoder.EncryptBlock256(b'abcd')
    with self.assertRaises(base.Error):
      encoder.DecryptBlock256(b'abcd')
    with self.assertRaises(base.Error):
      encoder.EncryptHexdigest256('abcd')
    with self.assertRaises(base.Error):
      encoder.DecryptHexdigest256('abcd')
    with self.assertRaises(ValueError):
      encoder.EncryptHexdigest256('abc')
    with self.assertRaises(ValueError):
      encoder.DecryptHexdigest256('abc')

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
