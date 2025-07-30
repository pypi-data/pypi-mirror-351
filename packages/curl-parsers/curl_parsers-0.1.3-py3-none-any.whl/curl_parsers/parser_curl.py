# -*- coding: utf-8 -*-
# ----------------------------
# @Author:    影子
# @Software:  PyCharm
# @时间:       2025/5/28 下午12:05
# @项目:       curl_parsers
# @FileName:  parser_curl.py
# ----------------------------
"""解析curl命令"""
import json
import shlex
import urllib.parse
from typing import Dict, Any
from urllib.parse import parse_qs, unquote


def _parse_urlencoded(data: str) -> dict:
    """解析 urlencoded 格式的字符串，返回字典"""
    try:
        return {k: unquote(v[0]).replace('+', ' ') for k, v in parse_qs(data).items()}
    except Exception as err:
        return {}


def _parse_curl(curl_command: str) -> Dict[str, Any]:
    """解析 curl 命令字符串，提取关键参数"""
    curl_command = curl_command.strip().replace('\\\n', ' ').replace('\n', ' ')
    args = shlex.split(curl_command)

    if not args or args[0].lower() != 'curl':
        raise ValueError("Invalid curl command")

    args = args[1:]  # 删除命令的头标识 curl

    result = {
        'method': 'GET',
        'url': None,
        'headers': {},
        'params': {},  # URL 查询参数
        'form_data': {},  # application/x-www-form-urlencoded 数据
        'json_data': None,  # JSON body 数据
        'raw_data': None,  # 其他原始 body 数据
        'files': {},  # multipart/form-data 文件上传
        'form_fields': {},  # multipart/form-data 普通字段
        'auth': None,
        'verify': True,
        'cookies': None,
        'binary_file': None,  # 新增字段，用于记录 --data-binary 的文件路径
    }

    i = 0
    has_json_content_type = False
    while i < len(args):
        arg = args[i]

        # 设置请求方法
        if arg in ['-X', '--request']:
            i += 1
            if i < len(args):
                result['method'] = args[i].upper()

        # 设置 header
        elif arg in ['-H', '--header']:
            i += 1
            if i < len(args):
                header = args[i]
                if ':' in header:
                    k, v = map(str.strip, header.split(':', 1))
                    result['headers'][k] = v

                    if k.lower() == 'content-type' and v.lower() == 'application/json':
                        has_json_content_type = True
                else:
                    result['headers'][header.strip()] = ''

        # POST 数据
        elif arg in ['-d', '--data']:
            i += 1
            if i < len(args):
                data = args[i]
                if '=' in data or '&' in data:
                    # 解析 form-urlencoded 数据
                    parsed_data = _parse_urlencoded(data)
                    result['form_data'].update(parsed_data)
                else:
                    # 非 key=value 形式，视为 raw 或 JSON
                    if not has_json_content_type:
                        # 如果未指定 Content-Type: application/json，则视为表单数据
                        result['raw_data'] = data
                    else:
                        # 显式指定 JSON 格式
                        try:
                            json_obj = json.loads(data)
                            result['json_data'] = json_obj
                        except json.JSONDecodeError:
                            result['raw_data'] = data
                if result['method'] == 'GET':
                    result['method'] = 'POST'

        # raw 数据
        elif arg in ['--data-raw', '--data-ascii']:
            i += 1
            if i < len(args):
                raw = args[i]
                try:
                    json_obj = json.loads(raw)
                    result['json_data'] = json_obj
                except json.JSONDecodeError:
                    result['raw_data'] = raw
                if result['method'] == 'GET':
                    result['method'] = 'POST'

        # urlencode 数据
        elif arg == '--data-urlencode':
            i += 1
            if i < len(args):
                key_value = args[i]
                if '=' in key_value:
                    k, v = key_value.split('=', 1)
                    result['form_data'][k] = unquote(v.replace('+', ' '))
                else:
                    result['form_data'][key_value] = ''
                if result['method'] == 'GET':
                    result['method'] = 'POST'

        # 文件上传
        elif arg == '--data-binary':
            i += 1
            if i < len(args):
                data = args[i]
                if data.startswith('@'):
                    result['binary_file'] = data[1:]
                else:
                    result['raw_data'] = data
                if result['method'] == 'GET':
                    result['method'] = 'POST'

        # 认证信息
        elif arg in ['-u', '--user']:
            i += 1
            if i < len(args):
                result['auth'] = args[i]

        # 忽略 SSL 验证
        elif arg in ['-k', '--insecure']:
            result['verify'] = False

        # Cookie处理
        elif arg in ['-b', '--cookie']:
            i += 1
            if i < len(args):
                result['cookies'] = args[i]

        # GET 请求
        elif arg in ['-G', '--get']:
            result['method'] = 'GET'

        # multipart/form-data 表单字段
        elif arg in ['-F', '--form']:
            i += 1
            if i < len(args):
                field = args[i]
                key_value = field.split('=', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    if value.startswith('@'):
                        # 文件上传字段
                        path = value[1:]
                        result['files'][key] = path
                    else:
                        result['form_fields'][key] = unquote(value.replace('+', ' '))
                else:
                    result['form_fields'][key_value[0]] = ''
                if result['method'] == 'GET':
                    result['method'] = 'POST'

        # URL 地址
        elif not arg.startswith('-') and result['url'] is None:
            parsed_url = urllib.parse.urlparse(arg)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            query_params = parse_qs(parsed_url.query)
            result['url'] = base_url
            result['params'] = {k: unquote(v[0]) for k, v in query_params.items()}

        i += 1

    return result
