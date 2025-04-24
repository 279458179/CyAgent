import os
import sys
import yt_dlp
from pathlib import Path
import time

def download_music(song_name):
    # 设置下载目录
    current_dir = Path(__file__).parent
    download_dir = current_dir / "download"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置yt-dlp选项
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac',
            'preferredquality': '0',  # 最高质量
        }],
        'outtmpl': str(download_dir / '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        # 创建yt-dlp下载器
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 搜索并下载音乐
            print(f"正在搜索并下载: {song_name}")
            ydl.download([f"ytsearch:{song_name}"])
            print(f"《{song_name}》下载完成！")
            # 添加短暂延迟，避免请求过于频繁
            time.sleep(2)
    except Exception as e:
        print(f"下载《{song_name}》时出现错误: {str(e)}")

def batch_download():
    # 获取当前目录
    current_dir = Path(__file__).parent
    list_file = current_dir / "audio_list.txt"
    
    # 检查文件是否存在
    if not list_file.exists():
        print("错误：找不到 audio_list.txt 文件！")
        return
    
    # 读取歌曲列表
    try:
        with open(list_file, 'r', encoding='utf-8') as f:
            songs = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"读取歌曲列表时出现错误: {str(e)}")
        return
    
    if not songs:
        print("歌曲列表为空！")
        return
    
    print(f"共找到 {len(songs)} 首歌曲待下载")
    
    # 批量下载
    for i, song in enumerate(songs, 1):
        print(f"\n[{i}/{len(songs)}] 开始下载")
        download_music(song)
    
    print("\n所有歌曲下载完成！")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 如果没有参数，执行批量下载
        batch_download()
    elif len(sys.argv) == 2:
        # 如果有一个参数，下载单首歌曲
        song_name = sys.argv[1]
        download_music(song_name)
    else:
        print("使用方法:")
        print("1. 批量下载: python music_downloader.py")
        print("2. 下载单首: python music_downloader.py '歌曲名称'")
        sys.exit(1) 