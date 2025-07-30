# -*- coding: utf-8 -*-
"""
Logger module
"""
import logging.config
import colorlog

# 定义 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 定义日志处理器
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# 创建日志格式
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    log_colors={
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
    }
)

stream_handler.setFormatter(formatter)

# 添加日志处理器到 logger
logger.addHandler(stream_handler)

# 定义新的 logger_details
logger_details = logging.getLogger('details')
logger_details.setLevel(logging.DEBUG)

# 定义新的日志处理器
details_handler = logging.StreamHandler()
details_handler.setLevel(logging.DEBUG)

# 定义新的日志格式，包括脚本名和行号
details_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s[%(lineno)d] %(message)s',
                                      '%Y-%m-%d %H:%M:%S')
details_handler.setFormatter(details_formatter)

# 添加新的日志处理器到 logger_details
logger_details.addHandler(details_handler)

# 定义新的 logger_details
logger_time = logging.getLogger('time')
logger_time.setLevel(logging.DEBUG)

# 定义新的日志处理器
time_handler = logging.StreamHandler()
time_handler.setLevel(logging.DEBUG)

# 定义新的日志格式，包括脚本名和行号
time_formatter = logging.Formatter('%(asctime)s %(message)s', '%H:%M:%S')
time_handler.setFormatter(time_formatter)

# 添加新的日志处理器到 logger_time
logger_time.addHandler(time_handler)

# 定义一个不带颜色日志格式
formatter_normal = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


def logger_to_file(filename: str, need_print: bool = True) -> logging.Logger:
    """
    将日志输出到指定文件
    Args:
        filename: 日志文件名
        need_print: 是否同时输出到屏幕
    Returns
        logger: 日志对象
    """
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter_normal)
    logger.addHandler(file_handler)
    if not need_print:
        logger.removeHandler(stream_handler)
    return logger


def func_logger(func_desc: str = str(), debug_mode: bool = False) -> callable:
    """
    装饰器，用于打印函数名称
    Args:
        func_desc (str): Function description
        debug_mode (bool): Debug mode, default is False
    Returns:
        wrapper: 装饰后的函数
    """

    def decorator(func: callable) -> callable:
        """
        装饰器函数
        Args:
            func (callable): 被装饰的函数

        Returns:

        """

        def wrapper(*args, **kwargs) -> None:
            """
            包装函数
            Args:
                *args (Any): Arguments
                **kwargs (Any): Arguments

            Returns:

            """
            # Define default logger level
            _logger = logger.info
            # If debug mode is True, set logger level to debug
            if debug_mode:
                _logger = logger.debug
            _logger(f'Start {func_desc}')
            result = func(*args, **kwargs)
            _logger(f'Completed {func_desc}')
            return result

        return wrapper

    return decorator


if __name__ == '__main__':
    logger.debug('this is a debug message')
    logger.info('this is a info message')
    logger.warning('this is a warning message')
    logger.error('this is a error message')
