import requests
import os
from django.conf import settings

def get_poster_url(movie_title):
    """
    Fetch the movie poster URL from TMDB based on movie title.
    """
    api_key = settings.TMDB_API_KEY
    base_url = "https://api.themoviedb.org/3/search/movie"
    image_base = "https://image.tmdb.org/t/p/w500"

    try:
        response = requests.get(base_url, params={"api_key": api_key, "query": movie_title})
        response.raise_for_status()
        data = response.json()

        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"{image_base}{poster_path}"
    except Exception as e:
        print(f"TMDB error for {movie_title}: {e}")

    return None
