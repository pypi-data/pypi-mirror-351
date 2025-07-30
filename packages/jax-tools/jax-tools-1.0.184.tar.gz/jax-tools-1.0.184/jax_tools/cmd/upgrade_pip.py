# -*- coding: utf-8 -*-
"""
Upgrade local pip package to the latest version.
"""
import os


def upgrade() -> None:
    """
    Main function
    Returns:

    """
    # check current directory have dist folder
    if not os.path.exists('dist'):
        print('No dist folder found')
        return
    package_name = os.listdir('dist')[0]
    os.system(f'pip install dist/{package_name} --upgrade')


def main() -> None:
    """
    Main function
    Returns:

    """
    upgrade()
