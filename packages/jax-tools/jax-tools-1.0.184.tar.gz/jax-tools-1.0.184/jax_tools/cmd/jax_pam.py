#!env python3
# -*- coding:utf-8 -*-
"""
Poppy Entrypoint
"""
from jax_tools.cmd_tools.pam import PasswordManager as pm
import sys
import getpass
import subprocess
import threading
from jax_tools.utils.base import notify


def print_help() -> None:
    """
    Print Help message
    Returns:

    """
    print(u'--help 打印帮助信息')
    print(u'--list 打印账号列表')
    print(u'--delete 删除账号信息,指定账号名,如--delete account1')
    print(u'--add 添加账号信息,指定账号名')
    print(u' --get 通过NUM或账号名获取密码如 --get 1或-g 1')
    print(u'输入非上述的--开头的内容，则表示搜索账号，并将搜索到的账号的密码复制到剪贴板')


def minimize_window() -> None:
    """
    Minimize window
    Returns:

    """
    applescript = """
    tell application "System Events"
        keystroke "m" using command down
    end tell
    """
    try:
        subprocess.call(["osascript", "-e", applescript])
    except FileNotFoundError:
        pass


def update_account() -> None:
    """
    Update account
    Returns:

    """
    account_count = pm.print_account_list()
    num = int(input(u'请输入您想要更新的账号NUM(1~{} 从上方首列获取)：'.format(account_count)))
    account_info = pm.get_user_info(num)
    name = account_info.get(pm.NAME_KEY)
    username = account_info.get(pm.USERNAME_KEY)
    new_name = input(u'请输入新的账号名称(默认名称:{})：'.format(name))
    new_url = input(u'请输入新的url(默认url:{}): '.format(account_info.get(pm.URL_KEY)))
    new_username = input(u'请输入新的用户名(默认用户名{}): '.format(username))
    if not new_name:
        new_name = name
    if not new_username:
        new_username = username
    password = getpass.getpass(u'请输入登录密码或验证token: ')
    if pm.delete_account(name, print_msg=False):
        pm.add_account(new_name, new_url, new_username, password, num, print_msg=False)
        print(u'NUM:{}, name:{}更新成功'.format(num, name))


def delete_account() -> None:
    """
    Delete account
    Returns:

    """
    if len(sys.argv) > 2:
        name = ''.join(sys.argv[2:])
        pm.delete_account(name)
    else:
        name = input(u'请输入您想要删除的账号名称：')
        pm.delete_account(name)


def main() -> None:
    """
    Main Function
    Returns:

    """
    list_sign_list = ['--list', 'list', '-l']
    add_sign_list = ['add', '--add', '-a']
    help_sign_list = ['--help', '-h']
    delete_sign_list = ['--delete', 'delete', '-d']
    update_sign_list = ['--update', 'update', '-u']
    get_sign_list = ['--get', 'get', '-g']

    try:
        # If the first argument is in the list, then execute the corresponding function
        arg_1 = sys.argv[1]
        # If the first argument is in the list of list_sign_list, then print the account list
        if arg_1 in list_sign_list:
            pm.print_account_list()
        # If the first argument is in the list of help_sign_list, then print the help message
        elif arg_1 in help_sign_list:
            print_help()
        # If the first argument is in the list of add_sign_list, then add account
        elif arg_1 in add_sign_list:
            name = input(u'请输入您的要新建的账号名称(如:jenkins web root account)：')
            url = input(u'请输入您的要新建的账号的url(如:https://www.jenkins.com):')
            username = input(u'请输入你的登录用户名: ')
            password = getpass.getpass(u'请输入你的登录密码或验证token: ')
            pm.add_account(name, url, username, password, None)
        elif arg_1 in delete_sign_list:
            delete_account()
        elif arg_1 in update_sign_list:
            update_account()
        elif arg_1 in get_sign_list:
            threading.Thread(target=pm().get_password, args=(sys.argv[2],)).start()
            notify('Jax Password Manager',
                   'The content you need has been copied to the clipboard, key:{}'.format(sys.argv[2]))
        else:
            threading.Thread(target=minimize_window).start()
            threading.Thread(target=pm().get_password, args=(sys.argv[1],)).start()
            notify('Jax Password Manager',
                   'The content you need has been copied to the clipboard, key:{}'.format(sys.argv[1]))
    except IndexError:
        print_help()
    except ValueError:
        print(u'The NUM you entered is invalid, please enter a valid NUM')
    except KeyboardInterrupt:
        print(u'Quit')


if __name__ == '__main__':
    main()
