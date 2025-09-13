from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Взимаме API_KEY и CX от променливите на средата
API_KEY = os.getenv("API_KEY")
CX = os.getenv("CX")

if not API_KEY or not CX:
    print("Грешка: Добави API_KEY и CX в Render Environment Variables")

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

@app.route("/")
def index():
    return "Чатботът е на линия!"

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "Липсва заявка"}), 400

    # Проверка дали ключовете са налични
    if not API_KEY or not CX:
        return jsonify({"error": "Грешка: Добави API_KEY и CX в Render Environment Variables"}), 500

    # Извършваме заявка към Google Custom Search
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query
    }
    response = requests.get(GOOGLE_SEARCH_URL, params=params)
    results = response.json()

    # Връщаме първите 3 резултата
    items = results.get("items", [])
    top_results = [{"title": item["title"], "link": item["link"]} for item in items[:3]]

    return jsonify(top_results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

