import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from app.services.tmdb_service import search_movies_by_title

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

_PROMPT_TEMPLATE = """
A user is looking for movie recommendations.

User Query:
{user_query}

Write a short 1-2 sentence intro acknowledging the user's mood/request.

Then recommend exactly {count} movies. At the very end output ONLY this JSON block and nothing after it:
```json
{{
  "movies": [
    {{
      "title": "Exact Movie Title",
      "year": "YYYY",
      "explanation": "2-3 sentence explanation of why this movie fits the request."
    }}
  ]
}}
```
"""


def _fetch_tmdb_data(title):
    result = search_movies_by_title(title)
    movies = result.get("results", [])
    if not movies:
        return None
    movie = movies[0]
    return {
        "title": movie.get("title"),
        "poster_path": movie.get("poster_path"),
        "rating": movie.get("vote_average"),
        "release_date": movie.get("release_date"),
    }


def stream_intro(user_query, count=5):
    """Streams only the intro text (everything before the JSON block)."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert cinematic AI recommendation assistant."},
            {"role": "user", "content": _PROMPT_TEMPLATE.format(user_query=user_query, count=count)},
        ],
        temperature=0.7,
        stream=True,
    )

    full_text = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_text += content
            yield content, full_text


def extract_movies_from_text(full_text):
    """Parse the JSON block and enrich each movie with TMDB poster data."""
    try:
        json_start = full_text.rfind("```json")
        json_end = full_text.rfind("```", json_start + 1)
        if json_start != -1 and json_end != -1:
            json_str = full_text[json_start + 7:json_end].strip()
            movies = json.loads(json_str).get("movies", [])
        else:
            return []
    except (json.JSONDecodeError, ValueError):
        return []

    enriched = []
    seen = set()
    for movie in movies:
        title = movie.get("title", "")
        if title in seen:
            continue
        seen.add(title)
        tmdb = _fetch_tmdb_data(title)
        if tmdb and tmdb.get("poster_path"):
            enriched.append({
                "title": tmdb["title"],
                "year": movie.get("year", ""),
                "explanation": movie.get("explanation", ""),
                "poster_path": tmdb["poster_path"],
                "rating": tmdb["rating"],
                "release_date": tmdb["release_date"],
            })

    return enriched
