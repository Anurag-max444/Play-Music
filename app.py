from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "SECRET_KEY"

UPLOAD_FOLDER = "static/songs"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ================= DB INIT =================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect("database.db")

# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        # 🔥 ADMIN LOGIN
        if user == "Ayush_JackSparrow" and pwd == "2267212474#":
            session["admin"] = True
            return redirect("/admin")

        # 👤 NORMAL USER LOGIN
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = cur.fetchone()

        if result:
            session["user"] = user
            return redirect("/home")
        else:
            flash("Invalid Username or Password ❌", "login_error")
            return redirect("/")# 🔥 same page

    return render_template("login.html")

# ================= HOME =================
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM songs")
    songs = cur.fetchall()

    return render_template("index.html", songs=songs)

# ================= ADMIN PANEL =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "admin" not in session:
        return redirect("/")

    # 🔥 POST: Upload song
    if request.method == "POST":
        title = request.form["title"]
        file = request.files["song"]

        if file:
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            db = get_db()
            cur = db.cursor()
            cur.execute("INSERT INTO songs (title, filename) VALUES (?, ?)", (title, file.filename))
            db.commit()

            flash("Song Uploaded Successfully ✅")
            return redirect("/admin")

    # 🔥 GET: Always fetch songs
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM songs")
    songs = cur.fetchall()

    return render_template("admin.html", songs=songs)

# ================= CREATE USER =================
@app.route("/create-user", methods=["POST"])
def create_user():
    if "admin" not in session:
        return redirect("/")

    user = request.form["username"]
    pwd = request.form["password"]

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
    db.commit()

    flash("User Created Successfully ✅")
    return redirect("/admin")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/delete-song/<int:id>")
def delete_song(id):
    if "admin" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    # filename bhi delete karne ke liye
    cur.execute("SELECT filename FROM songs WHERE id=?", (id,))
    song = cur.fetchone()

    if song:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], song[0])
        if os.path.exists(filepath):
            os.remove(filepath)

    cur.execute("DELETE FROM songs WHERE id=?", (id,))
    db.commit()

    flash("Song Deleted Successfully ❌")
    return redirect("/admin")

# ================= RUN =================
app.run(host="0.0.0.0",port=5000)
