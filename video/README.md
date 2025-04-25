# 视频自动下载与合成工具

这是一个自动下载风景视频并合成高质量视频的工具。它可以：
- 从 Pexels 下载高质量风景视频
- 自动搜索并下载适合的背景音乐
- 将多个视频片段拼接成30分钟的视频
- 导出8K以上质量的最终视频

## 环境要求

- Python 3.12
- FFmpeg（用于视频处理）
- Pexels API Key

## 安装步骤

1. 安装 FFmpeg：
   - Windows: 从 https://ffmpeg.org/download.html 下载并安装
   - 确保 FFmpeg 已添加到系统环境变量中

2. 获取 Pexels API Key：
   - 访问 https://www.pexels.com/api/
   - 注册账号并获取 API Key

3. 创建 `.env` 文件并添加 API Key：
   ```
   PEXELS_API_KEY=你的API密钥
   ```

4. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

直接运行脚本：
```bash
python video_creator.py
```

脚本会自动：
1. 下载20个风景视频片段
2. 下载适合的背景音乐
3. 将视频片段拼接成30分钟的视频
4. 添加背景音乐
5. 导出高质量视频

## 输出文件

- 下载的视频片段保存在 `downloads` 目录
- 临时文件保存在 `temp` 目录
- 最终视频保存在 `output` 目录

## 注意事项

- 确保有足够的磁盘空间（建议至少20GB）
- 视频处理可能需要较长时间
- 需要稳定的网络连接
- 请遵守 Pexels 的使用条款 