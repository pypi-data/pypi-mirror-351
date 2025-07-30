# -*- coding: utf-8 -*-
# ----------------------------
# @Author:    影子
# @Software:  PyCharm
# @时间:       2025/5/28 下午11:26
# @项目:       curl_parsers
# @FileName:  generator.py
# ----------------------------
"""输出转换后的代码"""
import json
from typing import Dict, Any
from pprint import pformat


def _to_python_code(parsed: Dict[str, Any]) -> str:
    """ 将解析后的curl转换为python代码 """
    method = parsed['method'].lower()
    url = parsed['url']
    headers = parsed['headers']
    params = parsed['params']
    form_data = parsed['form_data']
    json_data = parsed['json_data']
    raw_data = parsed['raw_data']
    files = parsed['files']
    form_fields = parsed['form_fields']
    auth = parsed['auth']
    cookies = parsed['cookies']
    verify = parsed['verify']
    binary_file = parsed.get('binary_file')

    code = 'import requests\n'

    # 自动添加 Content-Type 头（如果未指定且 raw_data 存在）
    if 'Content-Type' not in headers and (raw_data or form_data):
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

    # 构建 headers
    if headers:
        code += '\nheaders = {\n'
        for k, v in headers.items():
            code += f"    '{k}': '{v}',\n"
        code = code.rstrip(',\n') + '\n}\n'

    # 构建 params
    if params:
        code += f"\nparams = {pformat(params)}\n"

    # 构建 binary_file 的读取逻辑
    if binary_file:
        code += f"\nwith open('{binary_file}', 'rb') as f:\n"
        code += "    data = f.read()\n"

    # 构建 json_data
    if json_data is not None:
        # 使用 pformat 自动转换 None、嵌套结构等
        processed_json = _replace_none_in_json(json_data)
        code += f"\njson_data = {pformat(processed_json, indent=4, width=100)}\n"

    # 构建 form_data
    elif form_data:
        code += f"\ndata = {pformat(form_data)}\n"

    # 构建 raw data
    elif raw_data:
        code += f"\ndata = '{raw_data}'\n"

    # 构建 files
    if files or form_fields:
        code += '\nfiles = {\n'
        for key, path in files.items():
            code += f"    '{key}': open('{path}', 'rb'),\n"
        for key, value in form_fields.items():
            code += f"    '{key}': (None, '{value}'),\n"
        code += '}\n'

    # 构建url
    code += f"\nurl = '{url}'\n"

    # 构建请求
    code += '\nresponse = requests.' + method + '('
    code += '\n    url,'

    if headers:
        code += '\n    headers=headers,'
    if params:
        code += '\n    params=params,'
    if json_data is not None:
        code += '\n    json=json_data,'
    else:
        # 如果存在 form_data、raw_data 或 binary_file，则添加 data=data
        if form_data or raw_data or binary_file:
            code += '\n    data=data,'
    if files or form_fields:
        code += '\n    files=files,'
    if auth:
        username, password = auth.split(':', 1)
        code += f'\n    auth=("{username}", "{password}"),'
    if cookies:
        cookie_dict = {}
        for item in cookies.strip().split(';'):
            if '=' in item:
                k, v = map(str.strip, item.split('=', 1))
                cookie_dict[k] = v
        code += f'\n    cookies={cookie_dict},'
    if not verify:
        code += '\n    verify=False,'

    code = code.rstrip(',') + '\n)\n'

    # 输出响应
    code += '\nprint(response.text)\n'
    return code


def _replace_none_in_json(obj):
    """递归替换 JSON 中的 'null' 字符串为 None"""
    if isinstance(obj, dict):
        return {k: _replace_none_in_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_none_in_json(i) for i in obj]
    elif obj == "null":
        return None
    else:
        return obj


def _to_json_code(parsed: dict) -> str:
    """
    将解析后的 curl 请求信息转换为 JSON 字符串。
    :param parsed: 解析后的请求信息字典
    :return: JSON 格式的字符串
    """
    return json.dumps(parsed, indent=4, ensure_ascii=False)
