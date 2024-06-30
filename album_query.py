import logging
from typing import List, Dict, Optional
import aiohttp
import asyncio
import json

from utils import setup_logging

logger = setup_logging()

MUSICBRAINZ_API_URL = "https://musicbrainz.org/ws/2"
HEADERS = {
  "User-Agent": "MyMusicDownloader/1.0.0 ( https://github.com/yourusername/your-repo )"
}


async def query_album_tracks(album: str, artist: str = "") -> Optional[List[str]]:
  """
  Query MusicBrainz API for album tracks.
  """
  query = f"release:{album}"
  if artist:
    query += f" AND artist:{artist}"

  params = {"query": query, "fmt": "json"}

  async with aiohttp.ClientSession() as session:
    try:
      async with session.get(
        f"{MUSICBRAINZ_API_URL}/release", params=params, headers=HEADERS
      ) as response:
        if response.status == 200:
          data = await response.json()
          logger.debug(
            f"MusicBrainz API response: {json.dumps(data, indent=2)}"
          )
          if data.get("releases"):
            # Sort releases by score and prefer official releases
            sorted_releases = sorted(
              data["releases"],
              key=lambda x: (
                x.get("score", 0),
                x.get("status") == "Official",
              ),
              reverse=True,
            )
            release_id = sorted_releases[0]["id"]
            return await get_tracks(release_id, session)
          else:
            logger.warning(f"No album found for query: {query}")
            return None
        else:
          logger.error(f"Error querying MusicBrainz API: {response.status}")
          return None
    except Exception as e:
      logger.error(f"Error querying MusicBrainz API: {str(e)}")
      return None


async def get_tracks(release_id: str, session: aiohttp.ClientSession) -> List[str]:
  """
  Get tracks for a specific release ID.
  """
  params = {
    "inc": "recordings artist-credits",  # Include artist-credits
    "fmt": "json",
  }

  try:
    async with session.get(
      f"{MUSICBRAINZ_API_URL}/release/{release_id}",
      params=params,
      headers=HEADERS,
    ) as response:
      if response.status == 200:
        data = await response.json()
        logger.debug(
          f"Track data response for release {release_id}: {json.dumps(data, indent=2)}"
        )
        tracks = parse_album_info(data)
        if not tracks:
          logger.error(f"No tracks found for release ID: {release_id}")
        return tracks
      else:
        logger.error(f"Error fetching tracks: {response.status}")
        return []
  except Exception as e:
    logger.error(f"Error fetching tracks: {str(e)}")
    logger.exception("Exception details:")
    return []


def parse_album_info(album_data: Dict) -> List[str]:
  """
  Parse album information and return a list of tracks.
  """
  tracks = []
  try:
    # Log the entire album_data for debugging
    logger.debug(f"Full album data: {json.dumps(album_data, indent=2)}")

    # Try to extract artist name from different possible locations
    artist = "Unknown Artist"
    if "artist-credit" in album_data:
      artist_credit = album_data["artist-credit"]
      logger.debug(f"Artist credit data: {artist_credit}")
      if isinstance(artist_credit, list) and len(artist_credit) > 0:
        artist = artist_credit[0].get("name", artist)
      elif isinstance(artist_credit, dict):
        artist = artist_credit.get("name", artist)
    logger.info(f"Extracted artist: {artist}")

    for medium in album_data.get("media", []):
      logger.debug(f"Processing medium: {medium}")
      for track in medium.get("tracks", []):
        logger.debug(f"Processing track: {track}")
        title = track.get("title", "Unknown Title")
        track_artist = track.get("artist-credit", [{}])[0].get("name", artist)
        tracks.append(f"{track_artist} - {title}")
        logger.debug(f"Added track: {track_artist} - {title}")

    if not tracks:
      logger.warning("No tracks found in the album data")
  except Exception as e:
    logger.error(f"Error parsing album info: {str(e)}")
    logger.exception("Exception details:")

  logger.info(f"Total tracks parsed: {len(tracks)}")
  return tracks


# Example usage
async def main():
  tracks = await query_album_tracks("The Dark Side of the Moon", "Pink Floyd")
  if tracks:
    print("Tracks:")
    for track in tracks:
      print(track)
  else:
    print("No tracks found or an error occurred.")


if __name__ == "__main__":
  # logging.getLogger().setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logging
  logging.getLogger().setLevel(
    logging.WARNING
  )  # Set to DEBUG for more detailed logging
  asyncio.run(main())
