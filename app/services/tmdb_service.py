import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"


def get_popular_movies(page=1):
    url = f"{BASE_URL}/movie/popular"

    params = {
        "api_key": API_KEY,
        "page": page
    }

    response = requests.get(url, params=params)

    return response.json()


def get_movies_by_genre(genre_id, page=1):
    url = f"{BASE_URL}/discover/movie"

    params = {
        "api_key": API_KEY,
        "with_genres": genre_id,
        "sort_by": "vote_count.desc",
        "page": page
    }

    response = requests.get(url, params=params)

    return response.json()


def search_movies_by_title(title):
    url = f"{BASE_URL}/search/movie"

    params = {
        "api_key": API_KEY,
        "query": title,
        "include_adult": False
    }

    response = requests.get(url, params=params)

    return response.json()