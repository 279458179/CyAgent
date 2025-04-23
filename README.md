# CyAgent - 系统初始化智能体

这是一个用于自动化系统初始化的智能体项目，支持多种Linux发行版的系统初始化配置。

## 功能特点

- 支持多种Linux发行版（CentOS, Ubuntu, Debian, AlmaLinux）
- 自动检测系统类型
- 系统初始化功能：
  - 防火墙配置
  - 系统更新源配置
  - 网络接口配置
  - 基础软件包安装

## 系统要求

- Python 3.12+
- 支持的Linux发行版：
  - CentOS 7/8
  - Ubuntu 20.04/22.04
  - Debian 10/11
  - AlmaLinux 8/9

## 安装

```bash
git clone https://github.com/yourusername/CyAgent.git
cd CyAgent
pip install -r requirements.txt
```

## 使用方法

```bash
python src/main.py
```

## 项目结构

```
CyAgent/
├── src/                # 源代码目录
├── tests/              # 测试代码目录
├── docs/               # 文档目录
└── requirements.txt    # 项目依赖
```

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

MIT License 