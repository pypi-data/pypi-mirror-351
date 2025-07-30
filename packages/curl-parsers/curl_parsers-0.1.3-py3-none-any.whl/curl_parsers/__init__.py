# -*- coding: utf-8 -*-
# ----------------------------
# @Author:    影子
# @Software:  PyCharm
# @时间:       2025/5/30 上午10:22
# @项目:       curl_parsers
# @FileName:  __init__.py
# ----------------------------
from .parser_curl import _parse_curl
from .generator import _to_python_code, _to_json_code


def parse_curl(command: str) -> dict:
    """将 curl 命令解析为 Python 对象"""
    if not command.strip():
        raise ValueError("Invalid curl command")
    return _parse_curl(command.strip())


def to_python(command: str) -> str:
    """将 curl 命令解析结果转为 Python 代码"""
    data = parse_curl(command)
    return _to_python_code(data)


def to_json(command: str) -> str:
    """将 curl 命令解析结果转为 JSON 字符串"""
    data = parse_curl(command)
    return _to_json_code(data)
