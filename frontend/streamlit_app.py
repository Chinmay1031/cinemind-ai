import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

# Streamlit Cloud doesn't load .env files; inject secrets into os.environ
# before services are imported so module-level os.getenv() calls pick up
# the correct values (API_KEY = os.getenv(...) runs at import time).
try:
    for _k, _v in st.secrets.items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass  # local dev uses .env via python-dotenv

from app.services.recommendation_service import stream_intro, extract_movies_from_text

st.set_page_config(page_title="CineMind AI", layout="wide")

# ── Global card styles 
st.markdown("""
<style>
.movie-card {
    display: flex;
    gap: 1.25rem;
    background: #1a1a2e;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    align-items: flex-start;
    border-left: 4px solid #e94560;
}
.movie-card img {
    width: 90px;
    min-width: 90px;
    border-radius: 8px;
    object-fit: cover;
}
.movie-info h3 {
    margin: 0 0 0.2rem 0;
    font-size: 1.15rem;
    color: #ffffff;
}
.movie-meta {
    font-size: 0.8rem;
    color: #aaaaaa;
    margin-bottom: 0.6rem;
}
.movie-explanation {
    font-size: 0.9rem;
    color: #cccccc;
    line-height: 1.5;
    margin: 0;
}
.star { color: #f5c518; }
.providers {
    display: flex;
    gap: 0.4rem;
    margin-top: 0.75rem;
    align-items: center;
    flex-wrap: wrap;
}
.provider-badge {
    font-size: 0.72rem;
    font-weight: 600;
    color: #ffffff;
    background: #2a2a3d;
    border: 1px solid #444466;
    border-radius: 20px;
    padding: 3px 10px;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 CineMind AI")
st.subheader("Your AI-powered cinema recommendation assistant")

query = st.text_input("Describe the kind of movie you want to watch:")

col1, col2 = st.columns([3, 1])
with col1:
    num_recommendations = st.slider("How many recommendations?", min_value=1, max_value=15, value=5)
with col2:
    country = st.selectbox("Your country", ["US", "IN", "GB", "CA", "AU", "DE", "FR", "JP"], index=0)

if st.button("Get Recommendations"):

    # ── Streaming intro ────────────────────────────────────────────────────
    intro_placeholder = st.empty()
    full_text = ""

    for chunk, accumulated in stream_intro(query, num_recommendations):
        full_text = accumulated

        # Strip the JSON block in real time so it never appears
        json_start = full_text.rfind("```json")
        display = full_text[:json_start].strip() if json_start != -1 else full_text
        intro_placeholder.markdown(display + " ▌")

    json_start = full_text.rfind("```json")
    display = full_text[:json_start].strip() if json_start != -1 else full_text
    intro_placeholder.markdown(display)

    # ── Horizontal movie cards ─────────────────────────────────────────────
    st.divider()
    st.subheader("Recommended Movies")

    with st.spinner("Fetching movie details..."):
        movies = extract_movies_from_text(full_text, country=country)

    if movies:
        for movie in movies:
            poster_url = f"https://image.tmdb.org/t/p/w200{movie['poster_path']}"
            rating = movie.get("rating") or 0
            stars = "★" * round(rating / 2) + "☆" * (5 - round(rating / 2))
            year = movie.get("year") or (movie.get("release_date") or "")[:4]
            explanation = movie.get("explanation", "")

            providers = movie.get("providers", [])
            if providers:
                badges = "".join(
                    f'<span class="provider-badge">{p["provider_name"]}</span>'
                    for p in providers[:6]
                )
                providers_html = f'<div class="providers"><span style="font-size:0.75rem;color:#aaa;margin-right:0.4rem;">Stream on:</span>{badges}</div>'
            else:
                providers_html = '<div style="font-size:0.75rem;color:#555;margin-top:0.6rem;">Not available on streaming in this region</div>'

            st.markdown(f"""
<div class="movie-card">
  <img src="{poster_url}" alt="{movie['title']} poster" />
  <div class="movie-info">
    <h3>{movie['title']} <span style="font-weight:400;color:#aaa;">({year})</span></h3>
    <div class="movie-meta">
      <span class="star">{stars}</span>&nbsp;{rating:.1f}&nbsp;&nbsp;·&nbsp;&nbsp;📅 {movie.get('release_date', 'N/A')}
    </div>
    <p class="movie-explanation">{explanation}</p>
    {providers_html}
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("Could not fetch poster data for the recommendations.")
