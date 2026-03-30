from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)

# 🔑 PASTE YOUR API KEY HERE
API_KEY = "AIzaSyD3FGvLYs3Fzs7yz4vRhjrNMat7m-oT_cg"


# 🔍 SEARCH MUSIC (REAL RESULTS)
@app.route("/search_music")
def search_music():
    query = request.args.get("q")

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "key": API_KEY,
        "maxResults": 6,
        "type": "video"
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []

    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]

        results.append({
            "id": video_id,
            "title": title
        })

    return jsonify(results)


# 🎵 MOOD MUSIC (SEARCH BASED)
@app.route("/get_music")
def get_music():
    mood = request.args.get("mood")

    mood_query = {
        "happy": "happy songs",
        "sad": "sad songs",
        "relaxed": "lofi chill",
        "angry": "rock music",
        "love": "romantic songs",
        "study": "study music",
        "chill": "chill music",
        "workout": "workout music"
    }

    query = mood_query.get(mood, "music")

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "key": API_KEY,
        "maxResults": 6,
        "type": "video"
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []

    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]

        results.append({
            "id": video_id,
            "title": title
        })

    return jsonify(results)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
