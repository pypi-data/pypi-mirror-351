# -*- coding: utf-8 -*-
"""
Check if the target IP and port is open
"""
import socket
import sys
from ping3 import ping
from jax_tools.colorful_font import Green
from jax_tools.colorful_font import Red
from jax_tools.colorful_font import Yellow
from jax_tools.colorful_font import ColorfulFont
from typing import Optional, Union


class PrintMSG(object):
    """
    Print message
    """
    need_print = True

    def __init__(self, msg: Union[str, ColorfulFont] = str()) -> None:
        """
        Init
        Args:
            msg : Message to print
        """
        if self.need_print:
            print(msg)


def check_icmp_connectivity(ip: str) -> bool:
    """
    Check if the target IP is reachable
    Args:
        ip(str): IP address or hostname

    Returns:
        bool: True if the target IP is reachable, False otherwise
    """
    try:
        # Use ping3 to check if the target IP is reachable
        if ping(ip):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def check_connectivity(ip: str, port: Optional[int], need_print_msg: Optional[bool] = False) -> bool:
    """
    检查目标IP和端口是否可以连接
    Args:
        ip (str): Destination IP address or hostname
        port (Optional[init]): Destination port
        need_print_msg (bool): Whether to print the result

    Returns:
        bool: True if the port is open, False if the port is closed or the connection is refused
    """
    print_msg = PrintMSG
    print_msg.need_print = need_print_msg
    # 如果没有端口，则只检查IP是否可以ping通
    if not port:
        if check_icmp_connectivity(ip):
            print_msg(Green.bold("Connection success"))
            return True
        else:
            print_msg(Red("Connection error: ping not work"))
            return False
    s = None
    network_unreachable = 'Network is unreachable'
    result_dict = {
        35: 'The port is closed',
        61: 'Connection refused, firewall restrictions may be set on the target port',
        111: 'Connection refused',
        113: 'No route to host',
        101: network_unreachable,
        110: 'Connection timed out',
        10035: network_unreachable,
        10061: 'Connection refused',
        10060: 'Connection timed out',
        10051: network_unreachable,
        10065: 'No route to host',
        10064: 'Host is down',
        10013: 'Permission denied',
        10049: 'Can\'t assign requested address'
    }
    try:
        # 创建一个socket对象
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # 设置超时时间（单位：秒）
        verify_port(port, print_msg)
        # 尝试连接到目标IP和端口
        result = s.connect_ex((ip, port))
        if result == 0:
            print_msg(Green.bold("Connection success"))
            result = True
        elif result in result_dict.keys():
            if check_icmp_connectivity(ip):
                print_msg(Red("Connection error: " + result_dict[result]))
            else:
                print_msg(Red("Connection error: " + result_dict[result] + "and ping not work"))
            result = False
        else:
            print_msg(Red("Connection error：" + str(result)))
            result = False
    except socket.error as e:
        print_msg(Red("Connection error：" + e))
        result = False
    finally:
        if s:
            s.close()
    return result


def verify_port(port: Union[str, int], print_msg: callable) -> None:
    """
    Verify if the port is valid
    Args:
        port (str): Port number
        print_msg (callable): Print message object

    Returns:
        bool: True if the port is valid, False otherwise
    """
    if isinstance(port, str):
        try:
            port = int(port)
            if port < 0 or port > 65535:
                print_msg(Yellow("The port must be between 0 and 65535"))
                sys.exit(1)
        except ValueError:
            print_msg(Yellow("The port must be a number"))
            sys.exit(1)

