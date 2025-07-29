import base64
from typing import Literal
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode()


def _b64d(s: str) -> bytes:
    return base64.b64decode(s)


def validate_b64(b64_key: str) -> None:
    try:
        base64.b64decode(b64_key)
    except Exception as e:
        raise ValueError("Invalid Base64 key format") from e


def generate_key(key_size: Literal[128, 192, 256] = 256) -> str:
    if key_size not in (128, 192, 256):
        raise ValueError("Invalid AES key size.")
    return _b64e(get_random_bytes(key_size // 8))


def encrypt(plaintext: str, b64_key: str) -> str:
    key = _b64d(b64_key)
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return _b64e(nonce + tag + ciphertext)


def decrypt(b64_ciphertext: str, b64_key: str) -> str:
    key = _b64d(b64_key)
    try:
        data = _b64d(b64_ciphertext)
        if len(data) < 28:
            raise ValueError("Ciphertext too short")

        nonce, tag, ciphertext = data[:12], data[12:28], data[28:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
    except Exception as e:
        raise ValueError("Decryption failed: " + str(e)) from e
