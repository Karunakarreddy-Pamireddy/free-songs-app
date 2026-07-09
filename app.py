import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "telugu_music_secret_key")

MY_USERNAME = os.getenv("MY_USERNAME", "karuna")
MY_PASSWORD = os.getenv("MY_PASSWORD", "MySecretPassword123")

TELUGU_SONGS = [
    {
        "id": 1,
        "title": "Chuttamalle",
        "movie": "Devara",
        "artist": "Shreya Ghoshal, Anirudh",
        "url": "/static/music/chuttamalle.mp3",
        "cover": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300",
        "lyrics": """Chuttamalle suttu muttai cheerakattu
Gundelona reppalotu allukuttu
Soodu soodu rangulaata jorugattu
Aahaa manase aagakunda paatu paatu...
Nee chupe oka tana tana
Naa kalale oka sarigama!"""
    },
    {
        "id": 2,
        "title": "Kurchi Madathapetti",
        "movie": "Guntur Kaaram",
        "artist": "Thaman S, Sahithi Chaganti",
        "url": "/static/music/kurchi.mp3",
        "cover": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300",
        "lyrics": """Kurchi madathapetti...
Massu step-u vesi kottu beat-u petti
Aata paata anni inga joru katti
Raa raa maava chudu crazy setup petti!
Ee roju manade thaggede le!"""
    },
    {
        "id": 3,
        "title": "Samayama",
        "movie": "Hi Nanna",
        "artist": "Anurag Kulkarni",
        "url": "/static/music/samayama.mp3",
        "cover": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=300",
        "lyrics": """Samayamaa koncham aagumaa
Nee payanam aapumaa...
Ivala kalisaa nenu tanani
Gundello preme nindi paarenaa!"""
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
            flash("Invalid login credentials!")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
