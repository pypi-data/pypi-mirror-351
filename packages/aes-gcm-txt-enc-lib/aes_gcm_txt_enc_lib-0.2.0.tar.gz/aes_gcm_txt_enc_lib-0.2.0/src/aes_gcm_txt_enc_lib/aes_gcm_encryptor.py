from typing import Literal, Optional
from aes_gcm_txt_enc_lib.core import generate_key as g_k, encrypt as en, decrypt as de, validate_b64


class AesGcmEncryptor:
    def __init__(self, b64_key: Optional[str] = None, key_size: Literal[128, 192, 256] = 256):
        if b64_key:
            validate_b64(b64_key)
            self.key = b64_key
        else:
            self.key = g_k(key_size)

    def generate_key(self, key_size: Literal[128, 192, 256] = 256) -> None:
        self.key = g_k(key_size)

    def set_key(self, b64_key: str) -> None:
        validate_b64(b64_key)
        self.key = b64_key

    def get_key(self) -> str:
        return self.key

    def encrypt(self, plaintext: str) -> str:
        return en(plaintext, self.key)

    def decrypt(self, b64_ciphertext: str) -> str:
        return de(b64_ciphertext, self.key)


