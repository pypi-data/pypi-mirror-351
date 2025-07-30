# -*- coding: utf-8 -*-
"""
Install python3, script compatible with CentOS 7 python2
"""
import subprocess, os
import sys


def install_python(version='3.9.13'):
    """
    Install python3.9.13
    Args:
        version (str): version

    Returns:

    """
    # if python3 already exist, tell user
    if os.path.exists('/usr/bin/python3'):
        print('python3 is exist already. we will continue to install python{0} to /usr/local/python{0}'.format(version))
    # Install python dependents
    subprocess.call('yum install gcc zlib zlib-devel libffi-devel openssl-devel -y', shell=True)
    # Enter /tmp directory
    os.chdir('/tmp')
    # Download python3.9.13.tar.xz, compatibility if file exist
    if not os.path.exists('/tmp/python{}.tar.xz'.format(version)):
        print('Downloading python{}.tar.xz'.format(version))
        subprocess.call('curl -fsSL https://www.python.org/ftp/python/{}/Python-{}.tar.xz > python{}.tar.xz'.format(
            version, version, version), shell=True)
    # Extract pythonx.x.xx.tar.xz
    subprocess.call('tar xf python{}.tar.xz -C /usr/local/src/'.format(version), shell=True)
    # Enter /usr/local/src/Python-x.x.x/
    os.chdir('/usr/local/src/Python-{}/'.format(version))
    # Configure pythonx.x.xx
    subprocess.call('./configure --prefix=/usr/local/python{}'.format(version), shell=True)
    # Make and make install
    subprocess.call('make', shell=True)
    subprocess.call('make install', shell=True)
    # Modify pythonx.x.xx
    subprocess.call("sed -i '210,212s/#//' /usr/local/src/Python-{}/Modules/Setup".format(version), shell=True)
    subprocess.call("sed -i '205s/#//' /usr/local/src/Python-{}/Modules/Setup".format(version), shell=True)
    # Make and make install
    subprocess.call('make', shell=True)
    subprocess.call('make install', shell=True)
    # Create soft link
    print('python{} has been installed successfully'.format(version))
    print('You can find python{0} at /usr/local/python{0}/bin/'.format(version))
    if os.path.exists('/usr/bin/python3'):
        print('/usr/bin/python3 is exist already. if you want to replace it, you can use command as this: '
              'mv /usr/bin/python3 /usr/bin/python3_bakup;ln -s /usr/local/python{0}/bin/python3 /usr'
              '/bin/;python3 --version'.format(version))
    print('Current python3 version is: ')
    subprocess.call('python3 --version', shell=True)


def main():
    """
    Main function
    Returns:

    """
    try:
        version = sys.argv[1]
        if not int(version.replace('.', '')):
            print('Invalid version number')
            exit()
    except IndexError:
        version = '3.9.13'
    except ValueError:
        print('Invalid version number')
        exit()
    install_python(version)
