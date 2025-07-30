import os
from configparser import ConfigParser
from pathlib import Path
from getpass import getpass

from cloudpack.crypto import encrypt, decrypt, derive_vault_key
from cloudpack.utils import is_password_secure

DEFAULT_CONFIG = """
; This is the configuration file for this cloudpack vault.
; Learn more at https://github.com/atar4xis/cloudpack

[vault]
version = 0.0.1

[provider:google_drive]
enabled = False
client_id =
client_secret =

[provider:dropbox]
enabled = False
client_id =
client_secret =
"""


def init(path):
    """
    Initialize a new CloudPack vault at the specified path.
    Creates the directory if it doesn't exist, and writes the default config file.
    Warns if the directory is not empty.
    """

    directory = Path(path).resolve()
    print(f"Initializing vault in {directory} ...")

    # create the directory if it doesn't exist
    if not directory.exists():
        directory.mkdir(parents=True)

    # warn if the directory is not empty
    if any(directory.iterdir()):
        print("Warning: Target directory is not empty")
        proceed = input("Proceed anyway? (y/N): ")
        if not proceed.strip().lower().startswith("y"):
            print("Operation aborted")
            return

    # create directory structure
    dir_tree = [
        "chunks",
    ]
    for dir in dir_tree:
        Path(directory / dir).mkdir(exist_ok=True)

    # write default configuration file
    config_file = directory / "config.ini"
    with open(config_file, "w") as f:
        f.write(DEFAULT_CONFIG)

    # write default meta file
    meta_file = directory / "vault.meta"
    with open(meta_file, "w") as f:
        f.write("{}")

    # === master password ===
    master_password = getpass("Enter master password: ")
    while not is_password_secure(master_password) and not master_password.startswith(
        "INSECURE: "
    ):
        print("""The password you entered is considered insecure.
We recommend using a password that meets the following criteria:
- At least 12 characters long
- Includes uppercase and lowercase letters
- Contains numbers and symbols

If you understand the risks and still wish to proceed,
you can bypass this check by prefixing your password with 'INSECURE: '
""")
        master_password = getpass("Enter master password: ")

    # if the password is insecure, strip the prefix
    if master_password.startswith("INSECURE: "):
        master_password = master_password[10:]

    # derive a vault key, encrypt a static string, store it in the .passwd file
    key_salt = os.urandom(16)
    vault_key = derive_vault_key(master_password, key_salt)
    with open(directory / ".passwd", "wb") as f:
        f.write(key_salt + encrypt(b"CloudPack", vault_key))

    # === initial configuration wizard ===
    config = ConfigParser()
    config.read(config_file)
    # TODO: implement wizard

    print("CloudPack vault initialized.")
    print("Now edit the configuration file:")
    print(f"  {config_file}")


def add(file):
    # TODO: implement
    pass


def upload():
    # TODO: implement
    pass


def configure(action, *args):
    # TODO: implement
    pass


def unlock(path):
    """
    Attempts to unlock the vault using the master password.
    """
    passwd_file = Path(path).resolve() / ".passwd"
    if not passwd_file.exists():
        print(
            "Error: Missing .passwd file. Make sure you are unlocking a cloudpack vault."
        )
        return

    master_password = getpass("Enter master password: ")
    data = passwd_file.read_bytes()
    key_salt = data[:16]
    encrypted_blob = data[16:]

    vault_key = derive_vault_key(master_password, key_salt)
    try:
        decrypted = decrypt(encrypted_blob, vault_key)
    except Exception:
        print("Invalid master password provided.")
        return

    if decrypted != b"CloudPack":
        print("Invalid master password provided.")
        return

    # TODO: implement
    print("Vault unlocked!")
