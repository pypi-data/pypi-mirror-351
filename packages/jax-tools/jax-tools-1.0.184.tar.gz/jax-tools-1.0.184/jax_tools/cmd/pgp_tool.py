import gnupg

def encrypt_file(public_key_path: str, file_to_encrypt: str, output_file: str) -> None:
    """
    Encrypt a file using a PGP public key.

    :param public_key_path: Path to the PGP public key file
    :param file_to_encrypt: Path to the file to be encrypted
    :param output_file: Path to the output encrypted file
    """
    gpg = gnupg.GPG()

    # Import the public key
    with open(public_key_path, 'r') as key_file:
        key_data = key_file.read()
        gpg.import_keys(key_data)

    # Encrypt the file
    with open(file_to_encrypt, 'rb') as f:
        status = gpg.encrypt(f.read(), recipients=[], output=output_file)

    if not status.ok:
        raise ValueError(f"Encryption failed: {status.stderr}")

def decrypt_file(private_key_path: str, passphrase: str, encrypted_file: str, output_file: str) -> None:
    """
    Decrypt a file using a PGP private key.

    :param private_key_path: Path to the PGP private key file
    :param passphrase: Passphrase for the private key
    :param encrypted_file: Path to the encrypted file
    :param output_file: Path to the output decrypted file
    """
    gpg = gnupg.GPG()

    # Import the private key
    with open(private_key_path, 'r') as key_file:
        key_data = key_file.read()
        gpg.import_keys(key_data)

    # Decrypt the file
    with open(encrypted_file, 'rb') as f:
        status = gpg.decrypt_file(f, passphrase=passphrase, output=output_file)

    if not status.ok:
        raise ValueError(f"Decryption failed: {status.stderr}")


if __name__ == '__main__':
    encrypt_file(public_key_path=r'D:\Nextcloud\01-Products\BastionHost\安全版\Documents\Huawei_PSIRT_PGP_Public_Key.asc', file_to_encrypt=r'D:\Nextcloud\01-Products\BastionHost\安全版\Documents\To Huawei\安全漏洞预警通知YBL-2024-112901 - 副本.docx', output_file=r"D:\Nextcloud\01-Products\BastionHost\安全版\Documents\To Huawei\test.gpg")