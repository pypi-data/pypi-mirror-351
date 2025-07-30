# -*- coding:utf-8 -*-
"""
ask gpt
"""
import logging
import os
from jax_tools.logger import logger

import openai
from jax_tools.encrypt import AESCipher
from typing import TypeVar
import sys

_KT = TypeVar('_KT')
_VT = TypeVar('_VT')


def interact_ask_gpt() -> None:
    """
    Ask question to GPT-4
    Returns:

    """
    question_queue = [{"role": "system", "content": "你是智能AI，你叫贾克斯。"}]
    # Confirm openai key file exists
    openai_key_file = os.path.join(os.path.expanduser('~'), '.jax', '.openai.key')
    if not os.path.exists(openai_key_file):
        print('OpenAI key file not found, please create it first, use jax-encrypt -e YOUR_OPENAI_KEY '
              'to generate a encrypted key and add it to {}'.format(openai_key_file))
        exit(0)
    try:
        while True:
            question = input('请输入问题：')
            if question in ['exit', 'quit', 'q', '']:
                print("本次会话结束，再见！")
                exit(0)
            question_queue.append({"role": "user", "content": question})
            question_queue = handle_question_length(question_queue)
            answer = ask_gpt(question_queue)
            question_queue += [{"role": "assistant", "content": answer}]
            print()
    except KeyboardInterrupt:
        print("本次会话结束，再见！")
        exit(0)


def handle_question_length(question: list[_VT]) -> list[_VT]:
    """
    Handle question length
    Args:
        question (list): Question

    Returns:
        list

    """
    max_allow_length = 2200
    while True:
        if len(str(question)) > max_allow_length and len(question) > 3:
            del question[1]
        else:
            break
    return question


def ask_gpt(question_queue: list[_VT]) -> str:
    """
    Ask question to GPT-4
    Args:
        question_queue (list[_VT]): Question queue, example: [{"role": "system", "content": "你是智能AI，你叫贾克斯。
        "},{"role": "user", "content": "你好"}]

    Returns:

    """
    http_proxy = 'http://127.0.0.1:10809'
    os.environ['http_proxy'] = http_proxy
    os.environ['https_proxy'] = http_proxy
    openai_key_file = os.path.join(os.path.expanduser('~'), '.jax', '.openai.key')
    if not os.path.exists(openai_key_file):
        print('OpenAI key file not found, please create it first, the key file path is: {}'.format(openai_key_file))
    openai_key = AESCipher().decrypt(open(openai_key_file).read())
    # 设置API密钥
    openai.api_key = openai_key
    # 调用OpenAI API并使用流式处理接收响应
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=question_queue,
        stream=True
    )
    # Define a variable to store the response
    message = str()
    for chunk in response:
        for char in chunk['choices'][0]['delta'].get('content', ''):
            print(char, end='')
            message += char
            sys.stdout.flush()
    return message


def main() -> None:
    """
    Main
    Returns:

    """
    interact_ask_gpt()


if __name__ == '__main__':
    # main()
    question_queue = [{"role": "system", "content": "你是智能AI，你叫贾克斯。"}]
    question = '基于这个内容帮我生成一个英文文件名，要全小写，不要后缀，尽量简短，多个英文时用下划线分隔: 进行登录认证'
    question_queue.append({"role": "user", "content": question})
    ask_gpt(question_queue)
