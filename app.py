
from flask import Flask, render_template, request, redirect, url_for, session, flash



app = Flask(__name__)

app.secret_key = 'telugu_music_secret_key'  # Required for sessions



# Mock user database (In production, replace with SQLite or PostgreSQL)

users = {

    "karunakar": "password123"

}



# Telugu Songs List (Auto-loaded in app)

TELUGU_SONGS = [

    {

        "id": 1,

        "title": "Samayama",

        "movie": "Hi Nanna",

        "artist": "Anurag Kulkarni",

        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",

        "cover": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300"

    },

    {

        "id": 2,

        "title": "Kurchi Madathapetti",

        "movie": "Guntur Kaaram",

        "artist": "Thaman S, Sahithi",

        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",

        "cover": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300"

    },

    {

        "id": 3,

        "title": "Chuttamalle",

        "movie": "Devara",

        "artist": "Shreya Ghoshal",

        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",

        "cover": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300"

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

        username = request.form.get("username")

        password = request.form.get("password")

        

        if username in users and users[username] == password:

            session["user"] = username

            return redirect(url_for("index"))

        else:

            flash("Invalid credentials! Try karuna / password123")

            

    return render_template("login.html")



@app.route("/register", methods=["POST"])

def register():

    username = request.form.get("username")

    password = request.form.get("password")

    if username and password:

        users[username] = password

        session["user"] = username

        return redirect(url_for("index"))

    flash("Registration failed!")

    return redirect(url_for("login"))



@app.route("/logout")

def logout():

    session.pop("user", None)

    return redirect(url_for("login"))



if __name__ == "__main__":

    app.run(debug=True)

