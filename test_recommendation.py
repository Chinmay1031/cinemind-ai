from app.services.recommendation_service import generate_movie_recommendations

query = "I want emotional sci-fi movies with deep philosophical themes"

result = generate_movie_recommendations(query)

print(result)
