# aes-gcm-txt-enc-lib

Python library for symmetric key based secure text encryption and decryption using AES-GCM.

## Features

- AES-GCM symmetric encryption for text data
- Support for multiple key lengths (128, 192, 256 bits)
- Easy-to-use API for encryption and decryption
- Built on `pycryptodome` for cryptographic primitives

## Installation

Install via PyPI:

```bash
pip install aes-gcm-txt-enc-lib
```

Usage Example

```python
from aes_gcm_txt_enc_lib import AesGcmEncryptor

txt = "Hello this is text"
print("Original Text: ", txt)

# Create an encryptor with a 256-bit random key
a = AesGcmEncryptor(key_size=256)
cipher = a.encrypt(txt)
key = a.get_key()

print("Key: ", key)
print("Encrypted: ", cipher)

# Create a new encryptor with the same key for decryption
b = AesGcmEncryptor(key)
plain = b.decrypt(cipher)

print("Decrypted: ", plain)
```

## 📄 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.