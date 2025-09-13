from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# TODO: сложи тук своите Google API ключове
API_KEY = "YOUR_GOOGLE_API_KEY"
CX = "YOUR_CUSTOM_SEARCH_ENGINE_ID"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Няма въведена заявка"}), 400

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": 5
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Google API грешка"}), 500

    results = response.json().get("items", [])
    output = []
    for item in results:
        output.append({
            "title": item.get("title"),
            "path": item.get("link")
        })

    return jsonify(output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
