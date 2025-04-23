import os
import time
import random
from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from rich.console import Console
from rich.progress import Progress
from docx import Document
from urllib.parse import urljoin, urlparse

class WebCrawler:
    def __init__(self, save_dir: str = "downloaded_content"):
        """
        初始化爬虫
        
        Args:
            save_dir (str): 保存文件的目录
        """
        self.ua = UserAgent()
        self.save_dir = save_dir
        self.console = Console()
        
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 设置请求头
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 设置请求延迟范围（秒）
        self.delay_range = (1, 3)
        
    def _get_random_headers(self) -> Dict[str, str]:
        """
        生成随机请求头
        
        Returns:
            Dict[str, str]: 请求头字典
        """
        headers = self.headers.copy()
        headers['User-Agent'] = self.ua.random
        return headers
        
    def _add_delay(self):
        """
        添加随机延迟
        """
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
    def _is_valid_url(self, url: str) -> bool:
        """
        检查URL是否有效
        
        Args:
            url (str): 要检查的URL
            
        Returns:
            bool: URL是否有效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def _get_filename_from_url(self, url: str) -> str:
        """
        从URL生成文件名
        
        Args:
            url (str): 网页URL
            
        Returns:
            str: 文件名
        """
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = 'index'
        return path.replace('/', '_')
        
    def _save_as_txt(self, content: str, filename: str):
        """
        保存为TXT文件
        
        Args:
            content (str): 要保存的内容
            filename (str): 文件名
        """
        filepath = os.path.join(self.save_dir, f"{filename}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def _save_as_docx(self, content: str, filename: str):
        """
        保存为DOCX文件
        
        Args:
            content (str): 要保存的内容
            filename (str): 文件名
        """
        filepath = os.path.join(self.save_dir, f"{filename}.docx")
        doc = Document()
        doc.add_paragraph(content)
        doc.save(filepath)
        
    def crawl_page(self, url: str, save_format: str = 'txt') -> bool:
        """
        爬取单个页面
        
        Args:
            url (str): 要爬取的URL
            save_format (str): 保存格式，'txt'或'docx'
            
        Returns:
            bool: 是否成功
        """
        if not self._is_valid_url(url):
            self.console.print(f"[red]无效的URL: {url}[/red]")
            return False
            
        try:
            # 添加随机延迟
            self._add_delay()
            
            # 发送请求
            response = requests.get(url, headers=self._get_random_headers(), timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取正文内容
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
                
            # 获取文本
            text = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # 生成文件名
            filename = self._get_filename_from_url(url)
            
            # 保存文件
            if save_format.lower() == 'docx':
                self._save_as_docx(text, filename)
            else:
                self._save_as_txt(text, filename)
                
            self.console.print(f"[green]成功保存: {filename}.{save_format}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]爬取失败: {str(e)}[/red]")
            return False
            
    def crawl_pages(self, urls: List[str], save_format: str = 'txt'):
        """
        批量爬取页面
        
        Args:
            urls (List[str]): URL列表
            save_format (str): 保存格式，'txt'或'docx'
        """
        with Progress() as progress:
            task = progress.add_task("[cyan]爬取进度...", total=len(urls))
            
            for url in urls:
                self.crawl_page(url, save_format)
                progress.update(task, advance=1)
                
    def extract_links(self, url: str) -> List[str]:
        """
        提取页面中的所有链接
        
        Args:
            url (str): 要提取链接的URL
            
        Returns:
            List[str]: 链接列表
        """
        try:
            response = requests.get(url, headers=self._get_random_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    # 转换为绝对URL
                    absolute_url = urljoin(url, href)
                    if self._is_valid_url(absolute_url):
                        links.append(absolute_url)
                        
            return links
            
        except Exception as e:
            self.console.print(f"[red]提取链接失败: {str(e)}[/red]")
            return [] 