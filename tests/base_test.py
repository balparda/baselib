#!/usr/bin/env python3
#
# Copyright 2025 Daniel Balparda (balparda@github.com) - Apache-2.0 license
#
# pylint: disable=invalid-name,protected-access
# pyright: reportPrivateUsage=false
"""base.py unittest."""

import base64
import json
import os.path
# import pdb
import sys
import tempfile
import time
from typing import Any, Generator

import pytest

from src.balparda_baselib import base

__author__ = 'balparda@github.com (Daniel Balparda)'
__version__: tuple[int, int] = (1, 9)


def test_JsonToString_human_readable() -> None:
  """Test."""
  data: dict[str, int] = {'a': 1, 'b': 2}
  result: str = base.JsonToString(data, human_readable=True)  # type:ignore
  # Should have indentation and newlines
  assert '\n' in result
  # Confirm it can be parsed back
  assert json.loads(result) == data


def test_JsonToString_compact() -> None:
  """Test."""
  data = {'x': 42, 'y': [1, 2, 3]}  # type:ignore
  result: str = base.JsonToString(data, human_readable=False)  # type:ignore
  # Should not have pretty formatting
  assert '\n' not in result
  assert json.loads(result) == data


def test_JsonToBytes() -> None:
  """Test."""
  data: dict[str, str] = {'key': 'value'}
  result: bytes = base.JsonToBytes(data)  # type:ignore
  assert isinstance(result, bytes)
  # Check round-trip
  assert json.loads(result.decode('utf-8')) == data


def test_StringToJson() -> None:
  """Test."""
  json_str = '{"hello": "world", "n": 123}'
  parsed: base.JsonType = base.StringToJson(json_str)
  assert parsed == {'hello': 'world', 'n': 123}


def test_BytesToJson() -> None:
  """Test."""
  json_bytes = b'{"arr": [1, 2, 3]}'
  parsed: base.JsonType = base.BytesToJson(json_bytes)
  assert parsed == {'arr': [1, 2, 3]}


def test_BytesBinHash() -> None:
  """Test."""
  data = b'hello world'
  bin_hash: bytes = base.BytesBinHash(data)
  assert isinstance(bin_hash, bytes)
  assert len(bin_hash) == 32  # 32 bytes for SHA-256
  # Check against a known SHA-256 for "hello world"
  expected_hex: str = base.hashlib.sha256(data).hexdigest()
  assert bin_hash == bytes.fromhex(expected_hex)


def test_BytesHexHash() -> None:
  """Test."""
  data = b'abc123'
  hex_hash: str = base.BytesHexHash(data)
  assert isinstance(hex_hash, str)
  assert len(hex_hash) == 64
  # Compare with known
  expected_hex = base.hashlib.sha256(data).hexdigest()
  assert hex_hash == expected_hex


@pytest.fixture
def temp_small_file() -> Generator[str, None, None]:
  """Small temporary file with fixed b'Some test content' bytes."""
  with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    tmp_file.write(b'Some test content')
    tmp_file.flush()
    yield tmp_file.name
  # remove the file after the test
  os.remove(tmp_file.name)


def test_FileHexHash(temp_small_file: str) -> None:  # pylint: disable=redefined-outer-name
  """Test."""
  result: str = base.FileHexHash(temp_small_file)
  assert len(result) == 64
  expected_hex: str = base.hashlib.sha256(b'Some test content').hexdigest()
  assert result == expected_hex


def test_FileHexHash_missing_file() -> None:
  """Test."""
  with pytest.raises(Exception):
    base.FileHexHash('/path/to/surely/not/exist-123')


def test_ImageHexHash() -> None:
  """Test."""
  # Create 1x1 black image
  img: base.Image.Image = base.Image.new('RGB', (1, 1), color=(0, 0, 0))
  hex_hash: str = base.ImageHexHash(img)
  assert isinstance(hex_hash, str)
  assert len(hex_hash) == 64
  # Re-hash with the known approach to confirm correctness
  direct_hex: str = base.hashlib.sha256(img.tobytes()).hexdigest()  # type:ignore
  assert hex_hash == direct_hex


