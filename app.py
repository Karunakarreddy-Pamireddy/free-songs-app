import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "telugu_music_admin_secret")

ADMIN_USERNAME = os.getenv("MY_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("MY_PASSWORD", "admin123")

users_db = {
    ADMIN_USERNAME: {"password": ADMIN_PASSWORD, "role": "admin"}
}

TELUGU_SONGS = [
    {"id": 1, "title": "Chuttamalle", "movie": "Devara", "artist": "Shreya Ghoshal, Anirudh", "url": "https://archive.org/download/MellaMellaMellagaDaaguduMoothalu/Mella%20Mella%20Mellaga%20Daagudu%20Moothalu.mp3", "cover": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500"},
    {"id": 2, "title": "Kurchi Madathapetti", "movie": "Guntur Kaaram", "artist": "Thaman S, Sahithi", "url": "https://archive.org/download/NaaPaataNeeNotaMoogaManasulo1964/Naa_Paata_Nee_Nota-Mooga_Manasulo%281964%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=500"},
    {"id": 3, "title": "Samayama", "movie": "Hi Nanna", "artist": "Anurag Kulkarni", "url": "https://archive.org/download/NaaPaataNeeNotaMoogaManasulo1964/Naa_Rani_Kanulalone.mp3", "cover": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=500"},
    {"id": 4, "title": "Fear Song", "movie": "Devara", "artist": "Anirudh Ravichander", "url": "https://archive.org/download/NaaPaataNeeNotaMoogaManasulo1964/Naa_Manasu_Nee_Manasu_Okatai-CID%281965%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=500"},
    {"id": 5, "title": "Pushpa Pushpa", "movie": "Pushpa 2 The Rule", "artist": "Nakash Aziz, DSP", "url": "https://archive.org/download/pict_20221110_202211/A1%20-%20Jikki%20-%20Yeruvaaka.mp3", "cover": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500"}
]

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", user=session["user"], is_admin=(session.get("role") == "admin"), songs=TELUGU_SONGS)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username in users_db and users_db[username]["password"] == password:
            session["user"] = username
            session["role"] = users_db[username]["role"]
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials!")
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    if username and password:
        if username in users_db:
            flash("Username already exists!")
        else:
            users_db[username] = {"password": password, "role": "user"}
            flash("Registration successful! Please login.")
    return redirect(url_for("login"))

@app.route("/change_password", methods=["POST"])
def change_password():
    if "user" not in session:
        return redirect(url_for("login"))
    
    new_password = request.form.get("new_password", "").strip()
    if new_password:
        username = session["user"]
        users_db[username]["password"] = new_password
        flash("Password updated successfully!")
    return redirect(url_for("index"))

@app.route("/admin")
def admin_panel():
    if session.get("role") != "admin":
        flash("Access denied! Admin privileges required.")
        return redirect(url_for("index"))
    return render_template("admin.html", users=users_db, songs=TELUGU_SONGS)

@app.route("/add_song", methods=["POST"])
def add_song():
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    title = request.form.get("title")
    movie = request.form.get("movie")
    artist = request.form.get("artist")
    url = request.form.get("url")
    cover = request.form.get("cover")
    
    if title and url:
        new_id = len(TELUGU_SONGS) + 1
        TELUGU_SONGS.append({
            "id": new_id, "title": title, "movie": movie, "artist": artist, 
            "url": url, "cover": cover or "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500"
        })
        flash("Song added successfully!")
    return redirect(url_for("admin_panel"))

@app.route("/delete_song/<int:song_id>", methods=["POST"])
def delete_song(song_id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    global TELUGU_SONGS
    TELUGU_SONGS = [s for s in TELUGU_SONGS if s["id"] != song_id]
    flash("Song removed successfully!")
    return redirect(url_for("admin_panel"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
