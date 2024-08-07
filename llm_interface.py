# llm_interface.py
import json
import logging
from typing import List, Dict, Optional
import openai

from config import OPENAI_API_KEY
from utils import setup_logging

logger = setup_logging()
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

async def get_best_match(query: str, search_results: List[Dict]) -> Optional[Dict]:
  """
  Use OpenAI's GPT to determine the best match for a song from search results.
  
  :param song: Original song query
  :param search_results: List of YouTube search results
  :return: Dictionary with best matching video info, or None if no match found
  """
  if not search_results:
    return None
    
  system_prompt = """
    YouTube Audio Selection System

    Task: Review YouTube search results and identify the best video for downloading audio based on a given query.

    Rules (in order of precedence):
    1. Assume the most popular artist for a song title if no artist is specified.
    2. Select the official recorded studio version if both song title and artist are specified.
    3. Choose a video that matches the requested cover artist if a cover version is specified.
    4. Select a video that matches the requested version type (remix, instrumental, live, acoustic).

    Additional considerations:
    - Favor audio-only versions or lyric videos over music videos.
    - Do not select instrumental-only videos unless specified.
    - Consider official sources (e.g., VEVO, official artist channel) over random YouTube users.
    - Refer to view count, likes/dislikes, and upload date for decision making.
    - Avoid live performances unless requested.

    Prioritize videos that:
    1. Match the query requirements precisely.
    2. Come from official or reputable sources.
    3. Have high view counts and positive engagement metrics.
    4. Are more recent uploads, unless an older version is required.

    Aim to select the highest quality audio source matching the user's query and intent. Use the proper JSON structure for responses.
  """

  user_prompt = f"Query: {query}\n\nSearch Results:\n"
  for i, result in enumerate(search_results, 1):
    user_prompt += f"{i}. Title: {result['title']}, Channel: {result['channelTitle']}, Views: {result['viewCount']}, Likes: {result['likeCount']}, Dislikes: {result['dislikeCount']}, Published: {result['publishedAt']}\n"

  tools = [{
    "type": "function",
    "function": {
      "name": "select_best_match",
      "description": "Select the best matching video for the given query",
      "parameters": {
        "type": "object",
        "properties": {
          "best_match_index": {
            "type": "integer",
            "description": "The index of the best matching video (1-based)"
          },
          "correct_title": {
            "type": "string",
            "description": "The correct title in the format 'Artist - Song Title (Optional Version Description)'. Omit the version description when moot such as (audio) or (lyric video)."
          },
          "explanation": {
            "type": "string",
            "description": "A brief explanation of why this video was selected"
          }
        },
        "required": ["best_match_index", "correct_title", "explanation"]
      }
    }
  }]

  try:
    logger.info(f"[{query}] Requesting LLM decision from OpenAI")
    response = await client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ],
      tools=tools,
      tool_choice={"type": "function", "function": {"name": "select_best_match"}}
    )

    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
      function_args = json.loads(tool_calls[0].function.arguments)
      best_match_index = function_args['best_match_index'] - 1  # Convert to 0-based index
      if 0 <= best_match_index < len(search_results):
        return {**search_results[best_match_index], 'correct_title': function_args['correct_title']}

    logger.error(f"[{query}] No suitable match found: {function_args.get('explanation', 'No explanation provided')}")

  except Exception as e:
    logger.error(f"[{query}] Error in LLM decision: {e}")
    
  return None
