# -*- coding: utf-8 -*-
"""
AES encryption method
"""
import string
import secrets
import base64
import hmac
import hashlib
import os
from Crypto.Cipher import AES
from base64 import b64encode
from base64 import b64decode
from Crypto.Util.Padding import pad, unpad
from jax_tools.utils import settings as st


def get_local_key() -> str:
    """
    Ensure that the encryption key exists locally, if not, generate a new one
    Returns:

    """
    if os.path.exists(st.JAX_KEY_FILE):
        encryption_key = open(st.JAX_KEY_FILE, 'r').read().strip()
        if len(encryption_key) != 32:
            msg = 'encryption key length must be 32, please check file {} correct, or delete this file and try again.' \
                .format(st.JAX_KEY_FILE)
            print(msg)
            exit(1)
    else:
        # generate encryption key
        encryption_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        if os.path.exists(st.JAX_DATA_DIR) is False:
            os.mkdir(st.JAX_DATA_DIR)
        with open(st.JAX_KEY_FILE, 'w') as f:
            f.write(encryption_key)
    return encryption_key


class AESCipher(object):
    """
    AES Encryption Class, can use CBC or GCM mode, default is GCM mode
    You can use encrypt_body and decrypt_body to encrypt and decrypt request body
    You can use encrypt_content and decrypt_content to encrypt and decrypt content
    """

    # key for encrypting sensitive data
    def __init__(self, key: str = get_local_key(), cbc_mode: bool = False) -> None:
        """
        Init method
        Args:
            key: give a token  as a key use for encrypting request body
        """
        if len(key) > 32:
            # Get the key from key 8:24
            self.key = key[8:24]
        else:
            self.key = key
        self.length = 8
        # Default encryption mode is GCM, if you want to use CBC, set it to True
        self.cbc_mode = cbc_mode
        if self.cbc_mode:
            self.encryption_mode = AES.MODE_CBC
        else:
            self.encryption_mode = AES.MODE_GCM

    @staticmethod
    def get_random_str(length: int) -> str:
        """
        Get a string from random length.
        Args:
            length (int): Length of random string

        Returns:
            str: Random string

        """
        # get secret random
        random_str = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
        return random_str

    def encrypt(self, data: str, key: str = str()) -> str:
        """
        Encryption base  method
        Args:
            data (str): Data to encrypt
            key (str): Encryption key

        Returns:
            str: Encrypted string
        """
        if key == str():
            key = self.key
        key = key.encode('utf-8')
        iv = self.get_random_str(AES.block_size)
        cipher = AES.new(key, self.encryption_mode, iv.encode('utf-8'))
        cipher_text = b64encode(cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))).decode()
        result = "{0}{1}{2}{3}".format(iv[:self.length], cipher_text[:self.length], iv[self.length:],
                                       cipher_text[self.length:])
        return result

    def decrypt(self, data: str, key: str = str()) -> str:
        """
        Decryption base method
        Args:
            data (str): Data to decrypt
            key (str): Encryption key

        Returns:
            str: Decrypted string
        """
        if key == str():
            key = self.key
        key = key.encode('utf-8')
        iv = "{0}{1}".format(data[0:self.length], data[self.length
                                                       * 2:self.length * 2 + (AES.block_size - self.length)])
        cipher_text = "{0}{1}".format(
            data[self.length: self.length * 2], data[self.length + AES.block_size:])
        cipher = AES.new(key, self.encryption_mode, iv.encode('utf-8'))
        try:
            plaintext = unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size).decode()
        except ValueError:
            plaintext = 'Failed decrypt, please give a correct encrypted string'
        return plaintext


def encrypt_hmac_sha256(plaintext: str, secret_key: str) -> str:
    """
    Use HMAC-SHA256 to do irreversible encryption, such as encrypting user passwords

    Args:
        plaintext: plaintext
        secret_key: secret key

    Returns:
        str: Encrypted string
    """
    secret_key = secret_key.encode('utf-8')
    plaintext = plaintext.encode('utf-8')
    cipher_data = base64.b64encode(
        hmac.new(
            secret_key,
            plaintext,
            digestmod=hashlib.sha256).digest())
    return cipher_data.decode()