def test_TimeString() -> None:
  """Test."""
  assert base.STD_TIME_STRING(1675788907) == '2023/Feb/07-16:55:07-UTC'


def test_HumanizedBytes() -> None:
  """Test."""
  assert base.HumanizedBytes(0) == '0b'
  assert base.HumanizedBytes(10) == '10b'
  assert base.HumanizedBytes(10000) == '9.77kb'
  assert base.HumanizedBytes(10000000) == '9.54Mb'
  assert base.HumanizedBytes(10000000000) == '9.31Gb'
  assert base.HumanizedBytes(10000000000000) == '9.09Tb'
  assert base.HumanizedBytes(10000000000000000) == '9094.95Tb'
  with pytest.raises(base.Error):
    base.HumanizedBytes(-1)


def test_HumanizedDecimal() -> None:
  """Test."""
  assert base.HumanizedDecimal(0) == '0'
  assert base.HumanizedDecimal(11) == '11'
  assert base.HumanizedDecimal(12100) == '12.10k'
  assert base.HumanizedDecimal(13200000) == '13.20M'
  assert base.HumanizedDecimal(14300000000) == '14.30G'
  assert base.HumanizedDecimal(15400000000000) == '15.40T'
  assert base.HumanizedDecimal(16500000000000000) == '16500.00T'
  with pytest.raises(base.Error):
    base.HumanizedDecimal(-1)


def test_HumanizedSeconds() -> None:
  """Test."""
  assert base.HumanizedSeconds(0) == '0 secs'
  assert base.HumanizedSeconds(0.0) == '0 secs'
  assert base.HumanizedSeconds(0.00456789) == '4.568 msecs'
  assert base.HumanizedSeconds(0.456789) == '0.4568 secs'
  assert base.HumanizedSeconds(10) == '10.00 secs'
  assert base.HumanizedSeconds(135) == '2.25 mins'
  assert base.HumanizedSeconds(5000) == '1.39 hours'
  assert base.HumanizedSeconds(100000) == '1.16 days'
  with pytest.raises(base.Error):
    base.HumanizedSeconds(-1)


def test_DeriveKeyFromStaticPassword() -> None:
  """Test."""
  with pytest.raises(base.Error, match='Empty passwords'):
    base.DeriveKeyFromStaticPassword(None)  # type: ignore
  with pytest.raises(base.Error, match='Empty passwords'):
    base.DeriveKeyFromStaticPassword('  \n ')
  with base.Timer(log='DeriveKeyFromStaticPassword - luke'):
    assert base.DeriveKeyFromStaticPassword('luke') == b'0rCiyBrqWokX9UNBiYzkvhi9ZsjoIyGeUdtkbPAjzaY='
  with base.Timer(log='DeriveKeyFromStaticPassword - Ben Star Wars Jedi'):
    assert base.DeriveKeyFromStaticPassword('Ben Star Wars Jedi') == b'yAK_QpO2RrSqwzzO8relAbl5c_cBgvp_cVPtk1D-Hrw='


def test_BasicCrypto() -> None:
  """Test."""
  crypto_key = b'LRtw2A4U9PAtihUow5p_eQex6IYKM7nUoPlf1fkKPgc='
  plaintext: bytes = 'the force will be with you... always'.encode('utf-8')
  cipher: bytes = base.Encrypt(plaintext, crypto_key)
  assert base.Decrypt(cipher, crypto_key) == plaintext
  assert len(cipher) == 105
  with pytest.raises(base.bin_fernet.InvalidToken):
    base.Decrypt(cipher, b'0rCiyBrqWokX9UNBiYzkvhi9ZsjoIyGeUdtkbPAjzaY=')  # wrong key
  with pytest.raises(base.bin_fernet.InvalidToken):
    base.Decrypt(cipher[5:], crypto_key)  # truncated ciphertext
  with pytest.raises(ValueError):
    base.Encrypt(plaintext, crypto_key[10:])  # invalid key format


