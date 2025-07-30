# -*- coding: utf-8 -*-
"""
csv to xlsx
"""

import pandas as pd
import os
import sys


def csv_to_xlsx(csv_file_path: str) -> None:
    """
    Convert a CSV file to an Excel file.
    Args:
        csv_file_path (str): The path of the CSV file.

    Returns:

    """
    # 检查文件是否存在
    if not os.path.isfile(csv_file_path):
        print(f"文件 {csv_file_path} 不存在。")
        return

    # 读取CSV文件
    try:
        df = pd.read_csv(csv_file_path, encoding='gb2312')
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return

    # 生成xlsx文件的路径
    xlsx_file_path = os.path.splitext(csv_file_path)[0] + '.xlsx'

    # 写入Excel文件
    try:
        df.to_excel(xlsx_file_path, index=False)
        print(f"成功将CSV文件转换为Excel文件: {xlsx_file_path}")
    except Exception as e:
        print(f"写入Excel文件时出错: {e}")


def mian() -> None:
    """
    Main function
    Returns:

    """
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("请提供一个CSV文件的路径作为参数。")
    else:
        csv_file_path = sys.argv[1]
        csv_to_xlsx(csv_file_path)


if __name__ == '__main__':
    mian()