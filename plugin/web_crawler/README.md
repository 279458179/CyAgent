# ��ҳ����ץȡ���

����һ�������Զ�ץȡ��ҳ���ݲ�����Ϊ�����ļ��Ĳ�������ܹ�ģ����ʵ�������Ϊ���Զ���ȡ��ҳ���ݣ���֧�ֱ���ΪTXT��DOCX��ʽ��

## �����ص�

- �Զ�αװ�������Ϊ
- ֧�ֵ���ҳ��ץȡ
- ֧������ҳ��ץȡ
- �Զ���ȡҳ������
- ֧��TXT��DOCX��ʽ����
- ����ʽ�����н���
- ������ʾ
- ���������

## ϵͳҪ��

- Python 3.12+
- ����������requirements.txt��

## ��װ

1. ������Ŀ¼��
```bash
cd CyAgent/plugin/web_crawler
```

2. ��װ������
```bash
pip install -r requirements.txt
```

## ʹ�÷���

### 1. ������ģʽ

ֱ��ץȡ����URL��
```bash
python main.py --url "https://example.com" --format txt
```

����˵����
- `--url`: Ҫץȡ��URL
- `--format`: �����ʽ����ѡ 'txt' �� 'docx'��Ĭ��Ϊ 'txt'
- `--output`: ���Ŀ¼��Ĭ��Ϊ 'downloaded_content'

ʾ����
```bash
# ץȡ��ҳ������ΪTXT��ʽ
python main.py --url "https://example.com" --format txt

# ץȡ��ҳ������ΪDOCX��ʽ
python main.py --url "https://example.com" --format docx

# ָ�����Ŀ¼
python main.py --url "https://example.com" --output "my_docs"
```

### 2. ����ģʽ

ֱ�����г�����뽻��ģʽ��
```bash
python main.py
```

����ģʽ���ܣ�
1. ����Ҫץȡ��URL
2. ѡ�񱣴��ʽ��txt/docx��
3. ��ѡ���Ƿ���ȡҳ���е�����
4. ��ѡ���Ƿ�ץȡ��ȡ��������

### 3. ��Ϊģ�鵼��

```python
from crawler import WebCrawler

# ��ʼ������
crawler = WebCrawler(save_dir="my_docs")

# ץȡ����ҳ��
crawler.crawl_page("https://example.com", save_format="txt")

# ��ȡҳ������
links = crawler.extract_links("https://example.com")

# ����ץȡҳ��
crawler.crawl_pages(links, save_format="docx")
```

## ע������

1. ���������ץȡ����������Ŀ����վ���ѹ��
2. ĳЩ��վ�����з�������ƣ�������Ҫ�����ӳ�ʱ��
3. ����������վ��robots.txt����
4. ������ļ��������URL�Զ�����
5. ��������������⣬������Ҫ�����ļ�����ʱ�ı�������

## ��������

1. �������������󣬿��Գ����޸��ļ�����ʱ�ı��룺
```python
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
```

2. �����վ�з�������ƣ����Ե����ӳ�ʱ�䣺
```python
crawler.delay_range = (2, 5)  # ���ø������ӳ�ʱ��
```

3. �����Ҫ������Ҫ��¼����վ���������cookie֧�֣�
```python
headers = crawler._get_random_headers()
headers['Cookie'] = 'your_cookie_here'
```

## ����

��ӭ�ύIssue��Pull Request�������Ľ���Ŀ��

## ���֤

MIT License 