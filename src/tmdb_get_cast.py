import requests
import csv
import os

API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYmQ1ZjIwYzk3MGIyYjkyZDg5NzYzMWM4YTM2OGY3NCIsIm5iZiI6MTc3Mzc2OTI0MS4yNTMsInN1YiI6IjY5Yjk5MjE5MWU2ZmEzMDcyNDAyMGI1MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.p8rv2Ugv-X1aHkzWcXaTChcSGXHZ4x5Rxs-sdNaoELo"

DECADES = [1990, 2010]
GENRES = ["Action", "Drama", "Comedy"]

MOVIES_PER_GENRE = 20
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

print("Loading genre list...", flush=True)
genre_data = get_json(f"{BASE_URL}/genre/movie/list")

genre_map = {}
for g in genre_data["genres"]:
    genre_map[g["name"].lower()] = g["id"]

movies_rows = []
cast_rows = []
seen_movie_ids = set()

for decade in DECADES:
    start_year = decade
    end_year = decade + 9

    for genre_name in GENRES:
        print(f"Getting {genre_name} movies from {decade}s...", flush=True)

        genre_id = genre_map[genre_name.lower()]

        page = 1
        selected_movies = []

        while len(selected_movies) < MOVIES_PER_GENRE:
            params = {
                "with_genres": genre_id,
                "primary_release_date.gte": f"{start_year}-01-01",
                "primary_release_date.lte": f"{end_year}-12-31",
                "sort_by": SORT_BY,
                "page": page
            }

            data = get_json(f"{BASE_URL}/discover/movie", params=params)
            results = data.get("results", [])

            if not results:
                break

            for movie in results:
                movie_id = movie["id"]

                if movie_id in seen_movie_ids:
                    continue

                seen_movie_ids.add(movie_id)
                selected_movies.append(movie)

                if len(selected_movies) == MOVIES_PER_GENRE:
                    break

            page += 1

        for i, movie in enumerate(selected_movies, start=1):
            movie_id = movie["id"]
            title = movie.get("title", "")
            release_date = movie.get("release_date", "")

            print(f"  [{i}/{len(selected_movies)}] {title}", flush=True)

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

print(f"Done. Files saved in: {OUTPUT_DIR}", flush=True)