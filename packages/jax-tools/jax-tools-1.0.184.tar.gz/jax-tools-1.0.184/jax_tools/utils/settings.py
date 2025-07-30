# -*- coding: utf-8 -*-
"""
utils
"""
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_DIR = os.path.expanduser('~')
JAX_DATA_DIR = os.path.join(HOME_DIR, '.jax')
JAX_KEY_FILE = os.path.join(JAX_DATA_DIR, '.jax_key')
