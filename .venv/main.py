import tmdbsimple as tmdb

from dotenv import load_dotenv
import os

load_dotenv()

# tmdbsimple config
tmdb.API_KEY = os.getenv('TMDB_API_KEY')
tmdb.REQUESTS_TIMEOUT = 5

# grabbing inception
# CHECK /find IN THE TMDB DOCS
search = tmdb.Search()
response = search.movie(query='The Bourne')

for s in search.results:
    print(s['title'], s['id'], s['release_date'], s['popularity'])
