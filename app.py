from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# 🔑 PUT YOUR YOUTUBE API KEY HERE
API_KEY = "AIzaSyD3FGvLYs3Fzs7yz4vRhjrNMat7m-oT_cg"


# 🎯 Mood → search queries
def get_queries(mood):
    queries = {
        "happy": ["happy songs playlist", "party music mix"],
        "sad": ["sad songs playlist", "emotional songs"],
        "angry": ["angry rock music", "intense workout music"],
        "relaxed": ["lofi chill beats", "relaxing music playlist"],

        # 🔥 EXTRA MOODS
        "love": ["romantic songs playlist", "love songs"],
        "sleep": ["sleep music", "deep sleep relaxing music"],
        "excited": ["hype songs", "festival music"],
        "focus": ["study music", "focus concentration music"],
        "chill": ["chill vibes playlist", "lofi chill music"],
        "workout": ["gym workout music", "motivation workout songs"]
    }

    return queries.get(mood, ["relaxing music"])


# 🔍 Fetch from YouTube API
def fetch_youtube(query):
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "key": API_KEY,
        "maxResults": 10,
        "type": "video,playlist"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "items" not in data:
            print("API ERROR:", data)
            return []

        results = []

        for item in data["items"]:
            kind = item["id"]["kind"]

            if kind == "youtube#video":
                results.append({
                    "type": "video",
                    "id": item["id"]["videoId"],
                    "title": item["snippet"]["title"]
                })

            elif kind == "youtube#playlist":
                results.append({
                    "type": "playlist",
                    "id": item["id"]["playlistId"],
                    "title": item["snippet"]["title"]
                })

        return results

    except Exception as e:
        print("ERROR:", e)
        return []


# 🏠 Home
@app.route("/")
def home():
    return render_template("index.html")


# 🎵 API route
@app.route("/get_music")
def get_music():
    mood = request.args.get("mood", "relaxed")

    queries = get_queries(mood)

    all_results = []

    for q in queries:
        all_results.extend(fetch_youtube(q))

    # fallback if API fails
    if not all_results:
        return jsonify([
            {"type": "video", "id": "ZbZSe6N_BXs", "title": "Happy Song"},
            {"type": "video", "id": "OPf0YbXqDm0", "title": "Uptown Funk"}
        ])

    return jsonify(all_results)


if __name__ == "__main__":
    app.run(debug=True)