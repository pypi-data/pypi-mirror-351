#! env python3
# -*- coding:utf-8 -*-
"""
Password Manager
"""
import json
import os
import pyperclip
import sys
from jax_tools.encrypt import AESCipher
from jax_tools.utils.settings import JAX_DATA_DIR
from typing import Optional, TypeVar

# 导入_KT _VT
_KT = TypeVar('_KT')
_VT = TypeVar('_VT')


class PasswordManager(object):
    """
    Password Manager
    """
    # Define pam data file
    data_file = os.path.join(JAX_DATA_DIR, '.pam.json')
    if os.path.exists(data_file):
        data_list = json.loads(open(data_file, 'r').read())
    else:
        data_list = list()

    # Define string
    NAME_KEY = 'name'
    URL_KEY = 'url'
    USERNAME_KEY = 'username'
    PASSWORD_KEY = 'password'
    DUPLICATE_ACCOUNT = u'The account name you entered already exists, please enter a new account name'

    def get_password(self, search_str: '') -> None:
        """
        Get password by search string and copy to clipboard
        Args:
            search_str: Search string

        Returns: password

        """
        # If search string is integer, get password by num
        try:
            pyperclip.copy(self.__get_pw_by_num(int(search_str)))
        # If search string is not integer, get password by name
        except ValueError:
            pw = self.__search_by_equal(search_str)
            if pw:
                pyperclip.copy(pw)
            elif self.__search_by_start(search_str):
                pyperclip.copy(self.__search_by_start(search_str))
            else:
                pyperclip.copy(self.__search_by_contains(search_str))

    def __search_by_start(self, search_str: str) -> str:
        """
        Search by start
        Args:
            search_str (str): Search string

        Returns:

        """
        # Reverse data list
        for encrypted_pw_info in self.data_list:
            # Decrypt password info
            pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
            # Get account name
            name = pw_info.get(self.NAME_KEY)
            # If name equals search string, copy password to clipboard
            if name.startswith(search_str):
                return pw_info.get(self.PASSWORD_KEY)
        return str()

    def __search_by_contains(self, search_str: str) -> str:
        """
        Search by contains
        Args:
            search_str (str): Search string

        Returns:

        """
        # Reverse data list
        for encrypted_pw_info in self.data_list:
            # Decrypt password info
            pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
            # Get account name
            name = pw_info.get(self.NAME_KEY)
            # If name equals search string, copy password to clipboard
            if name.__contains__(search_str):
                return pw_info.get(self.PASSWORD_KEY)
        return str()

    def __get_pw_by_num(self, num: int) -> str:
        """
        Get password by num
        Args:
            num (int): Num

        Returns:

        """
        try:
            encrypted_pw_info = self.data_list[num - 1]
        except IndexError:
            print('Jax Remind: The account number you entered does not exist')
            sys.exit(1)
        pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
        return pw_info.get(self.PASSWORD_KEY)

    def __search_by_equal(self, search_str: str) -> str:
        """
        Search by equal
        Args:
            search_str (str): Search string

        Returns:

        """
        # Reverse data list
        for encrypted_pw_info in self.data_list:
            # Decrypt password info
            pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
            # Get account name
            name = pw_info.get(self.NAME_KEY)
            # If name equals search string, copy password to clipboard
            if name == search_str:
                return pw_info.get(self.PASSWORD_KEY)
        return str()

    @classmethod
    def print_account_list(cls) -> int:
        """
        Print account list
        Returns:

        """
        # Define max length
        max_name_len = 4
        max_username_len = 8
        max_url_len = 12
        min_serial_len = 3
        max_serial_len = len(str(len(cls.data_list)))
        space_len = 2
        # Compare max and min serial length
        if max_serial_len < min_serial_len:
            max_serial_len = min_serial_len
        # Traverse encrypted account list
        for encrypted_pw_info in cls.data_list:
            # Decrypt account information
            pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
            # Get account name and username
            name = pw_info.get(cls.NAME_KEY)
            username = pw_info.get(cls.USERNAME_KEY)
            url = pw_info.get(cls.URL_KEY, str())
            # Compare max length
            if len(name) > max_name_len:
                max_name_len = len(name)
            if len(username) > max_username_len:
                max_username_len = len(username)
            if len(url) > max_url_len:
                max_url_len = len(url)
        head_and_tail_str = '+' + '-' * (max_serial_len + space_len) + '+' + '-' * (
                max_name_len + space_len) + '+' + '-' * (max_url_len + space_len) + '+' + '-' * (
                                    max_username_len + space_len) + '+'
        print('Jax Remind: You have {} accounts'.format(len(cls.data_list)))
        print('Use "jax-pam NUM" to get the password for the specified NUM to the clipboard， exp: jax-pam 6,'
              ' then you can paste the password to the specified location')
        print(head_and_tail_str)
        print(
            f'| {"NUM".ljust(max_serial_len)} | {"NAME".ljust(max_name_len)} | {"URL".ljust(max_url_len)} | '
            f'{"USERNAME".ljust(max_username_len)} |'
        )
        print(head_and_tail_str)
        for encrypted_pw_info in cls.data_list:
            pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
            name = pw_info.get(cls.NAME_KEY)
            url = pw_info.get(cls.URL_KEY, str())
            username = pw_info.get(cls.USERNAME_KEY)
            serial_num = cls.data_list.index(encrypted_pw_info) + 1
            print(
                f'| {str(serial_num).ljust(max_serial_len)} '
                f'| {name.ljust(max_name_len)} '
                f'| {url.ljust(max_url_len)} '
                f'| {username.ljust(max_username_len)} |')
        print(head_and_tail_str)
        return len(cls.data_list)

    @classmethod
    def get_user_info(cls, num: int) -> dict[_KT, _VT]:
        """
        Get user info by num
        Args:
            num (int): user num

        Returns:

        """
        encrypted_pw_info = cls.data_list[num - 1]
        pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
        return pw_info

    @classmethod
    def delete_account(cls, name: str, print_msg: bool = True) -> bool:
        """
        Delete account
        Args:
            name: Account name
            print_msg: Print message

        Returns:

        """
        for encrypted_pw_info in cls.data_list:
            pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
            account_name = pw_info.get(cls.NAME_KEY)
            if name == account_name:
                cls.data_list.remove(encrypted_pw_info)
                # dump account list to json
                data_json = json.dumps(cls.data_list)
                # write to data file
                open(cls.data_file, 'w').write(data_json)
                # Print finally message
                if print_msg:
                    print(f'Account {name} has been deleted successfully')
                return True
        print(f'Account {name} not found, if your account information contains spaces, please wrap the complete ')
        return False

    @classmethod
    def add_account(cls, name: str, url: str, username: str, password: str, num: Optional[int],
                    print_msg: bool = True) -> None:
        """
        Add Account to data file
        Args:
            name: Account name
            url: Account url
            username: Username
            password: Password
            num: Num of account
            print_msg: Print message

        Returns:

        """
        # Traverse encrypted account list
        for encrypted_pw_info in cls.data_list:
            # Get account information
            pw_info = json.loads(AESCipher().decrypt(encrypted_pw_info))
            account_name = pw_info.get(cls.NAME_KEY)
            # If new name is duplicate with exist name, return and print a message
            if name == account_name:
                print(cls.DUPLICATE_ACCOUNT)
                return
        # Define account information use a dict
        account_info = {cls.NAME_KEY: name, cls.URL_KEY: url, cls.USERNAME_KEY: username, cls.PASSWORD_KEY: password}
        # Define encrypted account information
        encrypted_account_info = AESCipher().encrypt(json.dumps(account_info))
        # Add new account to account list
        if num:
            cls.data_list.insert(num - 1, encrypted_account_info)
        else:
            cls.data_list.append(encrypted_account_info)
        # dump account list to json
        data_json = json.dumps(cls.data_list)
        # write to data file
        open(cls.data_file, 'w', encoding='utf-8').write(data_json)
        # Print finally message
        if print_msg:
            print(f'The account {name} has been added successfully')


if __name__ == '__main__':
    try:
        PasswordManager().get_password(sys.argv[1])
    except IndexError:
        print(PasswordManager().get_user_info(2))
