# -*- coding: utf-8 -*-
"""
模拟 tail -f 命令
"""
import time
import sys


def tail_f(filename: str) -> None:
    """
    tail -f
    Args:
        filename (str): filename

    Returns:

    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # 先打印最后10行
            lines = file.readlines()
            last_lines = lines[-10:]
            # 打印最后10行
            for line in last_lines:
                print(line, end='')
            file.seek(0, 2)  # 把文件指针移动到文件末尾
            while True:
                line = file.readline()  # 读取新行
                if not line:
                    time.sleep(0.1)  # 没有新内容就稍微休息一下
                    continue
                print(line, end='')  # 打印新行
    except FileNotFoundError:
        print(f"文件 '{filename}' 不存在，请确认路径和文件名！")
    except KeyboardInterrupt:
        print("\n程序被终止了，拜拜~")
    except Exception as e:
        print(f"发生了一些意想不到的错误：{e}")


def tail(filename: str, lines: int) -> None:
    """
    tail -n
    Args:
        filename (str): filename
        lines (int): number of lines to display from the end

    Returns:

    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # 打印最后N行
            all_lines = file.readlines()
            last_lines = all_lines[-lines:]
            for line in last_lines:
                print(line, end='')
    except FileNotFoundError:
        print(f"文件 '{filename}' 不存在，请确认路径和文件名！")
    except Exception as e:
        print(f"发生了一些意想不到的错误：{e}")


def main() -> None:
    """
    Main function
    Returns:

    """
    if len(sys.argv) < 3:
        print("用法: python tail.py -f 文件名 或 python tail.py -n 行数 文件名")
    else:
        option = sys.argv[1]
        if option == '-f':
            tail_f(sys.argv[2])
        elif option == '-n' and len(sys.argv) == 4:
            lines = int(sys.argv[2])
            filename = sys.argv[3]
            tail(filename, lines)
        else:
            print("用法: python tail.py -f 文件名 或 python tail.py -n 行数 文件名")


if __name__ == "__main__":
    main()
