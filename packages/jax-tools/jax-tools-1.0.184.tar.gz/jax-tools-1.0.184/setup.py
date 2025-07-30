# -*- coding:utf-8 -*-
"""
pypi定义打包信息的文件
"""
import setuptools


def read_file(file_path):
    """
    Read file
    Args:
        file_path (str): file path

    Returns:

    """
    with open(file_path, 'r') as f:
        return f.read()


setuptools.setup(
    name="jax-tools",
    version="1.0.184",
    author=u"Jax",
    author_email='alvin.wan.cn@hotmail.com',
    description=u"Jax common tools library",
    platforms=['CentOS', 'Redhat', 'MacOS', 'Windows'],
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    url="https://jax-arsenals.com",
    license="MIT Licence",
    python_requires=">=3.0.0",
    # 定义要构建到包中的文件列表，这些文件会放到/usr/local下
    data_files=[],
    packages=['jax_tools', 'jax_tools.utils', 'jax_tools.cmd', 'jax_tools.cmd_tools', 'jax_tools.tools', 'jax_tools.sec'],
    exclude=['upload.py'],
    package_dir={},
    package_data={
        # 'jax_tools': ['*.md'],
        '': ['CHANGELOG.md']
    },
    include_package_data=True,
    keywords=['jax'],
    # 安装时需要执行的脚本列表，如可用于管理配置文件
    scripts=[],
    download_url="https://jax-arsenals.com",
    # 定义可以为哪些模块提供依赖
    provides=[],
    install_requires=[
        "ping3 >= 4.0.4",
        "paramiko >= 3.2.0",
        "colorlog >= 6.7.0",
        "pycryptodome >= 3.18.0",
        "pyperclip >= 1.8.2",
        "psutil >= 5.9.5",
    ],
    # 定义额外的依赖, 例如win10toast,安装方式为pip install jax-tools[win10]
    extras_require={
        'win10': [
            "win10toast >= 0.9"
        ],
        'openai': ["openai == 0.27.8"],
        'python': [],
    },
    # 定义entry points, 前面的sta指的是命令，第二个sta表示模块名，也是目录名，第三个sta表示脚本名，最好那个main，表示sta.py中的main函数
    entry_points={
        'console_scripts': [
            'jax=jax_tools.cmd.jax:main',

            'nd=jax_tools.cmd.nd:main',
            'nd-jax=jax_tools.cmd.nd:main',
            'jax-nd=jax_tools.cmd.nd:main',

            'jax-encrypt=jax_tools.cmd.jax_encrypt:main',

            'jax-fix=jax_tools.cmd.jax_fix:main',

            'pam=jax_tools.cmd.jax_pam:main',
            'pam-jax=jax_tools.cmd.jax_pam:main',
            'jax-pam=jax_tools.cmd.jax_pam:main',

            'gpt=jax_tools.cmd.jax_gpt:main',
            'gpt-jax=jax_tools.cmd.jax_gpt:main',

            'build-pip=jax_tools.cmd.build_pip:main',
            'build-pip-jax=jax_tools.cmd.build_pip:main',
            'jax-build-pip=jax_tools.cmd.build_pip:main',

            'upgrade-pip=jax_tools.cmd.upgrade_pip:main',
            'upgrade-pip-jax=jax_tools.cmd.upgrade_pip:main',
            'jax-upgrade-pip=jax_tools.cmd.upgrade_pip:main',

            'install_python=jax_tools.cmd.install_python:main',

            'find-jax=jax_tools.cmd.jax_find:main',

            'tail-jax=jax_tools.cmd.jax_tail:main',

            'xargs-jax=jax_tools.cmd.jax_xargs:main',
        ]
    }
)
