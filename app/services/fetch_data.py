import requests
import os
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv('OMDB_API_KEY')


def fetch_movie_from_api(title):
    """
    Fetch movie data from OMDb API.
    Returns dict with title, year, rating, poster_url
    or None if movie not found.
    """
    if not API_KEY:
        print("Error: OMDb key not set.")

    url = "http://www.omdbapi.com/"
    params = {
        "apikey": API_KEY,
        "t": title
    }

    res = requests.get(url, params=params)
    data = res.json()

    return data
