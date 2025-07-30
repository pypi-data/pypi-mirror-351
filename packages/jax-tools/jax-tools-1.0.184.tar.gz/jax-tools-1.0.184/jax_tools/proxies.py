# -*- coding: utf-8 -*-
"""
Set proxies for requests
"""
from jax_tools.network_test import check_connectivity
from jax_tools.utils.base import KT, VT
from typing import Optional


def local_proxies(host: str = '127.0.0.1', port: int = 19999, protocol: str = 'http') -> Optional[dict[KT, VT]]:
    """
    Set proxies for requests
    Args:
        host (str): host for proxy
        port (int): port for proxy, defaults to 19999
        protocol (str): protocol for proxy, defaults to http

    Returns:
        proxies or None
    """
    enable_proxy = True
    if not enable_proxy:
        return None
    http_proxy_address = host
    http_proxy_port = port
    proxy_address = '{}://{}:{}'.format(protocol, http_proxy_address, http_proxy_port)
    if check_connectivity(http_proxy_address, http_proxy_port):
        proxies = {
            'http': proxy_address,
            'https': proxy_address,
        }
    else:
        proxies = None
    return proxies
