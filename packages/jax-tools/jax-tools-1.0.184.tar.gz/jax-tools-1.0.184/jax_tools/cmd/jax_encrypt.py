# -*- coding:utf-8 -*-
"""
jax-encrypt cmd, provide encryption and decryption functions
"""
import sys
import os
import argparse
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jax_tools.encrypt import AESCipher
from jax_tools.encrypt import get_local_key


# Ensure the existence of the encryption key file
JAX_ENCRYPT = AESCipher().encrypt
JAX_DECRYPT = AESCipher().decrypt


def main() -> None:
    """
    main
    Returns:

    """
    parser = argparse.ArgumentParser(
        description="Jax-encrypt is used to encrypt and decrypt your sensitive information", prog='JAX-ENCRYPT')
    parser.add_argument('-d', '--decrypt', type=str, default=None, help='Specifies the string to be decrypted')
    parser.add_argument('-e', '--encrypt', type=str, default=None, help='SSpecifies the encryption string')
    parser.add_argument('-k', '--key', type=str, default=None, help='Specifies the encryption key')
    parser.add_argument('-t', '--type', type=str, default='gcm', help='Specifies the encryption type, cbc or gcm')
    parser.add_argument('-v', '--version', action='version', version='1.0')
    options = parser.parse_args()
    if options.key is not None:
        key = options.key
    else:
        key = get_local_key()
    if options.type.lower().__contains__('cbc'):
        cbc_mode = True
    else:
        cbc_mode = False
    if options.decrypt is not None:
        print(AESCipher(key, cbc_mode).decrypt(options.decrypt))
    if options.encrypt is not None:
        print(AESCipher(key, cbc_mode).encrypt(options.encrypt))


if __name__ == '__main__':
    main()
