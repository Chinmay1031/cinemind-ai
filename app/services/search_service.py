from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from app.services.tmdb_service import get_movies_by_genre

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Genre IDs: Comedy, Drama, Action, Romance, Thriller, Animation, Horror, Sci-Fi
GENRE_IDS = [35, 18, 28, 10749, 53, 16, 27, 878]

movies_data = []
seen_ids = set()

for genre_id in GENRE_IDS:
    for page in range(1, 3):
        response = get_movies_by_genre(genre_id, page)
        for movie in response.get("results", []):
            movie_id = movie.get("id")
            if movie_id in seen_ids:
                continue
            seen_ids.add(movie_id)

            text = f"""
            Title: {movie.get('title', '')}
            Overview: {movie.get('overview', '')}
            Release Date: {movie.get('release_date', '')}
            Rating: {movie.get('vote_average', '')}
            """

            movies_data.append({
                "title": movie.get("title"),
                "overview": movie.get("overview"),
                "poster_path": movie.get("poster_path"),
                "rating": movie.get("vote_average"),
                "release_date": movie.get("release_date"),
                "text": text
            })

# Generate embeddings
texts = [movie["text"] for movie in movies_data]

embeddings = model.encode(texts)

embeddings = np.array(embeddings).astype("float32")

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)


def semantic_movie_search(query, top_k=5):

    query_embedding = model.encode([query])

    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    results = []

    for idx in indices[0]:
        results.append(movies_data[idx])

    return results
