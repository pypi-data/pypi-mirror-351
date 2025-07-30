"""
This module provides a function to get the CPU and memory usage of all processes running on the system.
"""
import platform
import psutil
from typing import TypeVar
KT = TypeVar('KT')
VT = TypeVar('VT')


def get_process_info() -> list[dict[str, VT]]:
    """
    Get process info
    Returns:

    """
    processes = []
    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(process.info)
    return processes


def print_process_info() -> None:
    """
    Print process info
    Returns:

    """
    processes = get_process_info()
    filtered_processes = [process for process in processes if process['cpu_percent'] is not None]
    sorted_processes = sorted(filtered_processes, key=lambda x: x['cpu_percent'], reverse=True)
    print("PID\tCPU%\tMemory%\tName")
    for process in sorted_processes:
        print(f"{process['pid']}\t{process['cpu_percent']}\t{process['memory_percent']}\t{process['name']}")


def main() -> None:
    """
    Main function
    Returns:

    """
    system = platform.system()
    if system == 'Linux' or system == 'Darwin':
        print_process_info()
    else:
        print("Unsupported operating system.")


if __name__ == '__main__':
    main()
