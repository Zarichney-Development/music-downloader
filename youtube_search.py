# youtube_search.py
import logging
from typing import List, Dict
import asyncio
from googleapiclient.discovery import build

from config import YOUTUBE_API_KEY, MAX_RETRIES
from utils import setup_logging

logger = setup_logging()
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

async def get_video_statistics(video_id: str) -> Dict:
  """
  Get statistics for a single video.
  """
  try:
    response = youtube.videos().list(
      part='statistics',
      id=video_id
    ).execute()

    if response['items']:
      stats = response['items'][0]['statistics']
      return {
        'viewCount': int(stats.get('viewCount', 0)),
        'likeCount': int(stats.get('likeCount', 0)),
        'dislikeCount': int(stats.get('dislikeCount', 0))
      }
    else:
      return {'viewCount': 0, 'likeCount': 0, 'dislikeCount': 0}
  except Exception as e:
    logger.error(f"Error getting statistics for video {video_id}: {e}")
    return {'viewCount': 0, 'likeCount': 0, 'dislikeCount': 0}

async def search_youtube(query: str, max_results: int = 10) -> List[Dict]:
  """
  Search YouTube for a given query and get video statistics.
  
  :param query: Search query string
  :param max_results: Maximum number of results to return
  :return: List of search result dictionaries
  """
  for attempt in range(MAX_RETRIES):
    try:
      response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results,
        type='video'
      ).execute()
      logger.info(f"[{query}] Search successful")

      search_results = []
      for item in response['items']:
        video_id = item['id']['videoId']
        stats = await get_video_statistics(video_id)
        search_results.append({
          'title': item['snippet']['title'],
          'description': item['snippet']['description'],
          'url': f"https://www.youtube.com/watch?v={video_id}",
          'channelTitle': item['snippet']['channelTitle'],
          'videoId': video_id,
          'viewCount': stats['viewCount'],
          'likeCount': stats['likeCount'],
          'dislikeCount': stats['dislikeCount'],
          'publishedAt': item['snippet']['publishedAt']
        })

      return search_results
    except Exception as e:
      logger.warning(f"[{query}] Attempt {attempt + 1} failed for search: {e}")
      if attempt == MAX_RETRIES - 1:
        logger.error(f"[{query}] All search attempts failed: {e}")
        return []
      await asyncio.sleep(2 ** attempt)  # Exponential backoff
