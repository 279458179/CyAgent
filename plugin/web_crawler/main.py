#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from rich.console import Console
from rich.prompt import Prompt
from crawler import WebCrawler

def main():
    console = Console()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='网页内容抓取工具')
    parser.add_argument('--url', help='要抓取的URL')
    parser.add_argument('--format', choices=['txt', 'docx'], default='txt', help='保存格式')
    parser.add_argument('--output', default='downloaded_content', help='输出目录')
    args = parser.parse_args()
    
    # 初始化爬虫
    crawler = WebCrawler(save_dir=args.output)
    
    if args.url:
        # 单个URL模式
        crawler.crawl_page(args.url, args.format)
    else:
        # 交互模式
        console.print("[yellow]欢迎使用网页内容抓取工具[/yellow]")
        
        while True:
            url = Prompt.ask("\n请输入要抓取的URL（输入q退出）")
            if url.lower() == 'q':
                break
                
            format_choice = Prompt.ask(
                "选择保存格式",
                choices=['txt', 'docx'],
                default='txt'
            )
            
            crawler.crawl_page(url, format_choice)
            
            # 询问是否提取链接
            if Prompt.ask("是否提取页面中的链接？", choices=['y', 'n']) == 'y':
                links = crawler.extract_links(url)
                if links:
                    console.print(f"\n[green]找到 {len(links)} 个链接：[/green]")
                    for i, link in enumerate(links, 1):
                        console.print(f"{i}. {link}")
                        
                    if Prompt.ask("是否抓取这些链接？", choices=['y', 'n']) == 'y':
                        crawler.crawl_pages(links, format_choice)

if __name__ == "__main__":
    main() 