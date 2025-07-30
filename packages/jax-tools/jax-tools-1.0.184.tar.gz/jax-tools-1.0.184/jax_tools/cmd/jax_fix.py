# -*- coding: utf-8 -*-
"""
jax_fix use for provide information to help fix problem
"""
import sys


def main() -> None:
    """
    Main function
    Returns:

    """
    info_dict = {
        "pip": "Upgrade pip: python -m pip install --upgrade pip",
    }
    if len(sys.argv) == 1:
        print("Usage: jax-fix <command>")
        print("arguments:")
        for key in info_dict.keys():
            print(key)
        exit(0)
    if sys.argv[1] in info_dict.keys():
        print(info_dict[sys.argv[1]])
    else:
        print("Usage: jax-fix <command>")
        print("arguments:")
        for key in info_dict.keys():
            print(key)
