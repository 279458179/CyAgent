#!/usr/bin/env python3
import argparse
from rich.console import Console
from rich.prompt import Prompt
from crawler import WebCrawler

def main():
    console = Console()
    
    # ���������в���
    parser = argparse.ArgumentParser(description='��ҳ����ץȡ����')
    parser.add_argument('--url', help='Ҫץȡ��URL')
    parser.add_argument('--format', choices=['txt', 'docx'], default='txt', help='�����ʽ')
    parser.add_argument('--output', default='downloaded_content', help='���Ŀ¼')
    args = parser.parse_args()
    
    # ��ʼ������
    crawler = WebCrawler(save_dir=args.output)
    
    if args.url:
        # ����URLģʽ
        crawler.crawl_page(args.url, args.format)
    else:
        # ����ģʽ
        console.print("[yellow]��ӭʹ����ҳ����ץȡ����[/yellow]")
        
        while True:
            url = Prompt.ask("\n������Ҫץȡ��URL������q�˳���")
            if url.lower() == 'q':
                break
                
            format_choice = Prompt.ask(
                "ѡ�񱣴��ʽ",
                choices=['txt', 'docx'],
                default='txt'
            )
            
            crawler.crawl_page(url, format_choice)
            
            # ѯ���Ƿ���ȡ����
            if Prompt.ask("�Ƿ���ȡҳ���е����ӣ�", choices=['y', 'n']) == 'y':
                links = crawler.extract_links(url)
                if links:
                    console.print(f"\n[green]�ҵ� {len(links)} �����ӣ�[/green]")
                    for i, link in enumerate(links, 1):
                        console.print(f"{i}. {link}")
                        
                    if Prompt.ask("�Ƿ�ץȡ��Щ���ӣ�", choices=['y', 'n']) == 'y':
                        crawler.crawl_pages(links, format_choice)

if __name__ == "__main__":
    main() 