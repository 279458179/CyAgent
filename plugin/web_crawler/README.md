# 网页内容抓取插件

这是一个用于自动抓取网页内容并保存为本地文件的插件。它能够模拟真实浏览器行为，自动提取网页内容，并支持保存为TXT或DOCX格式。

## 功能特点

- 自动伪装浏览器行为
- 支持单个页面抓取
- 支持批量页面抓取
- 自动提取页面链接
- 支持TXT和DOCX格式保存
- 交互式命令行界面
- 进度显示
- 错误处理机制

## 系统要求

- Python 3.12+
- 依赖包（见requirements.txt）

## 安装

1. 进入插件目录：
```bash
cd CyAgent/plugin/web_crawler
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 命令行模式

直接抓取单个URL：
```bash
python main.py --url "https://example.com" --format txt
```

参数说明：
- `--url`: 要抓取的URL
- `--format`: 保存格式，可选 'txt' 或 'docx'，默认为 'txt'
- `--output`: 输出目录，默认为 'downloaded_content'

示例：
```bash
# 抓取网页并保存为TXT格式
python main.py --url "https://example.com" --format txt

# 抓取网页并保存为DOCX格式
python main.py --url "https://example.com" --format docx

# 指定输出目录
python main.py --url "https://example.com" --output "my_docs"
```

### 2. 交互模式

直接运行程序进入交互模式：
```bash
python main.py
```

交互模式功能：
1. 输入要抓取的URL
2. 选择保存格式（txt/docx）
3. 可选择是否提取页面中的链接
4. 可选择是否抓取提取到的链接

### 3. 作为模块导入

```python
from crawler import WebCrawler

# 初始化爬虫
crawler = WebCrawler(save_dir="my_docs")

# 抓取单个页面
crawler.crawl_page("https://example.com", save_format="txt")

# 提取页面链接
links = crawler.extract_links("https://example.com")

# 批量抓取页面
crawler.crawl_pages(links, save_format="docx")
```

## 注意事项

1. 请合理设置抓取间隔，避免对目标网站造成压力
2. 某些网站可能有反爬虫机制，可能需要调整延迟时间
3. 建议遵守网站的robots.txt规则
4. 保存的文件名会根据URL自动生成
5. 如果遇到编码问题，可能需要调整文件保存时的编码设置

## 常见问题

1. 如果遇到编码错误，可以尝试修改文件保存时的编码：
```python
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
```

2. 如果网站有反爬虫机制，可以调整延迟时间：
```python
crawler.delay_range = (2, 5)  # 设置更长的延迟时间
```

3. 如果需要处理需要登录的网站，可以添加cookie支持：
```python
headers = crawler._get_random_headers()
headers['Cookie'] = 'your_cookie_here'
```

## 贡献

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

MIT License 