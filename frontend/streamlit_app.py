import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

try:
    for _k, _v in st.secrets.items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass

from audio_recorder_streamlit import audio_recorder
from app.services.recommendation_service import stream_intro, extract_movies_from_text
from app.services.whisper_service import transcribe_audio

st.set_page_config(page_title="CineMind AI", layout="wide", page_icon="🎬")

st.markdown("""
<style>
/* ── Layout ──────────────────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 900px;
}

/* ── Text input ──────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #e94560 !important;
    box-shadow: 0 0 0 3px rgba(233,69,96,0.1) !important;
}

/* ── All widget labels ───────────────────────────────────────────────────── */
[data-testid="stTextInput"] label,
[data-testid="stSlider"]    label,
[data-testid="stSelectbox"] label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* ── Slider accent ───────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] { background: #e94560 !important; }
[data-testid="stSlider"] [data-testid="stTickBar"] { display: none; }

/* ── Audio recorder ──────────────────────────────────────────────────────── */
[data-testid="stCustomComponentV1"] {
    border: 1.5px solid #e0e0e0 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stCustomComponentV1"] iframe { display: block !important; border-radius: 8px !important; }

/* ── Buttons ─────────────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #e94560 0%, #b8273e 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    box-shadow: 0 3px 14px rgba(233,69,96,0.25) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(233,69,96,0.38) !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* ── Movie cards ─────────────────────────────────────────────────────────── */
.movie-card {
    display: flex;
    gap: 1.25rem;
    background: #f8f9fb;
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.85rem;
    align-items: flex-start;
    border-left: 4px solid #e94560;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    transition: box-shadow 0.2s ease;
}
.movie-card:hover { box-shadow: 0 6px 24px rgba(233,69,96,0.12); }
.movie-card img { width: 90px; min-width: 90px; border-radius: 8px; object-fit: cover; }
.movie-info h3 { margin: 0 0 0.2rem 0; font-size: 1.1rem; color: #1a1a2e; }
.movie-meta { font-size: 0.78rem; color: #888; margin-bottom: 0.55rem; }
.movie-explanation { font-size: 0.88rem; color: #444; line-height: 1.55; margin: 0; }
.star { color: #f5c518; }
.providers { display: flex; gap: 0.35rem; margin-top: 0.7rem; align-items: center; flex-wrap: wrap; }
.provider-badge {
    font-size: 0.7rem;
    font-weight: 600;
    color: #333;
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 3px 10px;
    white-space: nowrap;
}
.genre-tag {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 600;
    color: #e94560;
    background: rgba(233,69,96,0.08);
    border: 1px solid rgba(233,69,96,0.2);
    border-radius: 20px;
    padding: 2px 9px;
    margin-right: 4px;
}
.mood-tag {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 600;
    color: #555;
    background: #f0f0f0;
    border-radius: 20px;
    padding: 2px 9px;
}
.plot-summary {
    font-size: 0.82rem;
    color: #666;
    font-style: italic;
    line-height: 1.5;
    margin: 0.35rem 0 0.5rem;
    padding-left: 0.65rem;
    border-left: 2px solid #e8e8e8;
}
</style>
""", unsafe_allow_html=True)

# ── Hero header ────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:2.5rem 0 2rem;">
    <div style="font-size:0.7rem; font-weight:700; letter-spacing:0.2em; color:#e94560;
                text-transform:uppercase; margin-bottom:1.1rem;">
        Powered by GPT-4o · Whisper · TMDB
    </div>
    <h1 style="font-size:3rem; font-weight:800; letter-spacing:-0.03em; line-height:1.1;
               margin:0; color:#1a1a2e;">
        🎬 CineMind AI
    </h1>
    <p style="color:#888; font-size:1rem; margin:0.8rem 0 0; font-weight:400;">
        Tell us what you're in the mood for — we'll find the perfect film.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Voice input (Whisper) ──────────────────────────────────────────────────
if "voice_query" not in st.session_state:
    st.session_state.voice_query = ""
if "processed_audio" not in st.session_state:
    st.session_state.processed_audio = None

query = st.text_input(
    "What are you in the mood for?",
    value=st.session_state.voice_query,
    placeholder="e.g. a slow-burn psychological thriller with an unexpected ending…",
)

mic_col, _ = st.columns([1, 9])
with mic_col:
    audio_bytes = audio_recorder(
        text="",
        pause_threshold=2.0,
        icon_size="sm",
        neutral_color="#e94560",
        recording_color="#ff6b8a",
    )

