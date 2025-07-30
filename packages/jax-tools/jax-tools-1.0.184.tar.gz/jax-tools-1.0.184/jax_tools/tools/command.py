# -*- coding: utf-8 -*-
"""
Command tool
"""
import os
import shlex
import subprocess


class Command(object):
    """
    Command tool
    """
    @staticmethod
    def exec_safety(cmd: str) -> int:
        """
        Execute command use safety method
        Args:
            cmd (str): command
        Returns:
            None
        """
        return subprocess.call(shlex.split(cmd))

    @staticmethod
    def get_output_safety(cmd: str) -> str:
        """
        Get command output use safety method
        Args:
            cmd (str): command
        Returns:
            str: command output
        """
        return subprocess.check_output(shlex.split(cmd)).decode('utf-8').rstrip()

    @staticmethod
    def exec_without_safety(cmd: str) -> int:
        """
        Execute command without safety method, suggest you validate the command before use this method
        Please Ensure the command is safe
        Args:
            cmd (str): command
        Returns:
            None
        """
        return os.system(cmd)

    @staticmethod
    def get_output_without_safety(cmd: str) -> str:
        """
        Get command output without safety method, suggest you validate the command before use this method
        Please Ensure the command is safe
        Args:
            cmd (str): command
        Returns:
            str: command output
        """
        return os.popen(cmd).read().rstrip()
