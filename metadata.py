# metadata.py
import re
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, WXXX

def clean_filename(filename: str) -> str:
  """
  Clean up the filename by removing invalid characters.
  """
  # Remove invalid filename characters
  cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)
  # Replace multiple spaces with a single space
  cleaned = re.sub(r'\s+', ' ', cleaned).strip()
  return cleaned

def set_metadata(file_path: str, title: str, artist: str, album: str = "", year: str = "", url: str = ""):
  """
  Set metadata for the MP3 file.
  """
  try:
    audio = EasyID3(file_path)
  except mutagen.id3.ID3NoHeaderError:
    audio = mutagen.File(file_path, easy=True)
    audio.add_tags()

  audio['title'] = title
  audio['artist'] = artist
  if album:
    audio['album'] = album
  if year:
    audio['date'] = year
  audio.save()

  # Set ID3v2.4 tags
  audio = ID3(file_path)
  audio.add(TIT2(encoding=3, text=title))
  audio.add(TPE1(encoding=3, text=artist))
  if album:
    audio.add(TALB(encoding=3, text=album))
  if year:
    audio.add(TDRC(encoding=3, text=year))
  if url:
    audio.add(WXXX(encoding=3, url=url))
  audio.save(v2_version=4)
