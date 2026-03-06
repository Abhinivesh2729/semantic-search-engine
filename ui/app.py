import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

API_URL = os.getenv('DJANGO_API_URL', 'http://localhost:8010')

st.set_page_config(page_title="Semantic Search Engine", layout="wide")
st.title("Semantic Search Engine")
st.markdown("Compare keyword search vs semantic (meaning-based) search side by side.")

query = st.text_input("Search query", placeholder="e.g. how do computers communicate")
search_clicked = st.button("Search", type="primary")

if search_clicked and query:
    col_keyword, col_semantic = st.columns(2)

    with col_keyword:
        st.subheader("Keyword Search")
        try:
            start = time.time()
            resp = requests.get(f"{API_URL}/api/search/keyword", params={'q': query}, timeout=30)
            elapsed = round((time.time() - start) * 1000)
            data = resp.json()

            cached = data.get('cached', False)
            server_ms = data.get('time_ms', elapsed)
            results = data.get('results', [])

            if cached:
                st.caption(f"Served from cache")
            else:
                st.caption(f"Response: {server_ms}ms")

            if not results:
                st.info("No results found.")
            for r in results:
                with st.container(border=True):
                    st.markdown(f"**{r['title']}**")
                    if r.get('category'):
                        st.caption(r['category'])
                    st.write(r['content'])
        except requests.ConnectionError:
            st.error("Cannot connect to backend. Is it running on port 8010?")

    with col_semantic:
        st.subheader("Semantic Search")
        try:
            start = time.time()
            resp = requests.get(f"{API_URL}/api/search/semantic", params={'q': query}, timeout=30)
            elapsed = round((time.time() - start) * 1000)
            data = resp.json()

            cached = data.get('cached', False)
            server_ms = data.get('time_ms', elapsed)
            results = data.get('results', [])

            if cached:
                st.caption(f"Served from cache")
            else:
                st.caption(f"Response: {server_ms}ms")

            if not results:
                st.info("No results found.")
            for r in results:
                with st.container(border=True):
                    sim = r.get('similarity', 0)
                    st.markdown(f"**{r['title']}**")
                    col_cat, col_sim = st.columns([1, 1])
                    if r.get('category'):
                        col_cat.caption(r['category'])
                    col_sim.caption(f"Similarity: {sim:.2%}")
                    st.write(r['content'])
        except requests.ConnectionError:
            st.error("Cannot connect to backend. Is it running on port 8010?")

elif search_clicked:
    st.warning("Please enter a search query.")

st.divider()
st.markdown("#### Try these queries to see the difference")
st.markdown("""
- **`PostgreSQL`** — keyword search matches the exact word; semantic search also finds related database topics
- **`how do computers communicate`** — keyword search finds nothing; semantic search finds internet/networking docs
- **`staying fit`** — keyword search misses it; semantic search finds exercise and health articles
""")
