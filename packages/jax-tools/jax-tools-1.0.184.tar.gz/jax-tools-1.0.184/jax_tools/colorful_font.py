# -*- coding: utf-8 -*-
"""
Colorful Log Process
"""
import time
from typing import Union


class ColorfulFont(object):
    """
    Colored Font
    """
    STYLE_NORMAL = 0
    STYLE_BOLD = 1
    STYLE_UNDERLINE = 4
    STYLE_INVERSE = 7
    STYLE_BLINK = 5

    COLOR_CYANIC = 36
    COLOR_RED = 31
    COLOR_GREEN = 32
    COLOR_YELLOW = 33
    COLOR_FUCHSIA = 35
    COLOR_NORMAL = 39

    color_num = COLOR_NORMAL

    def __new__(cls, msg: str, color_num: Union[int] = None) -> str:
        """
        New instance
        Args:
            msg (str): Message text.
            color_num (int): color number
        Returns
            str: Colored text.
        """
        color_num = color_num or cls.color_num
        return cls.text(msg, color_num)

    @classmethod
    def text(cls, msg: str, color_num: Union[int] = None) -> str:
        """
        Get colored text with the given message and color number.

        Args:
            msg (str): Message text.
            color_num (int, optional): Color number. If not provided, the default color number of the class will be used

        Returns:
            str: Colored text.
        """
        color_num = color_num or cls.color_num
        return cls.colorful_text(cls.STYLE_NORMAL, color_num, msg)

    @classmethod
    def bold(cls, msg: str, color_num: Union[int] = None) -> str:
        """
        Get bold colored text with the given message and color number.

        Args:
            msg (str): Message text.
            color_num (int, optional): Color number. If not provided, the default color number of the class will be used

        Returns:
            str: Bold colored text.
        """
        color_num = color_num or cls.color_num
        return cls.colorful_text(cls.STYLE_BOLD, color_num, msg)

    @classmethod
    def blink(cls, msg: str, color_num: Union[int] = None) -> str:
        """
        Get blink colored text with the given message and color number.

        Args:
            msg (str): Message text.
            color_num (int, optional): Color number. If not provided, the default color number of the class will be used

        Returns:
            str: Blink colored text.
        """
        color_num = color_num or cls.color_num
        return cls.colorful_text(cls.STYLE_BLINK, color_num, msg)

    @classmethod
    def underline(cls, msg: str, color_num: Union[int] = None) -> str:
        """
        Get underlined colored text with the given message and color number.

        Args:
            msg (str): Message text.
            color_num (int, optional): Color number. If not provided, the default color number of the class will be used

        Returns:
            str: Underlined colored text.
        """
        color_num = color_num or cls.color_num
        return cls.colorful_text(cls.STYLE_UNDERLINE, color_num, msg)

    @classmethod
    def inverse(cls, msg: str, color_num: Union[int] = None) -> str:
        """
        Get inversely colored text with the given message and color number.

        Args:
            msg (str): Message text.
            color_num (int, optional): Color number. If not provided, the default color number of the class will be used

        Returns:
            str: Inversely colored text.
        """
        color_num = color_num or cls.color_num
        return cls.colorful_text(cls.STYLE_INVERSE, color_num, msg)

    @classmethod
    def colorful_text(cls, style: int, color: int, msg: str) -> str:
        """
        Colorful text

        Args:
            style (int): Text style. Possible values: cls.STYLE_NORMAL, cls.STYLE_BOLD, cls.STYLE_UNDERLINE,
                          cls.STYLE_INVERSE.
            color (int): Color number. Possible values: cls.COLOR_CYANIC, cls.COLOR_RED, cls.COLOR_GREEN,
                             cls.COLOR_YELLOW, cls.COLOR_FUCHSIA, cls.COLOR_NORMAL.
            msg (str): Message text.

        Returns:
            str: Colorful text.
        """
        return '\033[{0};33;{1}m{2}\033[0m'.format(style, color, msg)


class Cyanic(ColorfulFont):
    """
    Cyanic colored font
    """
    color_num = ColorfulFont.COLOR_CYANIC


class Red(ColorfulFont):
    """
    Red colored font
    """
    color_num = ColorfulFont.COLOR_RED


class Green(ColorfulFont):
    """
    Green colored font
    """
    color_num = ColorfulFont.COLOR_GREEN


class Yellow(ColorfulFont):
    """
    Yellow Colored font
    """
    color_num = ColorfulFont.COLOR_YELLOW


class Fuchsia(ColorfulFont):
    """
    Fuchsia Colored Font
    """
    color_num = ColorfulFont.COLOR_FUCHSIA


class Normal(ColorfulFont):
    """
    Normal Colored Font
    """
    color_num = ColorfulFont.COLOR_NORMAL


def bold_msg(color: int, msg: str) -> str:
    """
    Return a bold colorful message.

    Args:
        color (int): The color code or name.
        msg (str): The message to be formatted.

    Returns:
        str: The formatted message with bold and color.

    """
    return '\033[1;36;{0}m{1}\033[0m'.format(color, msg)

def blink_msg(color: int, msg: str) -> str:
    """
    Return a blink colorful message.

    Args:
        color (int): The color code or name.
        msg (str): The message to be formatted.

    Returns:
        str: The formatted message with blink and color.

    """
    return '\033[5;36;{0}m{1}\033[0m'.format(color, msg)


class GetColor(ColorfulFont):
    """
    Get Font Color
    """

    @classmethod
    def score(cls, s: Union[float, str]) -> int:
        """
        Get color based on the score value.

        Args:
            s (float or str): Score value.

        Returns:
            int: Color code based on the score value.
        """
        if s == '':
            response = cls.COLOR_NORMAL
        else:
            s = float(s)
            if s > 9.0:
                response = cls.COLOR_FUCHSIA
            elif s > 7.0:
                response = cls.COLOR_RED
            elif s > 4.0:
                response = cls.COLOR_YELLOW
            elif s > 0:
                response = cls.COLOR_GREEN
            else:
                response = cls.COLOR_NORMAL
        return response

    @classmethod
    def date(cls, d: str) -> int:
        """
        Get color based on the date.

        Args:
            d (str): Date string.

        Returns:
            int: Color code based on the date.
        """
        if not d.count('-'):
            return cls.COLOR_NORMAL
        year = int(d.split('-')[0])
        now_year = int(time.strftime('%Y'))
        if year >= now_year:
            response = cls.COLOR_FUCHSIA
        elif year >= now_year - 1:
            response = cls.COLOR_RED
        elif year >= now_year - 3:
            response = cls.COLOR_YELLOW
        else:
            response = cls.COLOR_NORMAL
        return response


if __name__ == '__main__':
    print(Red.underline('Cyanic'))
    print(Yellow.bold('Red'))
    print(GetColor.score(9.5))
    print(ColorfulFont.colorful_text(ColorfulFont.STYLE_NORMAL, GetColor.score(6.5), '6.5 score'))
    print(bold_msg(GetColor.score(2.5), '2.5 score'))
    print(bold_msg(GetColor.date('2020-01-01'), '2020-01-01'))
    print(bold_msg(GetColor.date('2023-01-01'), '2023-01-01'))
    print(bold_msg(GetColor.date('2019-01-01'), '2019-01-01'))
    print(Yellow('hello'))
    print(Yellow.text('hello'))
    print(Red.bold('hello'))
