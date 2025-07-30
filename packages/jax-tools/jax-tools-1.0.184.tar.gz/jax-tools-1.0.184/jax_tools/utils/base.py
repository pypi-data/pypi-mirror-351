# -*- coding:utf-8 -*-
"""
utils base
"""
from typing import TypeVar
import re
import sys
import subprocess
try:
    from win10toast import ToastNotifier
except ImportError:
    ToastNotifier = None

KT = TypeVar('KT')
VT = TypeVar('VT')


def sanitize_input(input_string: str, safe_str_list: tuple[str] = ()) -> str:
    """
    Sanitizes an input string by escaping potentially dangerous characters.

    Args:
        input_string (str): The string to be sanitized.
        safe_str_list (tuple): A list of strings that should not be removed.

    Returns:
        str: The sanitized string.
    """
    # 定义特殊字符
    special_str = r'[ ;|&`\'\"*?~<>^()[\]{}$\\!@#%+=\-/.,:]'
    for safe_str in safe_str_list:
        special_str = special_str.replace(safe_str, '')
    # 移除或转义特殊字符
    sanitized = re.sub(special_str, '', input_string)
    return sanitized


def chinese_double_length(string: str) -> int:
    """
    Get string length, chinese double length
    Args:
        string (str): string for calculate length

    Returns:
        int: string length
    """
    length = 0
    for char in string:
        if ord(char) > 127:  # 如果字符的ASCII码大于127，则认为是中文字符
            length += 2
        else:
            length += 1
    return length


def get_input(prompt: str) -> str:
    """
    Get input from user with a prompt.
    Args:
        prompt (str): The prompt to display to the user.

    Returns:

    """
    sys.stdout.write(prompt)
    sys.stdout.flush()
    input_string = ''
    try:
        import termios
        old_settings = termios.tcgetattr(sys.stdin)
    except ModuleNotFoundError:
        return input(prompt)
    try:
        import tty
        tty.setcbreak(sys.stdin.fileno())
        while True:
            char = sys.stdin.read(1)
            if char == '\r' or char == '\n':
                sys.stdout.write('\n')
                return input_string
            # Backspace character
            elif char == '\x08':
                if len(input_string) > 0:
                    input_string = input_string[:-1]
                    # Move cursor back and erase character
                    sys.stdout.write('\b \b')
            else:
                input_string += char
                sys.stdout.write(char)
            sys.stdout.flush()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def notify(title: str='Jax Notice', message: str="Jax Notice", duration: int=1) -> None:
    """
    Notify
    Args:
        title (str): title of notify
        message (str): message to notify
        duration (int): duration of notify

    Returns:
    """
    applescript = f'display notification "{message}" with title "{title}"'
    # If you want to use this function, you need to install terminal-notifier
    try:
        # try to use terminal-notifier
        subprocess.call(['osascript', '-e', applescript])
    except (FileNotFoundError, TypeError):
        pass  # 忽略异常

    try:
        toaster = ToastNotifier()
        # 发送通知
        toaster.show_toast(title, message, duration=duration)
    # If you want to use this function, you need to install win10toast, Mac OS does not support this function
    except (FileNotFoundError, AttributeError, TypeError):
        pass  # 忽略异常


if __name__ == '__main__':
    print(sanitize_input('test\ !@_#$%^&*()_+=-][\';/.,?>":}{\|"?',('+-')))
    notify('hello world','hello world')