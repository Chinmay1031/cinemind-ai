from app.services.search_service import semantic_movie_search

query = "dark emotional sci-fi movies"

results = semantic_movie_search(query)

print("\\nRecommended Movies:\\n")

for movie in results:
    print(movie)
    