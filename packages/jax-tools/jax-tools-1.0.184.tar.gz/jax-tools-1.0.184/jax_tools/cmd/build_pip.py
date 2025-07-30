# -*- coding: utf-8 -*-
"""
Build Jax Tools
"""
import os.path
import subprocess
import sys
import shutil


def update_version() -> None:
    """
    Update version
    Returns:

    """
    setup_py = 'setup.py'
    last_version = open(setup_py, 'r', encoding='utf-8').read().split('version="')[1].split('"')[0]
    last_num = int(last_version.split('.')[-1])
    new_version = '.'.join(last_version.split('.')[:-1]) + '.' + str(last_num + 1)
    with open(setup_py, 'r', encoding='utf-8') as f:
        setup_file = f.read()
    setup_file = setup_file.replace('version="{}"'.format(last_version), 'version="{}"'.format(new_version))
    with open(setup_py, 'w', encoding='utf-8') as f:
        f.write(setup_file)

    print('Update Version to {}'.format(new_version))


def build() -> None:
    """
    Build Jax Tools
    Returns:

    """
    # Delete dist folder
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    # Build
    subprocess.call('python setup.py sdist', shell=True)


def main() -> None:
    """
    Main function
    Returns:

    """
    try:
        if not sys.argv[1]:
            print("need update version")
            update_version()
    except IndexError:
        update_version()
    finally:
        build()


if __name__ == '__main__':
    main()
