import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "telugu_music_admin_secret")

# Admin credentials from .env or fallback
ADMIN_USERNAME = os.getenv("MY_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("MY_PASSWORD", "admin123")

# User database storing registered credentials
users_db = {
    ADMIN_USERNAME: {"password": ADMIN_PASSWORD, "role": "admin"}
}

# Pre-loaded 20 Telugu Songs Database with full vocal tracks
TELUGU_SONGS = [
    {"id": 1, "title": "Chuttamalle", "movie": "Devara", "artist": "Shreya Ghoshal, Anirudh", "url": "https://archive.org/download/MellaMellaMellagaDaaguduMoothalu/Mella%20Mella%20Mellaga%20Daagudu%20Moothalu.mp3", "cover": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500"},
    {"id": 2, "title": "Kurchi Madathapetti", "movie": "Guntur Kaaram", "artist": "Thaman S, Sahithi", "url": "https://archive.org/download/NaaPaataNeeNotaMoogaManasulo1964/Naa_Paata_Nee_Nota-Mooga_Manasulo%281964%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=500"},
    {"id": 3, "title": "Samayama", "movie": "Hi Nanna", "artist": "Anurag Kulkarni", "url": "https://archive.org/download/NaaPaataNeeNotaMoogaManasulo1964/Naa_Rani_Kanulalone.mp3", "cover": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=500"},
    {"id": 4, "title": "Fear Song", "movie": "Devara", "artist": "Anirudh Ravichander", "url": "https://archive.org/download/NaaPaataNeeNotaMoogaManasulo1964/Naa_Manasu_Nee_Manasu_Okatai-CID%281965%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=500"},
    {"id": 5, "title": "Pushpa Pushpa", "movie": "Pushpa 2 The Rule", "artist": "Nakash Aziz, DSP", "url": "https://archive.org/download/pict_20221110_202211/A1%20-%20Jikki%20-%20Yeruvaaka.mp3", "cover": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500"},
    {"id": 6, "title": "Sooseki", "movie": "Pushpa 2 The Rule", "artist": "Shreya Ghoshal", "url": "https://archive.org/download/pict_20221110_202211/A2%20-%20Jikki%2C%20Ghantasala%E2%80%93Chettulekka%20Galava.mp3", "cover": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=500"},
    {"id": 7, "title": "Inthandham", "movie": "Sita Ramam", "artist": "Vishal Chandrashekhar", "url": "https://archive.org/download/pict_20221110_202211/A3%20-%20Ghantasala%2C%20P.%20Susheela%20-%20Townu%20Pakka.mp3", "cover": "https://images.unsplash.com/photo-1445985543468-89085aed8a20?w=500"},
    {"id": 8, "title": "Kalavathi", "movie": "Sarkaru Vaari Paata", "artist": "Sid Sriram", "url": "https://archive.org/download/pict_20221110_202211/A4%20-%20Ghantasala%20-%20Pogaru%20Bothu.mp3", "cover": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=500"},
    {"id": 9, "title": "Srivalli", "movie": "Pushpa", "artist": "Sid Sriram", "url": "https://archive.org/download/pict_20221110_202211/A5%20-%20Ghantasala%2C%20P.%20Susheela%20-%20Sariganchu%20Cheera.mp3", "cover": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=500"},
    {"id": 10, "title": "Oo Antava", "movie": "Pushpa", "artist": "Indravathi Chauhan", "url": "https://archive.org/download/pict_20221110_202211/B1%20-%20Ghantasala%2C%20Jamuna%20Rani%20-%20Maama%20Maama%20Maama.mp3", "cover": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=500"},
    {"id": 11, "title": "Natu Natu", "movie": "RRR", "artist": "Rahul Sipligunj, Kaala Bhairava", "url": "https://archive.org/download/pict_20221110_202211/B2%20-%20Ghantasala%2C%20P.%20Susheela%20-%20Gowramma%20Nee%20Mogudevaramma.mp3", "cover": "https://images.unsplash.com/photo-1498038432885-c6f3f1b912ee?w=500"},
    {"id": 12, "title": "Komuram Bheemudo", "movie": "RRR", "artist": "Kaala Bhairava", "url": "https://archive.org/download/pict_20221110_202211/B3%20-%20P.%20Susheela%20-%20Pandavulu%20Pandavulu%20Thummedha.mp3", "cover": "https://images.unsplash.com/photo-1471478331149-c72f17e33c73?w=500"},
    {"id": 13, "title": "Ramuloo Ramulaa", "movie": "Ala Vaikunthapurramuloo", "artist": "Anurag Kulkarni", "url": "https://archive.org/download/pict_20221110_202211/B4%20-%20S.P.%20Balasubrahmanyam%20-%20Pattaali%20Araka.mp3", "cover": "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=500"},
    {"id": 14, "title": "Butta Bomma", "movie": "Ala Vaikunthapurramuloo", "artist": "Armaan Malik", "url": "https://archive.org/download/OorediPerediRajaMakutam1960/O_Ante_Theliyani-Bandipotu%281963%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500"},
    {"id": 15, "title": "Samajavaragamana", "movie": "Ala Vaikunthapurramuloo", "artist": "Sid Sriram", "url": "https://archive.org/download/OorediPerediRajaMakutam1960/O_Bangaru_Rangula_Chilaka-Thota_Ramudu%281975%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1445985543468-89085aed8a20?w=500"},
    {"id": 16, "title": "Vathi Coming Telugu", "movie": "Master", "artist": "Anirudh", "url": "https://archive.org/download/OorediPerediRajaMakutam1960/O_Chamathi_Emite-Aathmeeyulu%281969%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=500"},
    {"id": 17, "title": "Master Coming", "movie": "Master", "artist": "Anirudh", "url": "https://archive.org/download/OorediPerediRajaMakutam1960/O_Chandamama_Andaala_Bhaama-Jayam_Manade%281956%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500"},
    {"id": 18, "title": "He's So Cute", "movie": "Sarileru Neekevvaru", "artist": "Madhu Priya", "url": "https://archive.org/download/OorediPerediRajaMakutam1960/O_Koyila-Ida_Lokam%281973%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=500"},
    {"id": 19, "title": "Mind Block", "movie": "Sarileru Neekevvaru", "artist": "Blaaze, Ranina", "url": "https://archive.org/download/OorediPerediRajaMakutam1960/O_Labbi_Venarayyo-Chikkadu_Dorakadu%281967%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=500"},
    {"id": 20, "title": "Dookudu", "movie": "Dookudu", "artist": "Shankar Mahadevan", "url": "https://archive.org/download/OorediPerediRajaMakutam1960/O_Mallayyagaari-Dasara_Bullodu%281971%29-%5Ba2z3gp.com%5D.mp3", "cover": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=500"}
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

# Admin Only Actions
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
