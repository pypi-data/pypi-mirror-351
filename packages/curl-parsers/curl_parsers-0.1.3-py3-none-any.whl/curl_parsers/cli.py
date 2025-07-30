# -*- coding: utf-8 -*-
# ----------------------------
# @Author:    影子
# @Software:  PyCharm
# @时间:       2025/5/30 上午10:21
# @项目:       curl_parsers
# @FileName:  cli.py
# ----------------------------
import argparse
from .parser_curl import _parse_curl
from .generator import _to_python_code, _to_json_code


def cli_run():
    """命令行解析"""
    parser = argparse.ArgumentParser(description='Convert curl command to Python requests code or JSON.')
    parser.add_argument('curl_command', type=str, help='The curl command string to be converted.')
    parser.add_argument('--output', choices=['python', 'json'], default='python',
                        help='Output format (default: python)')
    args = parser.parse_args()

    curl_cmd = args.curl_command.strip()
    try:
        parsed = _parse_curl(curl_cmd)
    except ValueError as e:
        print(f"解析 curl 命令失败: {e}")
        return

    if args.output == 'python':
        print(_to_python_code(parsed))
    elif args.output == 'json':
        print(_to_json_code(parsed))


if __name__ == "__main__":
    cli_run()
