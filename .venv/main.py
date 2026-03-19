import tmdbsimple as tmdb

from dotenv import load_dotenv
import pprint
import os

load_dotenv()

# tmdbsimple config
tmdb.API_KEY = os.getenv('TMDB_API_KEY')
tmdb.REQUESTS_TIMEOUT = 5


def popular_movies_by_date(start_date, end_date):
    """
    Date format: 'YYYY-MM-DD'

    Example (Year of 2016): popular_movies_by_date('2016-01-01', '2016-12-31')
    """
    discover = tmdb.Discover()
    discover_kwargs = {
        'primary_release_date.gte': start_date,
        'primary_release_date.lte': end_date,
        'sort_by': 'popularity.desc'
    }

    return discover.movie(**discover_kwargs)

# Testing for year of 2025
response1 = popular_movies_by_date('2025-01-01', '2025-12-31')
pprint.pp(response1['results'][:3])
# For some reason Avatar: Fire and Ash doesn't appear on this list or,
# even in the documentations testing environment: https://developer.themoviedb.org/reference/discover-movie
# Still need to discuss what result we're expecting so we know what to filter by, but this is a start for gathering data
