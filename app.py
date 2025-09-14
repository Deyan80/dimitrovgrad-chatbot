import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
CX = os.getenv("CX")

# FAQ речник
FAQ = {
    "работно време": "Работното време на Община Димитровград е от понеделник до петък, 8:00 – 17:00 ч. Повече: https://www.dimitrovgrad.bg/bg/kontakti",
    "кмет": "Кмет на Община Димитровград е Иво Димов. Повече: https://www.dimitrovgrad.bg/bg/kmet",
    "общински съвет": "Общинският съвет е колективен орган на местното самоуправление. Състав: https://www.dimitrovgrad.bg/bg/obshtinski-savet"
}


def search_google(query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": API_KEY,
        "cx": CX,
        "sort": "date"
    }

    # Пробваме първо последната седмица
    params["dateRestrict"] = "w1"
    resp = requests.get(base_url, params=params).json()

    if "items" in resp:
        return resp["items"]

    # Ако няма резултати → махаме ограничението
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
    query = data.get("query", "").lower()

    # 1) Проверка за FAQ
    for key, answer in FAQ.items():
        if key in query:
            return jsonify([{"title": "FAQ", "link": "#", "snippet": answer}])

    # 2) Ако няма съвпадение → Google Custom Search
    if not API_KEY or not CX:
        return jsonify({"error": "Липсва API_KEY или CX"}), 500

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
