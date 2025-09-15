import os
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
CX = os.getenv("CX")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

FAQ = {
    "работно време": "Работното време на Община Димитровград е от понеделник до петък, 8:30 – 17:00 ч. без прекъсване. Повече: https://www.dimitrovgrad.bg/bg/rabotno-vreme",
    "кмет": "Кмет на Община Димитровград е Иво Димов. Повече: https://www.dimitrovgrad.bg/bg/kmet",
    "общински съвет": "Общинският съвет е колективен орган на местното самоуправление. Състав: https://www.dimitrovgrad.bg/bg/obshtinski-savet",
    "председател": "Председател на Общинския съвет е Гергана Кръстева. Повече: https://www.dimitrovgrad.bg/bg/predsedatel-na-obshtinski-savet",
    "телефон": "Център за административно обслужване: 0391/68 214. Горещ телефон: 0391/68 222. Повече: https://www.dimitrovgrad.bg/bg/kontakti",
    "културна програма": "Актуалната културна програма е публикувана тук: https://www.dimitrovgrad.bg/bg/kultura",
    "сесия": "Видеозаписи и дневен ред на сесиите на Общински съвет: https://www.dimitrovgrad.bg/bg/obshtinski-savet",
}

def search_google(query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query + " site:dimitrovgrad.bg",
        "key": API_KEY,
        "cx": CX,
    }
    resp = requests.get(base_url, params=params).json()
    return resp.get("items", [])

def generate_ai_response(query, search_results):
    if not GEMINI_API_KEY:
        return "❗ Липсва GEMINI_API_KEY за AI."

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    current_date = datetime.now().strftime("%d.%m.%Y (%A), %H:%M ч.")
    snippets = "\n".join(
        [f"- {item.get('title', '')}: {item.get('link', '')}\n{item.get('snippet','')}" for item in search_results]
    )
    prompt = f"""Днес е {current_date}.
Потребителят пита: '{query}'.
Базирай се на информацията от сайта на Община Димитровград:
{snippets}

Изведи отговор на български, с ясен и приятелски стил 🙂. Ако има линкове, вмъкни ги като активни. Бъди полезен и точен.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Грешка при AI обработка: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "").lower()

    if any(word in query for word in ["ден", "днес", "дата", "час"]):
        now = datetime.now().strftime("%d.%m.%Y (%A), %H:%M ч.")
        return jsonify([{"title": "Време", "link": "#", "snippet": f"⌛ Днес е {now}."}])

    for key, answer in FAQ.items():
        if key in query:
            return jsonify([{"title": "FAQ", "link": "#", "snippet": answer}])

    if not API_KEY or not CX:
        return jsonify({"error": "Липсва API_KEY или CX"}), 500

    try:
        results = search_google(query)
        ai_answer = generate_ai_response(query, results)
        return jsonify([{"title": "AI Отговор", "link": "#", "snippet": ai_answer}])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

