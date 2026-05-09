from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from app.services.tmdb_service import get_popular_movies

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

movies_data = []

# Fetch multiple pages
for page in range(1, 6):
    response = get_popular_movies(page)

    for movie in response["results"]:

        text = f"""
        Title: {movie.get('title', '')}
        Overview: {movie.get('overview', '')}
        Release Date: {movie.get('release_date', '')}
        Rating: {movie.get('vote_average', '')}
        """

        movies_data.append({
            "title": movie.get("title"),
            "text": text
        })

# Generate embeddings
texts = [movie["text"] for movie in movies_data]

embeddings = model.encode(texts)

# Convert to numpy array
embeddings = np.array(embeddings).astype("float32")

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

print(f"Stored {len(movies_data)} movie embeddings in FAISS.")