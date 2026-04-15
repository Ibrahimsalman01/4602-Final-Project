import requests
import csv
import os
import re
import time

API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYmQ1ZjIwYzk3MGIyYjkyZDg5NzYzMWM4YTM2OGY3NCIsIm5iZiI6MTc3Mzc2OTI0MS4yNTMsInN1YiI6IjY5Yjk5MjE5MWU2ZmEzMDcyNDAyMGI1MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.p8rv2Ugv-X1aHkzWcXaTChcSGXHZ4x5Rxs-sdNaoELo"

TOP_CAST = 5

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "data")

BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

LIST_FILES = {
    (1990, "Action"): "1990sAction.txt",
    (1990, "Comedy"): "1990sComedy.txt",
    (1990, "Drama"): "1990sDrama.txt",
    (2000, "Action"): "2000sAction.txt",
    (2000, "Comedy"): "2000sComedy.txt",
    (2000, "Drama"): "2000sDrama.txt",
    (2010, "Action"): "2010sAction.txt",
    (2010, "Comedy"): "2010sComedy.txt",
    (2010, "Drama"): "2010sDrama.txt",
}

def get_json(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()

def parse_movie_line(line):
    line = line.strip()
    if not line:
        return None, None

    match = re.match(r"^(.*)\s+(\d{4})$", line)
    if not match:
        return line, None

    title = match.group(1).strip()
    year = int(match.group(2))
    return title, year

def read_movie_list(filepath):
    movies = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            title, year = parse_movie_line(line)
            if title:
                movies.append((title, year))
    return movies

def search_movie(title, year=None):
    params = {
        "query": title,
        "include_adult": "false"
    }

    if year is not None:
        params["year"] = year

    data = get_json(f"{BASE_URL}/search/movie", params=params)
    results = data.get("results", [])

    if not results:
        return None

    for movie in results:
        movie_title = movie.get("title", "").strip().lower()
        release_date = movie.get("release_date", "")
        movie_year = None

        if release_date and len(release_date) >= 4:
            try:
                movie_year = int(release_date[:4])
            except ValueError:
                pass

        if movie_title == title.strip().lower() and movie_year == year:
            return movie

    for movie in results:
        release_date = movie.get("release_date", "")
        movie_year = None

        if release_date and len(release_date) >= 4:
            try:
                movie_year = int(release_date[:4])
            except ValueError:
                pass

        if movie_year == year:
            return movie

    return results[0]

movies_rows = []
cast_rows = []
seen_movie_ids = set()

print("Reading local movie lists...", flush=True)

for (decade, genre), filename in LIST_FILES.items():
    filepath = os.path.join(DATA_DIR, filename)

    print(f"\nLoading {filename}...", flush=True)

    local_movies = read_movie_list(filepath)

    for i, (title, year) in enumerate(local_movies, start=1):
        print(f"  [{i}/{len(local_movies)}] Searching: {title} ({year})", flush=True)

        movie = search_movie(title, year)

        if movie is None:
            print(f"    Not found: {title} ({year}) | {decade}s | {genre}", flush=True)
            continue

        movie_id = movie.get("id")
        tmdb_title = movie.get("title", "")
        release_date = movie.get("release_date", "")

        if movie_id in seen_movie_ids:
            print(f"    Skipped duplicate movie id: {tmdb_title}", flush=True)
            continue

        seen_movie_ids.add(movie_id)

        movies_rows.append({
            "movie_id": movie_id,
            "title": tmdb_title,
            "release_date": release_date,
            "decade": decade,
            "genre": genre
        })

        credits = get_json(f"{BASE_URL}/movie/{movie_id}/credits")
        cast_list = credits.get("cast", [])[:TOP_CAST]

        for actor in cast_list:
            cast_rows.append({
                "movie_id": movie_id,
                "title": tmdb_title,
                "actor_id": actor.get("id"),
                "actor_name": actor.get("name", "")
            })

        time.sleep(0.15)

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(os.path.join(OUTPUT_DIR, "movies.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["movie_id", "title", "release_date", "decade", "genre"]
    )
    writer.writeheader()
    writer.writerows(movies_rows)

with open(os.path.join(OUTPUT_DIR, "cast.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["movie_id", "title", "actor_id", "actor_name"]
    )
    writer.writeheader()
    writer.writerows(cast_rows)

print("\nDone.", flush=True)
print(f"movies.csv saved to: {OUTPUT_DIR}", flush=True)
print(f"cast.csv saved to: {OUTPUT_DIR}", flush=True)