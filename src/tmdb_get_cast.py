import requests
import csv
import os

API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYmQ1ZjIwYzk3MGIyYjkyZDg5NzYzMWM4YTM2OGY3NCIsIm5iZiI6MTc3Mzc2OTI0MS4yNTMsInN1YiI6IjY5Yjk5MjE5MWU2ZmEzMDcyNDAyMGI1MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.p8rv2Ugv-X1aHkzWcXaTChcSGXHZ4x5Rxs-sdNaoELo"

DECADES = [1990, 2010]
GENRES = ["Action", "Drama", "Comedy"]

MOVIES_PER_GENRE = 3
TOP_CAST = 5
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "data")
SORT_BY = "popularity.desc"

BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

def get_json(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r.json()

genre_data = get_json(f"{BASE_URL}/genre/movie/list")
genre_map = {}
for g in genre_data["genres"]:
    genre_map[g["name"].lower()] = g["id"]

movies_rows = []
cast_rows = []

for decade in DECADES:
    start_year = decade
    end_year = decade + 9

    for genre_name in GENRES:
        genre_id = genre_map[genre_name.lower()]

        params = {
            "with_genres": genre_id,
            "primary_release_date.gte": f"{start_year}-01-01",
            "primary_release_date.lte": f"{end_year}-12-31",
            "sort_by": SORT_BY,
            "page": 1
        }

        data = get_json(f"{BASE_URL}/discover/movie", params=params)
        results = data["results"][:MOVIES_PER_GENRE]

        for movie in results:
            movie_id = movie["id"]
            title = movie.get("title", "")
            release_date = movie.get("release_date", "")

            movies_rows.append({
                "movie_id": movie_id,
                "title": title,
                "release_date": release_date,
                "decade": decade,
                "genre": genre_name
            })

            credits = get_json(f"{BASE_URL}/movie/{movie_id}/credits")
            cast_list = credits.get("cast", [])[:TOP_CAST]

            for actor in cast_list:
                cast_rows.append({
                    "movie_id": movie_id,
                    "title": title,
                    "actor_id": actor.get("id"),
                    "actor_name": actor.get("name", "")
                })

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(f"{OUTPUT_DIR}/movies.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["movie_id", "title", "release_date", "decade", "genre"]
    )
    writer.writeheader()
    writer.writerows(movies_rows)

with open(f"{OUTPUT_DIR}/cast.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["movie_id", "title", "actor_id", "actor_name"]
    )
    writer.writeheader()
    writer.writerows(cast_rows)

print(f"movies.csv and cast.csv saved in: {OUTPUT_DIR}")