from app.services.tmdb_service import get_popular_movies

movies = get_popular_movies()

for movie in movies["results"][:5]:
    print(movie["title"])