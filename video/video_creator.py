import os
import sys
import time
from pathlib import Path
import requests
import yt_dlp
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from dotenv import load_dotenv
import random

# 加载环境变量
load_dotenv()

class VideoCreator:
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.downloads_dir = self.current_dir / "downloads"
        self.temp_dir = self.current_dir / "temp"
        self.output_dir = self.current_dir / "output"
        
        # 创建必要的目录
        for dir_path in [self.downloads_dir, self.temp_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Pexels API配置
        self.pexels_api_key = os.getenv('PEXELS_API_KEY')
        if not self.pexels_api_key:
            raise ValueError("请设置PEXELS_API_KEY环境变量")
        
        self.headers = {
            'Authorization': self.pexels_api_key
        }
    
    def download_pexels_video(self, query, per_page=10):
        """从Pexels下载视频"""
        url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Pexels API请求失败: {response.status_code}")
        
        videos = response.json()['videos']
        downloaded_files = []
        
        for video in videos:
            video_url = video['video_files'][0]['link']  # 获取最高质量的视频
            video_id = video['id']
            output_path = self.downloads_dir / f"{video_id}.mp4"
            
            print(f"正在下载视频: {video_id}")
            response = requests.get(video_url, stream=True)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            downloaded_files.append(output_path)
            time.sleep(1)  # 避免请求过于频繁
        
        return downloaded_files
    
    def download_background_music(self, duration=1800):
        """下载背景音乐"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(self.temp_dir / 'background_music.%(ext)s'),
        }
        
        # 搜索适合的背景音乐
        search_query = "ambient music background"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch:{search_query}"])
        
        return self.temp_dir / "background_music.mp3"
    
    def create_final_video(self, video_files, music_file, target_duration=1800):
        """合成最终视频"""
        # 加载视频片段
        video_clips = []
        for video_file in video_files:
            clip = VideoFileClip(str(video_file))
            video_clips.append(clip)
        
        # 计算每个片段的时长
        total_clips = len(video_clips)
        clip_duration = target_duration / total_clips
        
        # 调整每个片段的时长
        adjusted_clips = []
        for clip in video_clips:
            if clip.duration > clip_duration:
                # 随机选择片段
                start_time = random.uniform(0, clip.duration - clip_duration)
                adjusted_clip = clip.subclip(start_time, start_time + clip_duration)
            else:
                adjusted_clip = clip
            adjusted_clips.append(adjusted_clip)
        
        # 连接视频片段
        final_video = concatenate_videoclips(adjusted_clips)
        
        # 加载并调整背景音乐
        audio = AudioFileClip(str(music_file))
        if audio.duration > target_duration:
            audio = audio.subclip(0, target_duration)
        else:
            # 循环播放音乐直到视频结束
            audio = audio.loop(duration=target_duration)
        
        # 设置音频音量
        audio = audio.volumex(0.3)  # 降低音量到30%
        
        # 添加背景音乐
        final_video = final_video.set_audio(audio)
        
        # 导出最终视频
        output_path = self.output_dir / "final_video.mp4"
        final_video.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(self.temp_dir / "temp-audio.m4a"),
            remove_temp=True,
            fps=30,
            preset='slow',  # 使用较慢的编码预设以获得更好的质量
            threads=4,
            bitrate='8000k'  # 8K视频的比特率
        )
        
        # 清理临时文件
        for clip in video_clips:
            clip.close()
        final_video.close()
        audio.close()
        
        return output_path

def main():
    try:
        creator = VideoCreator()
        
        # 下载视频
        print("正在下载风景视频...")
        video_files = creator.download_pexels_video("nature landscape", per_page=20)
        
        # 下载背景音乐
        print("正在下载背景音乐...")
        music_file = creator.download_background_music()
        
        # 合成最终视频
        print("正在合成最终视频...")
        output_path = creator.create_final_video(video_files, music_file)
        
        print(f"视频创建完成！保存在: {output_path}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 