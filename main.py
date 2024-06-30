# main.py
import argparse
import asyncio
import logging
import sys
from typing import List

from config import DEFAULT_DOWNLOAD_DIR, OPENAI_API_KEY, YOUTUBE_API_KEY
from youtube_search import search_youtube
from audio_download import download_audio
from llm_interface import get_best_match
from utils import setup_logging
from album_query import query_album_tracks

logger = setup_logging()


def check_environment_variables():
  """Check if required environment variables are set."""
  missing_vars = []
  if not YOUTUBE_API_KEY:
    missing_vars.append("YOUTUBE_API_KEY")
  if not OPENAI_API_KEY:
    missing_vars.append("OPENAI_API_KEY")

  if missing_vars:
    logger.error(
      f"Missing required environment variables: {', '.join(missing_vars)}"
    )
    logger.error(
      "Please set these variables in your environment or in a .env file."
    )
    sys.exit(1)


def parse_arguments():
  parser = argparse.ArgumentParser(
    description="Download songs or albums from YouTube."
  )
  parser.add_argument("-s", "--songs", nargs="+", help="List of songs to download")
  parser.add_argument("-a", "--albums", nargs="+", help="List of albums to download")
  parser.add_argument(
    "--artist", help="Artist name (optional, improves album search accuracy)"
  )
  parser.add_argument(
    "-d",
    "--directory",
    default=DEFAULT_DOWNLOAD_DIR,
    help="Directory to save downloaded songs",
  )
  parser.add_argument(
    "--batch", action="store_true", help="Run in batch mode (non-interactive)"
  )
  return parser.parse_args()


async def download_songs(songs: List[str], output_path: str) -> None:
  for song in songs:
    search_results = await search_youtube(song)
    if not search_results:
      logger.error(f"[{song}] No search results found")
      continue

    best_match = await get_best_match(song, search_results)
    if not best_match:
      logger.error(f"[{song}] Couldn't determine best match")
      continue

    await download_audio(song, best_match, output_path)


async def download_album(album: str, artist: str, output_path: str) -> None:
  tracks = await query_album_tracks(album, artist)
  if not tracks:
    logger.error(f"No tracks found for album: {album}")
    return

  logger.info(f"Found {len(tracks)} tracks for album: {album}")
  await download_songs(tracks, output_path)


async def main():
  args = parse_arguments()

  if args.albums:
    await download_album(args.albums, args.artist, args.directory)
  elif args.songs:
    await download_songs(args.songs, args.directory)
  elif args.batch:
    print(
      "Error: Batch mode requires a list of songs or an album. Use -s/--songs or -a/--albums to specify."
    )
  else:
    # Interactive mode
    while True:
      user_input = input(
        "Enter a song to download, 'album' to download an album, or 'exit' to quit: "
      ).strip()
      if user_input.lower() == "exit":
        break
      elif user_input.lower() == "album":
        album = input("Enter album name: ").strip()
        artist = input("Enter artist name (optional): ").strip()
        await download_album(album, artist, args.directory)
      elif user_input:
        await download_songs([user_input], args.directory)


if __name__ == "__main__":
  asyncio.run(main())
