from flask import Flask, render_template, request, jsonify, redirect, session
import requests
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = "your-secret-key-here-change-in-production"

API_KEY = "AIzaSyD3FGvLYs3Fzs7yz4vRhjrNMat7m-oT_cg"

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    
    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        full_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Search history table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS search_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        search_query TEXT,
        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(username) REFERENCES users(username)
    )
    """)
    
    # Recently played table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recently_played(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        song_title TEXT,
        song_id TEXT,
        mood TEXT,
        thumbnail TEXT,
        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(username) REFERENCES users(username)
    )
    """)
    
    # Liked songs table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS liked_songs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        song_id TEXT,
        song_title TEXT,
        thumbnail TEXT,
        liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(username, song_id)
    )
    """)
    
    conn.commit()
    conn.close()

# Fix existing database - add missing columns
def fix_database():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    
    try:
        cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
        print("✓ Added email column")
    except:
        pass
    
    try:
        cur.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        print("✓ Added full_name column")
    except:
        pass
    
    conn.commit()
    conn.close()

# Initialize database
init_db()
fix_database()

# Helper functions
def save_search_history(username, query):
    if username:
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO search_history(username, search_query) VALUES(?, ?)", (username, query))
        conn.commit()
        conn.close()

def save_recently_played(username, song_title, song_id, mood, thumbnail=""):
    if username:
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO recently_played(username, song_title, song_id, mood, thumbnail) VALUES(?, ?, ?, ?, ?)", 
                   (username, song_title, song_id, mood, thumbnail))
        cur.execute("DELETE FROM recently_played WHERE id NOT IN (SELECT id FROM recently_played WHERE username=? ORDER BY played_at DESC LIMIT 30)", (username,))
        conn.commit()
        conn.close()

def like_song(username, song_id, song_title, thumbnail=""):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO liked_songs(username, song_id, song_title, thumbnail) VALUES(?, ?, ?, ?)", 
                   (username, song_id, song_title, thumbnail))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def unlike_song(username, song_id):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM liked_songs WHERE username=? AND song_id=?", (username, song_id))
    conn.commit()
    conn.close()

def is_song_liked(username, song_id):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM liked_songs WHERE username=? AND song_id=?", (username, song_id))
    result = cur.fetchone()
    conn.close()
    return result is not None

# Routes
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()
        
        if user:
            session["user"] = username
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid credentials! Please register.")
    
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form.get("email", "")
        full_name = request.form.get("full_name", "")
        
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        
        try:
            cur.execute("INSERT INTO users(username, password, email, full_name) VALUES(?, ?, ?, ?)", 
                       (username, password, email, full_name))
            conn.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists! Please choose another.")
        except Exception as e:
            return render_template("register.html", error=f"Error: {str(e)}")
        finally:
            conn.close()
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/about")
def about():
    if "user" not in session:
        return redirect("/login")
    return render_template("about.html")

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")
    
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT username, email, full_name, created_at FROM users WHERE username=?", (session["user"],))
    user_data = cur.fetchone()
    conn.close()
    
    if user_data:
        return render_template("profile.html", user={
            "username": user_data[0],
            "email": user_data[1] if user_data[1] else "Not set",
            "full_name": user_data[2] if user_data[2] else "Not set",
            "joined": user_data[3]
        })
    else:
        return redirect("/login")

@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT search_query, search_time FROM search_history WHERE username=? ORDER BY search_time DESC LIMIT 50", (session["user"],))
    search_history = [{"query": row[0], "time": row[1]} for row in cur.fetchall()]
    conn.close()
    
    return render_template("history.html", history=search_history)

@app.route("/recent")
def recent():
    if "user" not in session:
        return redirect("/login")
    
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT song_title, song_id, mood, thumbnail, played_at FROM recently_played WHERE username=? ORDER BY played_at DESC LIMIT 30", (session["user"],))
    recent_songs = [{"title": row[0], "id": row[1], "mood": row[2], "thumbnail": row[3], "played_at": row[4]} for row in cur.fetchall()]
    conn.close()
    
    return render_template("recent.html", songs=recent_songs)

@app.route("/liked")
def liked():
    if "user" not in session:
        return redirect("/login")
    
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT song_title, song_id, thumbnail, liked_at FROM liked_songs WHERE username=? ORDER BY liked_at DESC LIMIT 50", (session["user"],))
    liked_songs = [{"title": row[0], "id": row[1], "thumbnail": row[2], "liked_at": row[3]} for row in cur.fetchall()]
    conn.close()
    
    return render_template("liked.html", songs=liked_songs)

# API Routes
@app.route("/search_music")
def search_music():
    if "user" not in session:
        return jsonify([])
    
    query = request.args.get("q", "")
    if query:
        save_search_history(session["user"], query)
    
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}+music&type=video&maxResults=20&key={API_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        songs = []
        for item in res.get("items", []):
            songs.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
            })
        return jsonify(songs)
    except:
        return jsonify([])

@app.route("/get_music")
def get_music():
    if "user" not in session:
        return jsonify([])
    
    mood = request.args.get("mood", "relaxed")
    mood_queries = {
        "happy": "upbeat happy pop music",
        "sad": "emotional sad songs",
        "angry": "aggressive rock metal",
        "relaxed": "chill lofi study beats",
        "love": "romantic love songs",
        "sleep": "calm sleep meditation",
        "excited": "energetic dance edm",
        "focus": "classical focus piano",
        "chill": "smooth r&b chillhop",
        "workout": "workout gym motivation"
    }
    
    search_query = mood_queries.get(mood, f"{mood} songs playlist")
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&type=video&maxResults=20&key={API_KEY}"
    
    try:
        res = requests.get(url, timeout=10).json()
        songs = []
        for item in res.get("items", []):
            songs.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
            })
        return jsonify(songs)
    except:
        return jsonify([])

@app.route("/save_recent", methods=["POST"])
def save_recent():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    save_recently_played(session["user"], data.get("title"), data.get("id"), data.get("mood"), data.get("thumbnail", ""))
    return jsonify({"success": True})

@app.route("/like_song", methods=["POST"])
def like_song_route():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    success = like_song(session["user"], data.get("id"), data.get("title"), data.get("thumbnail", ""))
    return jsonify({"success": success})

@app.route("/unlike_song", methods=["POST"])
def unlike_song_route():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    unlike_song(session["user"], data.get("id"))
    return jsonify({"success": True})

@app.route("/check_liked", methods=["GET"])
def check_liked():
    if "user" not in session:
        return jsonify({"liked": False})
    
    song_id = request.args.get("id")
    liked = is_song_liked(session["user"], song_id)
    return jsonify({"liked": liked})

if __name__ == "__main__":
    app.run(debug=True)
