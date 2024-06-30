# config.py
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FFMPEG_PATH = os.getenv('FFMPEG_PATH', r"C:\Program Files\ffmpeg\bin\ffmpeg.exe")
DEFAULT_DOWNLOAD_DIR = os.getenv('DEFAULT_DOWNLOAD_DIR', 'downloads')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
CONCURRENT_DOWNLOADS = int(os.getenv('CONCURRENT_DOWNLOADS', '3'))