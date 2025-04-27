import os
import sys
import time
from pathlib import Path
import yt_dlp
from typing import Optional
import re

def clean_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def is_file_exists(download_dir: Path, song_name: str) -> bool:
    """检查文件是否已存在"""
    clean_name = clean_filename(song_name)
    for ext in ['.flac', '.mp3', '.m4a']:
        if (download_dir / f"{clean_name}{ext}").exists():
            return True
    return False

def download_music(song_name: str, max_retries: int = 3) -> bool:
    """
    下载音乐文件
    :param song_name: 歌曲名称
    :param max_retries: 最大重试次数
    :return: 是否下载成功
    """
    # 设置下载目录
    current_dir = Path(__file__).parent
    download_dir = current_dir / "download"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查文件是否已存在
    if is_file_exists(download_dir, song_name):
        print(f"《{song_name}》已存在，跳过下载")
        return True
    
    # 优化搜索关键词，添加"原版"或"官方"等关键词
    search_query = f"{song_name} 原版 官方"
    
    # 配置yt-dlp选项
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac',
            'preferredquality': '0',  # 最高质量
        }],
        'outtmpl': str(download_dir / f'{clean_filename(song_name)}.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'progress_hooks': [lambda d: print(f"\r下载进度: {d['_percent_str']}", end='') if d['status'] == 'downloading' else None],
        'extract_flat': False,
        'noplaylist': True,
        'prefer_ffmpeg': True,
        'keepvideo': False,
    }
    
    for attempt in range(max_retries):
        try:
            print(f"\n正在搜索并下载: {song_name} (尝试 {attempt + 1}/{max_retries})")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch:{search_query}"])
            print(f"\n《{song_name}》下载完成！")
            time.sleep(2)  # 添加延迟避免请求过于频繁
            return True
        except Exception as e:
            print(f"\n下载《{song_name}》时出现错误: {str(e)}")
            if attempt < max_retries - 1:
                print(f"等待 5 秒后重试...")
                time.sleep(5)
            else:
                print(f"达到最大重试次数，跳过下载《{song_name}》")
                return False

def batch_download():
    """批量下载歌曲"""
    current_dir = Path(__file__).parent
    list_file = current_dir / "audio_list.txt"
    
    if not list_file.exists():
        print("错误：找不到 audio_list.txt 文件！")
        return
    
    try:
        with open(list_file, 'r', encoding='utf-8') as f:
            # 跳过注释行和空行
            songs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"读取歌曲列表时出现错误: {str(e)}")
        return
    
    if not songs:
        print("歌曲列表为空！")
        return
    
    total_songs = len(songs)
    successful_downloads = 0
    
    print(f"共找到 {total_songs} 首歌曲待下载")
    
    for i, song in enumerate(songs, 1):
        print(f"\n[{i}/{total_songs}] 开始下载")
        if download_music(song):
            successful_downloads += 1
    
    print(f"\n下载完成！成功: {successful_downloads}/{total_songs}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        batch_download()
    elif len(sys.argv) == 2:
        song_name = sys.argv[1]
        download_music(song_name)
    else:
        print("使用方法:")
        print("1. 批量下载: python music_downloader.py")
        print("2. 下载单首: python music_downloader.py '歌曲名称'")
        sys.exit(1) 