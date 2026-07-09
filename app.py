import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "telugu_music_secret_key")

MY_USERNAME = os.getenv("MY_USERNAME", "karuna")
MY_PASSWORD = os.getenv("MY_PASSWORD", "MySecretPassword123")

# Updated Telugu Hit Songs Database
TELUGU_SONGS = [
    {
        "id": 1,
        "title": "Fear Song",
        "movie": "Devara",
        "artist": "Anirudh Ravichander",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "cover": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300"
    },
    {
        "id": 2,
        "title": "Chuttamalle",
        "movie": "Devara",
        "artist": "Shreya Ghoshal",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "cover": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300"
    },
    {
        "id": 3,
        "title": "Kurchi Madathapetti",
        "movie": "Guntur Kaaram",
        "artist": "Thaman S, Sahithi Chaganti",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "cover": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300"
    },
    {
        "id": 4,
        "title": "Pushpa Pushpa",
        "movie": "Pushpa 2 The Rule",
        "artist": "Nakash Aziz, DSP",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        "cover": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300"
    },
    {
        "id": 5,
        "title": "Sooseki",
        "movie": "Pushpa 2 The Rule",
        "artist": "Shreya Ghoshal",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
        "cover": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300"
    },
    {
        "id": 6,
        "title": "Samayama",
        "movie": "Hi Nanna",
        "artist": "Anurag Kulkarni",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
        "cover": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=300"
    }
]

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", user=session["user"], songs=TELUGU_SONGS)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username == MY_USERNAME and password == MY_PASSWORD:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            flash(f"Invalid login! Attempted: '{username}'")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
