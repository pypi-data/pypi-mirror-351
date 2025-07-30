# -*- coding: utf-8 -*-
"""
An imitation of xargs command
"""
import sys
import subprocess


def main():
    if len(sys.argv) < 2:
        print("用法: xargs <command>")
        sys.exit(1)

    command = sys.argv[1:]

    # 从标准输入读取所有数据
    input_data = sys.stdin.read().strip()

    # 将输入数据作为参数
    args = input_data.split()

    # 拼接命令和参数
    full_command = command + args

    # 执行命令
    try:
        result = subprocess.run(full_command, check=True, text=True, capture_output=True)
        print(result.stdout, end="")
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
    except FileNotFoundError:
        print("找不到命令，请确保命令存在并可执行")


if __name__ == "__main__":
    main()