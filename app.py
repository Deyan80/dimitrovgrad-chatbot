import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
CX = os.getenv("CX")


def search_google(query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": API_KEY,
        "cx": CX,
        "sort": "date"
    }

    # 1️⃣ Първо пробваме само последната седмица
    params["dateRestrict"] = "w1"
    resp = requests.get(base_url, params=params).json()

    if "items" in resp:
        return resp["items"]

    # 2️⃣ Ако няма резултати → премахваме ограничението и търсим всичко
    params.pop("dateRestrict")
    resp = requests.get(base_url, params=params).json()

    if "items" in resp:
        return resp["items"]

    return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query")

    if not API_KEY or not CX:
        return jsonify({"error": "Добави API_KEY и CX в Render Environment Variables"}), 500

    try:
        results = search_google(query)
        output = []
        for item in results:
            output.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


