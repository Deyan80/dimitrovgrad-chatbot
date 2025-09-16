from flask import Flask, request, jsonify, render_template
import requests
import os
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)

# Конфигурация
API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🔍 Търсене в Google Custom Search
def search_google(query):
    base_url = "https://www.googleapis.com/customsearch/v1"

    # при специфични заявки – таргетираме поддиректории
    if "бюджет" in query.lower():
        query += " site:dimitrovgrad.bg/bg/bjudzhet"
    elif "решение" in query.lower() or "сесия" in query.lower():
        query += " site:dimitrovgrad.bg/bg/obshtinski-savet"
    elif "видео" in query.lower():
        query += " site:dimitrovgrad.bg/bg/obshtinski-savet/video"
    else:
        query += " site:dimitrovgrad.bg"

    params = {"q": query, "key": API_KEY, "cx": CX}
    resp = requests.get(base_url, params=params).json()
    return resp.get("items", [])

# 🧠 Генериране на AI отговор
def generate_ai_response(query, search_results):
    if not GEMINI_API_KEY:
        return "❗ Липсва GEMINI_API_KEY за AI."

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    current_date = datetime.now().strftime("%d.%m.%Y (%A), %H:%M ч.")

    snippets = ""
    for item in search_results:
        link = item.get("link", "")
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        if link.endswith(".pdf"):
            snippets += f"- <a href='{link}' target='_blank'>{title}</a> ⬇️ <a href='{link}' target='_blank' class='download-btn'>Изтегли PDF</a>\n{snippet}\n"
        else:
            snippets += f"- <a href='{link}' target='_blank'>{title}</a>\n{snippet}\n"

    prompt = f"""Днес е {current_date}.
Потребителят пита: '{query}'.
Базирай се на информацията от сайта на Община Димитровград:
{snippets}

Формирай отговор на български, приятелски и ясен 🙂.
- Ако има точен отговор (например бюджет, решение), напиши го директно.
- След това дай 1-2 активни линка към оригиналните документи/страници.
Използвай HTML формат за линковете: <a href="URL" target="_blank">име</a>.
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
    data = request.get_json()
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Няма подаден въпрос."})

    search_results = search_google(query)
    ai_answer = generate_ai_response(query, search_results)

    return jsonify([{"snippet": ai_answer}])

if __name__ == "__main__":
    app.run(debug=True)


