from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)

API_KEY = "AIzaSyD3FGvLYs3Fzs7yz4vRhjrNMat7m-oT_cg"


# 🔍 SEARCH MUSIC
@app.route("/search_music")
def search_music():
    query = request.args.get("q")

    if not query:
        return jsonify([])

    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "key": API_KEY,
            "maxResults": 20,
            "type": "video"
        }

        response = requests.get(url, params=params)
        data = response.json()

        # 🔴 PRINT FULL RESPONSE (VERY IMPORTANT)
        print("YOUTUBE RESPONSE:", data)

        # ❌ API ERROR
        if "error" in data:
            print("API ERROR:", data["error"])
            return jsonify([])

        results = []

        for item in data.get("items", []):
            if item["id"].get("videoId"):
                results.append({
                    "id": item["id"]["videoId"],
                    "title": item["snippet"]["title"]
                })

        # ⚠️ IF EMPTY → RETURN FALLBACK SONGS
        if not results:
            return jsonify([
                {"id": "5qap5aO4i9A", "title": "Lofi Chill"},
                {"id": "RgKAFK5djSk", "title": "See You Again"},
                {"id": "JGwWNGJdvx8", "title": "Shape of You"}
            ])

        return jsonify(results)

    except Exception as e:
        print("ERROR:", e)
        return jsonify([
            {"id": "5qap5aO4i9A", "title": "Lofi Chill"},
            {"id": "RgKAFK5djSk", "title": "See You Again"}
        ])


# 🎵 MOOD MUSIC
@app.route("/get_music")
def get_music():
    mood = request.args.get("mood")

    mood_query = {
        "happy": "happy songs",
        "sad": "sad songs",
        "relaxed": "lofi chill",
        "angry": "rock music",
        "love": "romantic songs",
        "sleep": "sleep music",
        "excited": "party songs",
        "focus": "study music",
        "chill": "chill music",
        "workout": "workout music"
    }

    query = mood_query.get(mood, "music")

    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "key": API_KEY,
            "maxResults": 20,
            "type": "video"
        }

        response = requests.get(url, params=params)
        data = response.json()

        print("MOOD RESPONSE:", data)

        if "error" in data:
            print("API ERROR:", data["error"])
            return jsonify([])

        results = []

        for item in data.get("items", []):
            if item["id"].get("videoId"):
                results.append({
                    "id": item["id"]["videoId"],
                    "title": item["snippet"]["title"]
                })

        if not results:
            return jsonify([
                {"id": "5qap5aO4i9A", "title": "Lofi Chill"},
                {"id": "hHW1oY26kxQ", "title": "Relax Music"}
            ])

        return jsonify(results)

    except Exception as e:
        print("ERROR:", e)
        return jsonify([
            {"id": "5qap5aO4i9A", "title": "Fallback Music"}
        ])


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
