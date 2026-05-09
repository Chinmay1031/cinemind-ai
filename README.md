# CineMind AI — Movie Recommendation Agent

A Retrieval-Augmented Generation (RAG) project that combines OpenAI's GPT-4o-mini, TMDB's movie database, and a Streamlit frontend to deliver personalized movie recommendations with real poster images.

Built as a project to explore LLMs, semantic search, and API integration.

## What It Does

1. User describes the kind of movie they want (e.g. *"a fun comedy with no serious tone"*)
2. GPT-4o-mini generates tailored recommendations and streams them to the UI in real time
3. Each recommended title is looked up on TMDB to fetch the official poster, rating, and release date
4. Results are displayed as styled horizontal cards with explanations

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Semantic Search | FAISS + Sentence Transformers |
| Movie Data | TMDB API |
| Frontend | Streamlit |
| Backend | FastAPI |

---

## Project Structure

```
AI Agent Movie/
├── app/
│   ├── services/
│   │   ├── recommendation_service.py  # LLM streaming + movie extraction
│   │   ├── search_service.py          # FAISS semantic search index
│   │   └── tmdb_service.py            # TMDB API calls
│   └── embeddings/
│       └── embed_movies.py            # Movie embedding generation
├── frontend/
│   └── streamlit_app.py               # UI — streaming cards + slider
├── requirements.txt
└── .env
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd "AI Agent Movie"
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add API keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_key_here
TMDB_API_KEY=your_tmdb_key_here
```

- Get an OpenAI key at [platform.openai.com](https://platform.openai.com)
- Get a free TMDB key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)

### 3. Run the app

```bash
streamlit run frontend/streamlit_app.py
```

---

## How It Works (RAG Flow)

```
User Query
    │
    ▼
GPT-4o-mini  ──►  Streams intro text to UI in real time
    │
    ▼
Structured JSON  (title + year + explanation per movie)
    │
    ▼
TMDB Search API  ──►  Fetches poster, rating, release date
    │
    ▼
Horizontal Movie Cards rendered in Streamlit
```

The FAISS index is built from movies fetched across 8 genres (Comedy, Drama, Action, Romance, Thriller, Animation, Horror, Sci-Fi) to keep the search results diverse.

---

## Features

- **Streaming response** — text appears token by token, no waiting for the full response
- **Dynamic count** — slider to choose between 1 and 15 recommendations
- **Matched posters** — posters always correspond to the movies the LLM actually recommended
- **Dark movie cards** — each card shows poster, star rating, release date, and a tailored explanation

---

## Environment

- Python 3.10+
- Tested on macOS

---

## Learnings

This project covers:
- Building a RAG pipeline from scratch (embedding → FAISS → LLM)
- Streaming LLM responses to a web UI
- Chaining external APIs (OpenAI + TMDB)
- Parsing structured LLM output reliably
- Styling Streamlit apps with custom HTML/CSS
