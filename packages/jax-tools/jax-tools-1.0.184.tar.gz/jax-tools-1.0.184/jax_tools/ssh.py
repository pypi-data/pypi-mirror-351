# -*- coding: utf-8 -*-
"""
ssh operations
"""
import os.path

import paramiko
from jax_tools.logger import logger
from typing import Optional
import base64
import shlex


class SSHClient(object):
    """
    SSH Connector
    """
    SSH_CONNECTION_FAILED = 'SSH connection failed'

    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        """
        SSH Connector
        Args:
            host (str): host for ssh connection
            port (int): port for ssh connection
            username (str): username for ssh connection
            password (str): password for ssh connection
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh_client = self.__get_ssh_client()

    def __get_ssh_client(self) -> Optional[paramiko.SSHClient]:
        """
        Get ssh client
        Args:

        Returns:
            ssh client or None

        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        response = True
        try:
            client.connect(
                self.host,
                self.port,
                username=str(self.username),
                password=str(self.password),
                timeout=10)
        except paramiko.ssh_exception.AuthenticationException:
            logger.error('authentication failed')
            response = None
        except paramiko.ssh_exception.NoValidConnectionsError:
            logger.error('can not connect to host')
            response = None
        except Exception as e:
            logger.error(e)
            response = None
        if response:
            return client
        else:
            return response

    def run_cmd(self, cmd: str, time_out: int = 300) -> [int]:
        """
        Run command on remote host
        Args:
            cmd (str): command to run
            time_out (int): timeout in seconds

        Returns:
            int: command running result. 0 for success, non-zero for failure
        """
        result = 1
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return result
        try:
            _std_in, std_out, _std_err = self.ssh_client.exec_command(cmd, timeout=time_out)
            exit_status = std_out.channel.recv_exit_status()
            result = 0 if exit_status == 0 else exit_status
        except Exception as e:
            logger.error('Connection exception, User login info may be wrong, or connection has been closed, '
                         ' msg: %s' % e)
            result = 1
        return result

    def run_cmd_safety(self, cmd: str, time_out: int = 300) -> Optional[int]:
        """
        Run command on remote host
        Args:
            cmd (str): command to run
            time_out (int): timeout in seconds

        Returns:
            int: command running result. 0 for success, non-zero for failure
        """
        result = None
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return result
        try:
            # Use shlex to sanitize the command
            sanitized_cmd = shlex.quote(cmd)
            _std_in, std_out, _std_err = self.ssh_client.exec_command(sanitized_cmd, timeout=time_out)
            exit_status = std_out.channel.recv_exit_status()
            result = exit_status
        except Exception as e:
            logger.error('Connection exception, User login info may be wrong, or connection has been closed, '
                         ' msg: %s' % e)
            result = 1
        return result

    def get_cmd_result(self, cmd: str, read_line: bool = False, time_out: int = 300) -> Optional[str]:
        """
        Run command on remote host
        Args:
            cmd (str): command to run
            read_line (bool): True if read line by line, False if read all
            time_out (int): timeout in seconds

        Returns:
            String if read_line is False

        """
        result = None
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return result
        try:
            _std_in, std_out, _std_err = self.ssh_client.exec_command(cmd, timeout=time_out)
            if read_line:
                result = std_out.readlines()
            else:
                result = std_out.read().decode('utf-8').rstrip()
        except Exception as e:
            logger.error('Connection exception when get cmd output, User login info may be wrong, or connection'
                         ' has been closed, msg: %s' % e)
        return result

    def get_cmd_result_safety(self, cmd: str, read_line: bool = False, time_out: int = 300) -> Optional[str]:
        """
        Run command on remote host
        Args:
            cmd (str): command to run
            read_line (bool): True if read line by line, False if read all
            time_out (int): timeout in seconds

        Returns:
            String if read_line is False

        """
        result = None
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return result
        try:
            # Use shlex to sanitize the command
            sanitized_cmd = shlex.quote(cmd)
            _std_in, std_out, _std_err = self.ssh_client.exec_command(sanitized_cmd, timeout=time_out)
            if read_line:
                result = std_out.readlines()
            else:
                result = std_out.read().decode('utf-8').rstrip()
        except Exception as e:
            logger.error('Connection exception when get cmd output, User login info may be wrong, or connection'
                         ' has been closed, msg: %s' % e)
        return result

    def put_file(self, local_file: str, remote_file: str) -> None:
        """
        Put file to remote host
        Args:
            local_file (str): local file path
            remote_file (str): remote file path

        Returns:

        """
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return
        if not os.path.exists(local_file):
            logger.warning('Local file not exists')
            return
        try:
            with open(local_file, 'rb') as f:
                file_content = f.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')
                self.run_cmd('echo "{}" | base64 --decode > {}'.format(encoded_content, remote_file))
        except Exception as e:
            logger.error('Got exception in put file to remote server: %s' % e)

    def get_file(self, remote_file: str, local_file: str) -> None:
        """
        Get file from remote host
        Args:
            remote_file (str): remote file path
            local_file (str): local file path

        Returns:

        """
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return
        try:
            file_content = self.run_cmd('cat {}'.format(remote_file))
            if file_content:
                with open(local_file, 'w') as f:
                    f.write(file_content)
        except Exception as e:
            logger.error('Got exception in get file from remote server: %s' % e)

    def sftp_put_file(self, local_file: str, remote_file: str) -> None:
        """
        Put file to remote host using sftp
        Args:
            local_file (str): local file path
            remote_file (str): remote file path

        Returns:

        """
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return
        try:
            sftp_client = self.ssh_client.open_sftp()
            sftp_client.put(local_file, remote_file)
        except Exception as e:
            logger.error('Connection exception, User login info may be wrong, or connection has been closed, '
                         ' msg: %s' % e)

    def sftp_get_file(self, remote_file: str, local_file: str) -> None:
        """
        Get file from remote host using sftp
        Args:
            remote_file (str): remote file path
            local_file (str): local file path

        Returns:

        """
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return
        try:
            sftp_client = self.ssh_client.open_sftp()
            sftp_client.get(remote_file, local_file)
        except Exception as e:
            logger.error('Connection exception, User login info may be wrong,  msg: %s' % e)

    def scp(self, local_file: str, remote_file: str) -> None:
        """
        Copy file to remote host using scp
        Args:
            local_file (str): local file path
            remote_file (str): remote file path

        Returns:

        """
        if self.ssh_client is None:
            logger.warning(self.SSH_CONNECTION_FAILED)
            return
        try:
            scp = paramiko.Transport((self.host, self.port))
            scp.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(scp)
            sftp.put(local_file, remote_file)
            scp.close()
        except Exception as e:
            logger.error('Connection exception, User login info may be wrong,  msg: %s' % e)

    def close(self) -> None:
        """
        Close ssh connection
        Returns:

        """
        self.ssh_client.close()

    def __del__(self) -> None:
        if self.ssh_client:
            self.close()

