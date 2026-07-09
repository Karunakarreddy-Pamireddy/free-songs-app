import streamlit as st
import requests

# Point to your active FastAPI backend instance
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="FreeSongs - Stream Unlimited Music",
    page_icon="🎵",
    layout="centered"
)

# Application Branding Headers
st.title("🎵 FreeSongs Player")
st.markdown("##### Stream your favorite AI-generated music tracks with absolute zero buffering.")
st.markdown("---")

# Fetch available music tracks from our backend server catalog
try:
    response = requests.get(f"{API_URL}/songs")
    if response.status_code == 200:
        song_list = response.json()
    else:
        song_list = []
        st.error("Failed to sync music catalog from backend cluster services.")
except requests.exceptions.ConnectionError:
    song_list = []
    st.warning("⚠️ Streaming services offline. Please make sure your FastAPI server is active on port 8000.")

# Build layout if tracks are discovered
if song_list:
    # --- SEARCH & FILTER FILTER WRAPPER ---
    search_query = st.text_input("🔍 Search for a song track...", "").strip()
    
    # Filter songs based on search entry
    filtered_songs = [song for song in song_list if search_query.lower() in song.lower()] if search_query else song_list

    if not filtered_songs:
        st.info("No tracks found matching your search query criteria.")
    else:
        st.markdown(f"**Available Catalog Tracks ({len(filtered_songs)}):**")
        
        # --- TRACK RENDER CARD MATRIX ---
        for index, song_name in enumerate(filtered_songs):
            # Clean up extensions for user aesthetics
            display_title = song_name.replace(".mp3", "").replace("_", " ").title()
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{index + 1}. {display_title}**")
                    # Construct our Day 4 live chunked streaming URL point
                    stream_url = f"{API_URL}/stream/{song_name}"
                    # Feed streaming URL into the browser's native hardware audio node
                    st.audio(stream_url, format="audio/mp3")
                    
                with col2:
                    st.write("") # Padding spacing
                    download_url = f"{API_URL}/download/{song_name}"
                    # Provide an aesthetic download link button pointing to the file system download route
                    st.link_button("📥 Download", download_url, use_container_width=True)
else:
    st.info("💿 The catalog storage cluster is currently empty. Fire up your upload bot to inject some music!")

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)