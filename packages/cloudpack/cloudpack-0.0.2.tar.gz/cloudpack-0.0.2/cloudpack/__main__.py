#!/usr/bin/env python3

import argparse
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


def init_vault(args):
    """
    Initialize a new CloudPack vault at the specified path.
    Creates the directory if it doesn't exist, and writes the default config file.
    Warns if the directory is not empty.
    """

    directory = Path(args.path).resolve()
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


def add_file(args):
    # TODO: implement
    pass


def upload_vault(args):
    # TODO: implement
    pass


def configure(args):
    # TODO: implement
    pass


def unlock(args):
    """
    Attempts to unlock the vault using the master password.
    """
    passwd_file = Path(args.path).resolve() / ".passwd"
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


def main():
    # === command parser ===
    commands = [
        {
            "name": "init",
            "help": "initialize a new vault",
            "func": init_vault,
            "args": [
                {
                    "name": "path",
                    "kwargs": {
                        "nargs": "?",
                        "type": Path,
                        "help": "optional path to the vault directory",
                        "default": ".",
                    },
                }
            ],
        },
        {
            "name": "config",
            "help": "configure the vault",
            "func": configure,
            "args": [],
        },
        {
            "name": "add",
            "help": "add a file to the vault",
            "func": add_file,
            "args": [
                {"name": "file", "kwargs": {"help": "path to the file to add"}},
            ],
        },
        {
            "name": "unlock",
            "help": "unlock the vault using the master password",
            "func": unlock,
            "args": [
                {
                    "name": "path",
                    "kwargs": {
                        "nargs": "?",
                        "type": Path,
                        "help": "optional path to the vault directory",
                        "default": ".",
                    },
                }
            ],
        },
        {
            "name": "upload",
            "help": "upload the vault to the cloud",
            "func": upload_vault,
            "args": [],
        },
    ]

    # define --path so it works globally (before or after subcommands)
    # e.g. `cloudpack init --path myVault` and `cloudpack --path myVault init`
    path_arg = {
        "flags": ("-p", "--path"),
        "kwargs": {
            "type": Path,
            "default": ".",
            "help": "path to the vault directory",
        },
    }

    parser = argparse.ArgumentParser(prog="cloudpack")
    parent_parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(*path_arg["flags"], **path_arg["kwargs"])
    parent_parser.add_argument(*path_arg["flags"], **path_arg["kwargs"])
    subparsers = parser.add_subparsers(title="commands", dest="command")

    for cmd in commands:
        sp = subparsers.add_parser(
            cmd["name"], parents=[parent_parser], help=cmd["help"]
        )
        for arg in cmd["args"]:
            sp.add_argument(arg["name"], **arg.get("kwargs", {}))
        sp.set_defaults(func=cmd["func"])

    # === command handler ===
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
