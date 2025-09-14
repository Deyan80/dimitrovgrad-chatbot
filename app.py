import os
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai  # Ново: за Gemini AI

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")  # Google Custom Search API
CX = os.getenv("CX")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Ново: Gemini API ключ

# Актуализиран FAQ речник с повече ключови и актуална info (от 2025)
FAQ = {
    "работно време": "Работното време на Община Димитровград е от понеделник до петък, 8:30 – 17:00 ч. без прекъсване. Повече: https://www.dimitrovgrad.bg/bg/rabotno-vreme",
    "кмет": "Кмет на Община Димитровград е Иво Димов. Повече: https://www.dimitrovgrad.bg/bg/kmet",
    "общински съвет": "Общинският съвет е колективен орган на местното самоуправление. Състав: https://www.dimitrovgrad.bg/bg/obshtinski-savet",
    "председател": "Председател на Общинския съвет е Гергана Кръстева. Повече: https://www.dimitrovgrad.bg/bg/predsedatel-na-obshtinski-savet",
    "телефон": "Център за административно обслужване: 0391/68 214. Горещ телефон: 0391/68 222. Повече: https://www.dimitrovgrad.bg/bg/kontakti"
}

def search_google(query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query + " site:dimitrovgrad.bg",  # Ограничи до официалния сайт за по-точни резултати
        "key": API_KEY,
        "cx": CX,
        "sort": "date"
    }

    # Първо последната седмица
    params["dateRestrict"] = "w1"
    resp = requests.get(base_url, params=params).json()

    if "items" in resp:
        return resp["items"]

    # Без ограничение
    params.pop("dateRestrict")
    resp = requests.get(base_url, params=params).json()

    if "items" in resp:
        return resp["items"]

    return []

def generate_ai_response(query, search_results):
    if not GEMINI_API_KEY:
        return "Липсва GEMINI_API_KEY за AI."

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')  # Безплатен модел

    # Събери snippets от търсенията
    snippets = "\n".join([item.get("snippet", "") for item in search_results])

    # Prompt за Gemini (на български за по-добри отговори)
    prompt = f"Отговори на запитването '{query}' на български език, базирано на тези данни: {snippets}. Бъди кратък, информативен и добави линкове ако са релевантни."

    response = model.generate_content(prompt)
    return response.text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "").lower()

    # 1) Проверка за FAQ с по-гъвкава логика (множество ключови)
    for key, answer in FAQ.items():
        if any(word in query for word in key.split()):  # По-добро съвпадение
            return jsonify([{"title": "FAQ", "link": "#", "snippet": answer}])

    # 2) Google Custom Search + AI
    if not API_KEY or not CX:
        return jsonify({"error": "Липсва API_KEY или CX"}), 500

    try:
        results = search_google(query)
        if results:
            # Използвай AI да генерира coherent отговор
            ai_answer = generate_ai_response(query, results)
            return jsonify([{"title": "AI Отговор", "link": "#", "snippet": ai_answer}])
        else:
            # Ако няма резултати, директно AI (Gemini знае обща info)
            ai_answer = generate_ai_response(query, [])
            return jsonify([{"title": "AI Отговор", "link": "#", "snippet": ai_answer}])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
