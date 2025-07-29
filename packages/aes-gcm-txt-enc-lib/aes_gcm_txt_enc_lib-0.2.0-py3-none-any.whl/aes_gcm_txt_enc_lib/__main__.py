from aes_gcm_txt_enc_lib.aes_gcm_encryptor import AesGcmEncryptor
from aes_gcm_txt_enc_lib.core import generate_key, encrypt, decrypt


if __name__ == "__main__":
    txt = "Hello this is text"
    print("Original Text: ", txt)
    a = AesGcmEncryptor(key_size=256)
    cipher = a.encrypt(txt)
    key = a.get_key()
    print("Key: ", key)
    print("Encrypted: ", cipher)

    b = AesGcmEncryptor(key)
    plain = b.decrypt(cipher)
    print("Decrypted: ", plain)
