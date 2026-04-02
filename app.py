from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "AIzaSyD3FGvLYs3Fzs7yz4vRhjrNMat7m-oT_cg"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/search_music")
def search_music():
    query = request.args.get("q")

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=16&key={API_KEY}"
    res = requests.get(url).json()

    songs = []
    for item in res.get("items", []):
        songs.append({
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"]
        })

    return jsonify(songs)

@app.route("/get_music")
def get_music():
    mood = request.args.get("mood")

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={mood}+songs&type=video&maxResults=16&key={API_KEY}"
    res = requests.get(url).json()

    songs = []
    for item in res.get("items", []):
        songs.append({
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"]
        })

    return jsonify(songs)

if __name__ == "__main__":
    app.run(debug=True)
