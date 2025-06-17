#!/usr/bin/env python3
#
# Copyright 2025 Daniel Balparda (balparda@github.com) - Apache-2.0 license
#
# pylint: disable=invalid-name,protected-access
"""base.py unittest."""

import base64
import io
import json
import logging
import os.path
# import pdb
import tempfile
import time
import unittest
from unittest import mock

from src.baselib import base  # pylint: disable=import-error

__author__ = 'balparda@github.com (Daniel Balparda)'
__version__ = (1, 6)


class TestBase(unittest.TestCase):
  """Tests for base.py."""

  def test_StartStdErrLogging_default(self) -> None:
    """Test."""
    # Capture stdout to verify logging output
    with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
      # Reset logger handlers to avoid interference from prior tests
      logger: logging.Logger = logging.getLogger()
      logger.handlers = []
      # Call the function
      base.StartStdErrLogging()
      logging.info('Test message')
      # Check the captured output
      output = mock_stdout.getvalue()
      self.assertIn('Test message', output)
      self.assertEqual(logger.level, logging.INFO)
      # Verify we have exactly one handler
      self.assertEqual(len(logger.handlers), 1)

  def test_StartStdErrLogging_custom_level_and_log_process(self) -> None:
    """Test."""
    with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
      logger: logging.Logger = logging.getLogger()
      logger.handlers = []
      base.StartStdErrLogging(level=logging.DEBUG, log_process=True)
      logging.debug('Debug message')
      output = mock_stdout.getvalue()
      self.assertIn('Debug message', output)
      # Check logger level
      self.assertEqual(logger.level, logging.DEBUG)
      self.assertEqual(len(logger.handlers), 1)
      # The format includes process name if log_process=True; typically see process name in brackets
      # (Actual format depends on _LOG_FORMATS in your code.)
      self.assertIn('MainProcess', output)  # or whichever process name if multi-processing

  def test_JsonToString_human_readable(self) -> None:
    """Test."""
    data: dict[str, int] = {'a': 1, 'b': 2}
    result: str = base.JsonToString(data, human_readable=True)  # type:ignore
    # Should have indentation and newlines
    self.assertIn('\n', result)
    # Confirm it can be parsed back
    parsed = json.loads(result)
    self.assertEqual(parsed, data)

  def test_JsonToString_compact(self) -> None:
    """Test."""
    data = {'x': 42, 'y': [1, 2, 3]}  # type:ignore
    result: str = base.JsonToString(data, human_readable=False)  # type:ignore
    # Should not have pretty formatting
    self.assertNotIn('\n', result)
    parsed = json.loads(result)
    self.assertEqual(parsed, data)

  def test_JsonToBytes(self) -> None:
    """Test."""
    data: dict[str, str] = {'key': 'value'}
    result: bytes = base.JsonToBytes(data)  # type:ignore
    self.assertIsInstance(result, bytes)
    # Check round-trip
    parsed = json.loads(result.decode('utf-8'))
    self.assertEqual(parsed, data)

  def test_StringToJson(self) -> None:
    """Test."""
    json_str = '{"hello": "world", "n": 123}'
    parsed: base.JsonType = base.StringToJson(json_str)
    self.assertEqual(parsed, {'hello': 'world', 'n': 123})

  def test_BytesToJson(self) -> None:
    """Test."""
    json_bytes = b'{"arr": [1, 2, 3]}'
    parsed: base.JsonType = base.BytesToJson(json_bytes)
    self.assertEqual(parsed, {'arr': [1, 2, 3]})

  def test_BytesBinHash(self) -> None:
    """Test."""
    data = b'hello world'
    bin_hash: bytes = base.BytesBinHash(data)
    self.assertIsInstance(bin_hash, bytes)
    self.assertEqual(len(bin_hash), 32)  # 32 bytes for SHA-256
    # Check against a known SHA-256 for "hello world"
    expected_hex: str = base.hashlib.sha256(data).hexdigest()
    self.assertEqual(bin_hash, bytes.fromhex(expected_hex))

  def test_BytesHexHash(self) -> None:
    """Test."""
    data = b'abc123'
    hex_hash: str = base.BytesHexHash(data)
    self.assertIsInstance(hex_hash, str)
    self.assertEqual(len(hex_hash), 64)
    # Compare with known
    expected_hex = base.hashlib.sha256(data).hexdigest()
    self.assertEqual(hex_hash, expected_hex)

  def test_FileHexHash(self) -> None:
    """Test."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
      try:
        tmp_file.write(b'Some test content')
        tmp_file.flush()
        path: str = tmp_file.name
      finally:
        tmp_file.close()
      # Test successful hash
      result: str = base.FileHexHash(path)
      self.assertEqual(len(result), 64)
      expected_hex: str = base.hashlib.sha256(b'Some test content').hexdigest()
      self.assertEqual(result, expected_hex)
      # Cleanup
      os.remove(path)

  def test_FileHexHash_missing_file(self) -> None:
    """Test."""
    with self.assertRaises(Exception):
      base.FileHexHash('/path/to/surely/not/exist-123')

  def test_ImageHexHash(self) -> None:
    """Test."""
    # Create 1x1 black image
    img: base.Image.Image = base.Image.new('RGB', (1, 1), color=(0, 0, 0))
    hex_hash: str = base.ImageHexHash(img)
    self.assertIsInstance(hex_hash, str)
    self.assertEqual(len(hex_hash), 64)
    # Re-hash with the known approach to confirm correctness
    direct_hex: str = base.hashlib.sha256(img.tobytes()).hexdigest()  # type:ignore
    self.assertEqual(hex_hash, direct_hex)

  def test_TimeString(self) -> None:
    """Test."""
    self.assertEqual(base.STD_TIME_STRING(1675788907), '2023/Feb/07-16:55:07-UTC')

  def test_HumanizedBytes(self) -> None:
    """Test."""
    self.assertEqual(base.HumanizedBytes(0), '0b')
    self.assertEqual(base.HumanizedBytes(10), '10b')
    self.assertEqual(base.HumanizedBytes(10000), '9.77kb')
    self.assertEqual(base.HumanizedBytes(10000000), '9.54Mb')
    self.assertEqual(base.HumanizedBytes(10000000000), '9.31Gb')
    self.assertEqual(base.HumanizedBytes(10000000000000), '9.09Tb')
    self.assertEqual(base.HumanizedBytes(10000000000000000), '9094.95Tb')
    with self.assertRaises(base.Error):
      base.HumanizedBytes(-1)

  def test_HumanizedDecimal(self) -> None:
    """Test."""
    self.assertEqual(base.HumanizedDecimal(0), '0')
    self.assertEqual(base.HumanizedDecimal(11), '11')
    self.assertEqual(base.HumanizedDecimal(12100), '12.10k')
    self.assertEqual(base.HumanizedDecimal(13200000), '13.20M')
    self.assertEqual(base.HumanizedDecimal(14300000000), '14.30G')
    self.assertEqual(base.HumanizedDecimal(15400000000000), '15.40T')
    self.assertEqual(base.HumanizedDecimal(16500000000000000), '16500.00T')
    with self.assertRaises(base.Error):
      base.HumanizedDecimal(-1)

  def test_HumanizedSeconds(self) -> None:
    """Test."""
    self.assertEqual(base.HumanizedSeconds(0), '0 secs')
    self.assertEqual(base.HumanizedSeconds(0.0), '0 secs')
    self.assertEqual(base.HumanizedSeconds(0.00456789), '4.568 msecs')
    self.assertEqual(base.HumanizedSeconds(0.456789), '0.4568 secs')
    self.assertEqual(base.HumanizedSeconds(10), '10.00 secs')
    self.assertEqual(base.HumanizedSeconds(135), '2.25 mins')
    self.assertEqual(base.HumanizedSeconds(5000), '1.39 hours')
    self.assertEqual(base.HumanizedSeconds(100000), '1.16 days')
    with self.assertRaises(base.Error):
      base.HumanizedSeconds(-1)

  def test_DeriveKeyFromStaticPassword(self) -> None:
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

  def test_BasicCrypto(self) -> None:
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

  def test_BlockEncoder256(self) -> None:
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

  def test_Serialize(self) -> None:
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

  def test_Timed(self) -> None:
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

    @base.Timed('empty method')  # type:ignore
    def _tm() -> None:
      pass

    _tm()  # type:ignore


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format=base.LOG_FORMAT)  # set this as default
  unittest.main(verbosity=2)
