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
        ��ʼ������
        
        Args:
            save_dir (str): �����ļ���Ŀ¼
        """
        self.ua = UserAgent()
        self.save_dir = save_dir
        self.console = Console()
        
        # ��������Ŀ¼
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # ��������ͷ
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # ���������ӳٷ�Χ���룩
        self.delay_range = (1, 3)
        
    def _get_random_headers(self) -> Dict[str, str]:
        """
        �����������ͷ
        
        Returns:
            Dict[str, str]: ����ͷ�ֵ�
        """
        headers = self.headers.copy()
        headers['User-Agent'] = self.ua.random
        return headers
        
    def _add_delay(self):
        """
        �������ӳ�
        """
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
    def _is_valid_url(self, url: str) -> bool:
        """
        ���URL�Ƿ���Ч
        
        Args:
            url (str): Ҫ����URL
            
        Returns:
            bool: URL�Ƿ���Ч
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def _get_filename_from_url(self, url: str) -> str:
        """
        ��URL�����ļ���
        
        Args:
            url (str): ��ҳURL
            
        Returns:
            str: �ļ���
        """
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = 'index'
        return path.replace('/', '_')
        
    def _save_as_txt(self, content: str, filename: str):
        """
        ����ΪTXT�ļ�
        
        Args:
            content (str): Ҫ���������
            filename (str): �ļ���
        """
        filepath = os.path.join(self.save_dir, f"{filename}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def _save_as_docx(self, content: str, filename: str):
        """
        ����ΪDOCX�ļ�
        
        Args:
            content (str): Ҫ���������
            filename (str): �ļ���
        """
        filepath = os.path.join(self.save_dir, f"{filename}.docx")
        doc = Document()
        doc.add_paragraph(content)
        doc.save(filepath)
        
    def crawl_page(self, url: str, save_format: str = 'txt') -> bool:
        """
        ��ȡ����ҳ��
        
        Args:
            url (str): Ҫ��ȡ��URL
            save_format (str): �����ʽ��'txt'��'docx'
            
        Returns:
            bool: �Ƿ�ɹ�
        """
        if not self._is_valid_url(url):
            self.console.print(f"[red]��Ч��URL: {url}[/red]")
            return False
            
        try:
            # �������ӳ�
            self._add_delay()
            
            # ��������
            response = requests.get(url, headers=self._get_random_headers(), timeout=10)
            response.raise_for_status()
            
            # ����HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ��ȡ��������
            # �Ƴ��ű�����ʽ
            for script in soup(["script", "style"]):
                script.decompose()
                
            # ��ȡ�ı�
            text = soup.get_text()
            
            # �����ı�
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # �����ļ���
            filename = self._get_filename_from_url(url)
            
            # �����ļ�
            if save_format.lower() == 'docx':
                self._save_as_docx(text, filename)
            else:
                self._save_as_txt(text, filename)
                
            self.console.print(f"[green]�ɹ�����: {filename}.{save_format}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]��ȡʧ��: {str(e)}[/red]")
            return False
            
    def crawl_pages(self, urls: List[str], save_format: str = 'txt'):
        """
        ������ȡҳ��
        
        Args:
            urls (List[str]): URL�б�
            save_format (str): �����ʽ��'txt'��'docx'
        """
        with Progress() as progress:
            task = progress.add_task("[cyan]��ȡ����...", total=len(urls))
            
            for url in urls:
                self.crawl_page(url, save_format)
                progress.update(task, advance=1)
                
    def extract_links(self, url: str) -> List[str]:
        """
        ��ȡҳ���е���������
        
        Args:
            url (str): Ҫ��ȡ���ӵ�URL
            
        Returns:
            List[str]: �����б�
        """
        try:
            response = requests.get(url, headers=self._get_random_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    # ת��Ϊ����URL
                    absolute_url = urljoin(url, href)
                    if self._is_valid_url(absolute_url):
                        links.append(absolute_url)
                        
            return links
            
        except Exception as e:
            self.console.print(f"[red]��ȡ����ʧ��: {str(e)}[/red]")
            return [] 