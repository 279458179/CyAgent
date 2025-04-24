# 音乐下载器

这是一个简单的音乐下载脚本，可以根据歌曲名称自动搜索并下载最高质量的 FLAC 格式音乐。

## 环境要求

- Python 3.12
- FFmpeg（用于音频转换）

## 安装步骤

1. 安装 FFmpeg：
   - Windows: 从 https://ffmpeg.org/download.html 下载并安装
   - 确保 FFmpeg 已添加到系统环境变量中

2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

运行以下命令下载音乐：
```bash
python music_downloader.py "歌曲名称"
```

例如：
```bash
python music_downloader.py "周杰伦 稻香"
```

下载的音乐文件将保存在 `audio/download` 目录下。

## 注意事项

- 请确保您有足够的磁盘空间
- 下载的音乐文件将以 FLAC 格式保存
- 如果遇到下载错误，请检查网络连接和 FFmpeg 安装是否正确 