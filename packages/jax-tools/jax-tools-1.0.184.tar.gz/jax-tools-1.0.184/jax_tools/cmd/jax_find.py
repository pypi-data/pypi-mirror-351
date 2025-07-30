"""
Find command, imitation of find command in linux
"""

import os
import argparse


def find_files(path: str, keyword: str) -> list[str]:
    """
    Find files with keyword in path
    Args:
        path (str): path
        keyword (str): keyword
    Returns:
        List[str]: files
    """
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if keyword in filename:
                files.append(os.path.join(root, filename))
    return files


def find_dirs(path: str, keyword: str) -> list[str]:
    """
    Find dirs with keyword in path
    Args:
        path (str): path
        keyword (str): keyword
    Returns:
        List[str]: dirs
    """
    dirs = []
    for root, dir_names, _ in os.walk(path):
        for dirname in dir_names:
            if keyword in dirname:
                dirs.append(os.path.join(root, dirname))
    return dirs


def main() -> None:
    """
    Main function
    Returns:

    """
    parser = argparse.ArgumentParser(description='Find files or dirs with keyword in path')
    parser.add_argument('path', help='path')
    parser.add_argument('-n', '-name', '--name', type=str, help='keyword')
    parser.add_argument('-t', '-type', '--type', choices=['file', 'dir', 'f', 'd'], default='file', help='file or dir')
    args = parser.parse_args()
    path = args.path
    keyword = args.name.replace('*', '')
    f_type = args.type
    if f_type in ['file', 'f']:
        result = find_files(path, keyword)
    else:
        result = find_dirs(path, keyword)
    for r in result:
        print(r)


if __name__ == '__main__':
    main()
