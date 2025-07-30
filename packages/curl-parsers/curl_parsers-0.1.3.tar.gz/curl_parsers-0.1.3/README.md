# curl_parsers

#### 介绍

curl命令转python代码，支持json格式数据转换

#### 安装教程

1. pip install curl_parsers
2. 或者下载源码，解压后运行

#### 使用说明

1. 终端命令行输入：

```base
方法一：
python -m curl_parsers.cli 'curl -X POST https://api.example.com/submit' --output python
python -m curl_parsers.cli 'curl -X POST https://api.example.com/submit' --output json

方法二：
uncurl 'curl -X POST https://api.example.com/submit' --output python
uncurl 'curl -X POST https://api.example.com/submit' --output json
```

2. 调用函数：

```python
from curl_parsers import parse_curl, to_python, to_json

curl_cmd = "curl -X POST https://api.example.com/submit"
print(parse_curl(curl_cmd))  # 解析curl命令并返回字典数据
print(to_python(curl_cmd))  # 转换为python代码
print(to_json(curl_cmd))  # 转换为json格式数据

````

