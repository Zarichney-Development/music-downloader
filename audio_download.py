# audio_download.py
import asyncio
import os
import logging
import subprocess
from typing import Dict, Optional
from pytube import YouTube
from tqdm import tqdm

from config import FFMPEG_PATH, MAX_RETRIES
from utils import setup_logging
from metadata import set_metadata, clean_filename

logger = setup_logging()


def check_ffmpeg():
    try:
        subprocess.run([FFMPEG_PATH, "-version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error(
            f"ffmpeg is not installed or not found at {FFMPEG_PATH}. Please install ffmpeg and update the FFMPEG_PATH."
        )
        return False


async def download_audio(
    song: str,
    video_info: Dict,
    output_path: str,
    format: str = "mp3",
    quality: str = "high",
) -> Optional[str]:
    """
    Download audio from a YouTube video, convert it to MP3, and set metadata.

    :param song: Original song query
    :param video_info: Dictionary containing video information
    :param output_path: Directory to save the downloaded file
    :return: Path to the downloaded MP3 file, or None if download failed
    """
    url = video_info["url"]
    logger.info(f"[{song}] Downloading from URL: {url}")

    for attempt in range(MAX_RETRIES):
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()

            # Create a progress bar
            progress_bar = tqdm(
                total=audio_stream.filesize,
                unit="B",
                unit_scale=True,
                desc=song,
                ncols=70,
            )

            def progress_callback(stream, chunk, bytes_remaining):
                current = audio_stream.filesize - bytes_remaining
                progress_bar.update(current - progress_bar.n)

            yt.register_on_progress_callback(progress_callback)

            output_file = audio_stream.download(output_path=output_path)
            progress_bar.close()

            logger.info(f"[{song}] Downloaded audio file: {output_file}")

            artist, title = video_info["correct_title"].split(" - ", 1)
            clean_name = clean_filename(f"{artist} - {title}")
            new_file = os.path.join(output_path, f"{clean_name}.{format}")

            # Convert to desired format using ffmpeg
            try:
                subprocess.run(
                    [
                        FFMPEG_PATH,
                        "-i",
                        output_file,
                        "-acodec",
                        "libmp3lame" if format == "mp3" else "aac",
                        "-b:a",
                        (
                            "320k"
                            if quality == "high"
                            else "192k" if quality == "medium" else "128k"
                        ),
                        new_file,
                    ],
                    check=True,
                    capture_output=True,
                )
                logger.info(f"[{song}] Converted to {format}: {new_file}")
            except subprocess.CalledProcessError as e:
                logger.error(f"[{song}] Error converting to {format}: {e}")
                return None

            logger.info(f"[{song}] Setting metadata for: {new_file}")
            set_metadata(new_file, title, artist, video_info["channelTitle"], url=url)

            logger.info(f"[{song}] Removing original file: {output_file}")
            os.remove(output_file)

            return new_file
        except Exception as e:
            logger.warning(
                f"[{song}] Attempt {attempt + 1} failed for URL '{url}': {str(e)}"
            )
            if attempt == MAX_RETRIES - 1:
                logger.error(
                    f"[{song}] All download attempts failed for URL '{url}': {str(e)}"
                )
                return None
            await asyncio.sleep(2**attempt)  # Exponential backoff
