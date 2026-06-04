import streamlit as st
import json
import os
import importlib
import transcriber
importlib.reload(transcriber)
from transcriber import transcribe_audio, transcribe_youtube
from downloader import download_audio
from summarizer import summarize_transcript
from rag import build_vector_store, ask_question

st.set_page_config(
    page_title="Video Note Extractor",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0f0f0f; color: white; }
    .stTextInput > div > div > input { background-color: #2a2a2a !important; color: white !important; border: 1px solid #3a3a3a !important; border-radius: 10px !important; padding: 15px !important; font-size: 1rem !important; }
    .stButton > button { background: linear-gradient(90deg, #ff4b4b, #ff9d4b) !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 12px 30px !important; font-size: 1rem !important; font-weight: 600 !important; width: 100% !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1a1a; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #888 !important; border-radius: 8px !important; }
    .stTabs [aria-selected="true"] { background-color: #2a2a2a !important; color: white !important; }
    .stat-box { background: #2a2a2a; border-radius: 12px; padding: 20px; text-align: center; margin: 5px; }
    .stat-num { font-size: 2rem; font-weight: 800; color: #ff4b4b; }
    .stat-label { color: #888; font-size: 0.9rem; margin-top: 5px; }
    div[data-testid="stMarkdownContainer"] p { color: #ccc; line-height: 1.8; }
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 { color: white; }
    div[data-testid="stMarkdownContainer"] li { color: #ccc; }
    footer { visibility: hidden; }
    .stTextInput label { color: #888 !important; }
    .transcript-line { padding: 6px 0; border-bottom: 1px solid #2a2a2a; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 40px 0 30px 0;">
    <h1 style="font-size:3rem; font-weight:800; background:linear-gradient(90deg,#ff4b4b,#ff9d4b); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">Video Note Extractor</h1>
    <p style="color:#888; font-size:1.1rem; margin-top:10px;">Paste any YouTube URL and get AI-powered notes, timestamps and action items instantly</p>
</div>
""", unsafe_allow_html=True)

url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
extract = st.button("Extract Notes")

if extract:
    if url:
        with st.spinner("Fetching transcript from YouTube..."):
            segments = transcribe_youtube(url)

        if segments:
            with st.spinner("Generating notes with LLaMA 3..."):
                notes = summarize_transcript(segments)

            with st.spinner("Building Q&A database..."):
                build_vector_store(segments)

            st.session_state.segments = segments
            st.session_state.notes = notes
            st.success("Done! Your notes are ready.")
        else:
            st.error("Could not get transcript. Try another video.")

if "notes" in st.session_state:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(st.session_state.segments)}</div><div class="stat-label">Transcript segments</div></div>', unsafe_allow_html=True)
    with col2:
        duration = st.session_state.segments[-1]["end"] if st.session_state.segments else 0
        mins = int(duration // 60)
        st.markdown(f'<div class="stat-box"><div class="stat-num">{mins} min</div><div class="stat-label">Video duration</div></div>', unsafe_allow_html=True)
    with col3:
        words = sum(len(s["text"].split()) for s in st.session_state.segments)
        st.markdown(f'<div class="stat-box"><div class="stat-num">{words}</div><div class="stat-label">Words transcribed</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Notes", "Ask a Question", "Full Transcript"])

    with tab1:
        st.markdown(st.session_state.notes)
        st.download_button(
            label="Download Notes",
            data=st.session_state.notes,
            file_name="notes.md",
            mime="text/markdown"
        )

    with tab2:
        st.markdown("### Ask anything about this video")
        question = st.text_input("Your question", placeholder="e.g. What are the main topics covered?", key="question")
        if st.button("Ask AI"):
            if question:
                with st.spinner("Searching transcript..."):
                    answer = ask_question(question, st.session_state.segments)
                st.markdown(f"**Answer:** {answer}")

    with tab3:
        st.markdown("### Full Transcript with Timestamps")
        for seg in st.session_state.segments:
            minutes = int(seg["start"] // 60)
            seconds = int(seg["start"] % 60)
            st.markdown(f"`[{minutes:02d}:{seconds:02d}]` {seg['text']}")