if audio_bytes and audio_bytes != st.session_state.processed_audio:
    st.session_state.processed_audio = audio_bytes
    with st.spinner("Transcribing your voice..."):
        transcribed = transcribe_audio(audio_bytes)
    if transcribed:
        st.session_state.voice_query = transcribed
        st.rerun()

col1, col2 = st.columns([3, 1])
with col1:
    num_recommendations = st.slider("Number of recommendations", min_value=1, max_value=15, value=5)
with col2:
    country = st.selectbox("Region", ["US", "IN", "GB", "CA", "AU", "DE", "FR", "JP"], index=0)

st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

# ── Trigger logic ──────────────────────────────────────────────────────────
if "current_movie_titles" not in st.session_state:
    st.session_state.current_movie_titles = []
if "pending_excluded" not in st.session_state:
    st.session_state.pending_excluded = None

if st.button("Get Recommendations", use_container_width=True):
    st.session_state.pending_excluded = []

if st.session_state.pending_excluded is not None:
    excluded = st.session_state.pending_excluded
    st.session_state.pending_excluded = None

    # ── Streaming intro ────────────────────────────────────────────────────
    intro_placeholder = st.empty()
    full_text = ""

    for chunk, accumulated in stream_intro(query, num_recommendations, excluded_titles=excluded):
        full_text = accumulated
        json_start = full_text.rfind("```json")
        display = full_text[:json_start].strip() if json_start != -1 else full_text
        intro_placeholder.markdown(display + " ▌")

    json_start = full_text.rfind("```json")
    display = full_text[:json_start].strip() if json_start != -1 else full_text
    intro_placeholder.markdown(display)

    # ── Movie cards ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Recommended for you")

    with st.spinner("Fetching movie details..."):
        movies = extract_movies_from_text(full_text, country=country)

    if movies:
        st.session_state.current_movie_titles = [m["title"] for m in movies]
        for movie in movies:
            poster_url = f"https://image.tmdb.org/t/p/w200{movie['poster_path']}"
            rating = movie.get("rating") or 0
            stars = "★" * round(rating / 2) + "☆" * (5 - round(rating / 2))
            year = movie.get("year") or (movie.get("release_date") or "")[:4]

            director  = movie.get("director", "")
            mood      = movie.get("mood", "")
            cast_str  = ", ".join(movie.get("cast", []))
            plot_summary = movie.get("plot_summary", "")
            explanation  = movie.get("explanation", "")
            genre_badges = "".join(f'<span class="genre-tag">{g}</span>' for g in movie.get("genres", []))

            providers = movie.get("providers", [])
            if providers:
                badges = "".join(f'<span class="provider-badge">{p["provider_name"]}</span>' for p in providers[:6])
                providers_html = f'<div class="providers"><span style="font-size:0.7rem;color:#888;margin-right:0.4rem;">Stream on</span>{badges}</div>'
            else:
                providers_html = '<div style="font-size:0.72rem;color:#aaa;margin-top:0.6rem;">Not available on streaming in this region</div>'

            # Build inner HTML as one continuous string — no blank lines (breaks CommonMark HTML block parsing)
            info = f'<h3>{movie["title"]} <span style="font-weight:400;color:#999;">({year})</span></h3>'
            info += f'<div class="movie-meta"><span class="star">{stars}</span>&nbsp;{rating:.1f}&nbsp;&nbsp;·&nbsp;&nbsp;{movie.get("release_date", "N/A")}</div>'
            if director or mood:
                parts = []
                if director:
                    parts.append(f'<span style="font-weight:600;">Dir.</span> {director}')
                if mood:
                    parts.append(f'<span class="mood-tag">{mood}</span>')
                info += f'<div style="font-size:0.78rem;color:#666;margin:0.3rem 0 0.35rem;">{"&nbsp;·&nbsp;".join(parts)}</div>'
            if genre_badges:
                info += f'<div style="margin-bottom:0.4rem;">{genre_badges}</div>'
            if cast_str:
                info += f'<div style="font-size:0.76rem;color:#999;margin-bottom:0.4rem;">👥 {cast_str}</div>'
            if plot_summary:
                info += f'<p class="plot-summary">{plot_summary}</p>'
            info += f'<p class="movie-explanation">{explanation}</p>'
            info += providers_html

            st.markdown(
                f'<div class="movie-card"><img src="{poster_url}" alt="{movie["title"]} poster" /><div class="movie-info">{info}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("Refresh — show me different movies", use_container_width=True):
            st.session_state.pending_excluded = list(st.session_state.current_movie_titles)
            st.rerun()
    else:
        st.info("Could not fetch poster data for the recommendations.")
