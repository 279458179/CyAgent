#!/bin/bash

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误：需要Python 3.12.0或更高版本"
    exit 1
fi

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行此脚本"
    exit 1
fi

# 安装依赖
pip3 install -r requirements.txt

# 运行主程序
python3 src/main.py "$@" 