def test_BlockEncoder256() -> None:
  """Test."""
  crypto_key = b'LRtw2A4U9PAtihUow5p_eQex6IYKM7nUoPlf1fkKPgc='
  digest = 'a771d3bd9b432b720b2bcebd3c4675d6d27d5868c5ce05261728ec9844b78a70'
  crypt_digest = 'd2ffc6e722eb0ae2db38b52796f4a13b0f1ace0befab9cdf265771951f9f89d6'
  bin_digest: bytes = bytes.fromhex(digest)
  encoder = base.BlockEncoder256(base64.urlsafe_b64decode(crypto_key))
  bin_cipher: bytes = encoder.EncryptBlock256(bin_digest)
  assert bin_cipher.hex() == crypt_digest
  assert encoder.DecryptBlock256(bin_cipher) == bin_digest
  hex_cipher: str = encoder.EncryptHexdigest256(digest)
  assert hex_cipher == crypt_digest
  assert encoder.DecryptHexdigest256(hex_cipher) == digest
  with pytest.raises(base.Error):
    base.BlockEncoder256(b'abcd')
  with pytest.raises(base.Error):
    encoder.EncryptBlock256(b'abcd')
  with pytest.raises(base.Error):
    encoder.DecryptBlock256(b'abcd')
  with pytest.raises(base.Error):
    encoder.EncryptHexdigest256('abcd')
  with pytest.raises(base.Error):
    encoder.DecryptHexdigest256('abcd')
  with pytest.raises(ValueError):
    encoder.EncryptHexdigest256('abc')
  with pytest.raises(ValueError):
    encoder.DecryptHexdigest256('abc')


def test_Serialize() -> None:
  """Test."""
  # do memory serialization test
  serial: bytes = base.BinSerialize(({1: 2, 3: 4}, []))
  obj: Any = base.BinDeSerialize(serial)
  assert obj == ({1: 2, 3: 4}, [])
  # do uncompressed memory serialization test
  serial = base.BinSerialize(({5: 6, 7: 8}, [9, 10]), compress=False)
  obj = base.BinDeSerialize(serial, compress=False)
  assert obj == ({5: 6, 7: 8}, [9, 10])
  # do encrypted uncompressed memory serialization test
  crypto_key = b'LRtw2A4U9PAtihUow5p_eQex6IYKM7nUoPlf1fkKPgc='
  serial = base.BinSerialize(({10: 9, 8: 7}, {6, 5}), compress=False, key=crypto_key)
  obj = base.BinDeSerialize(serial, compress=False, key=crypto_key)
  assert obj == ({10: 9, 8: 7}, {6, 5})
  # do encrypted and compressed memory serialization test
  serial = base.BinSerialize(({100: 90, 80: 70}, {60, 50}), compress=True, key=crypto_key)
  obj = base.BinDeSerialize(serial, key=crypto_key)
  assert obj == ({100: 90, 80: 70}, {60, 50})
  # do compressed disk serialization test
  with tempfile.TemporaryDirectory() as tmpdir:
    tmp_file = os.path.join(tmpdir, f'base_test.test_Serialize.{int(time.time())}')
    base.BinSerialize(({4: 3, 2: 1}, [None, 7]), file_path=tmp_file)
    assert base.BinDeSerialize(file_path=tmp_file) == ({4: 3, 2: 1}, [None, 7])


def test_Timed() -> None:
  """Test."""
  with base.Timer() as tm:
    with pytest.raises(base.Error):
      _ = tm.delta
  tm._start, tm._end = 1455237912.5451021, 1455237944.955657
  assert tm.readable == '32.41 secs'
  tm._end = tm._start + 1000
  assert tm.readable == '16.67 mins'
  tm._end = tm._start + 10000
  assert tm.readable == '2.78 hours'

  @base.Timed('empty method')  # type:ignore
  def _tm() -> None:
    pass

  _tm()  # type:ignore


if __name__ == '__main__':
  # run only the tests in THIS file but pass through any extra CLI flags
  args: list[str] = sys.argv[1:] + [__file__]
  print(f'pytest {" ".join(args)}')
  sys.exit(pytest.main(sys.argv[1:] + [__file__]))
