import os
from flask import Flask, render_template, request, jsonify
import requests
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)

# Вземаме ключовете от системните променливи
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ----------------------------
# Функция за търсене в Google CSE
# ----------------------------
def google_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": SEARCH_ENGINE_ID,
        "key": GOOGLE_API_KEY,
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        return []

# ----------------------------
# Генериране на отговор от AI
# ----------------------------
def generate_ai_response(query, search_results):
    if not GEMINI_API_KEY:
        return "❗ Липсва GEMINI_API_KEY за AI."

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    current_date = datetime.now().strftime("%d.%m.%Y (%A), %H:%M ч.")

    if not search_results:
        return f"ℹ️ Не намерих информация по темата „{query}“ на сайта на Община Димитровград."

    # Форматираме резултатите като източници
    sources = ""
    for item in search_results:
        link = item.get("link", "")
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        if link.endswith(".pdf"):
            sources += f"- {title}: {snippet}\n  <a href=\"{link}\" target=\"_blank\">Виж документа</a> | <a href=\"{link}\" target=\"_blank\">⬇️ Изтегли PDF</a>\n"
        else:
            sources += f"- {title}: {snippet}\n  <a href=\"{link}\" target=\"_blank\">Отвори</a>\n"

    prompt = f"""
Ти си виртуален асистент за сайта на Община Димитровград.
Днес е {current_date}.
Потребителят пита: "{query}".

Ето какво намерих в сайта на общината:
{sources}

❗ Много важно:
- Никога не казвай, че "нямаш достъп до интернет" или че "не можеш да провериш".
- Винаги използвай информацията от горните резултати, за да формулираш отговор.
- Първо дай кратък и ясен отговор на български.
- След това добави линк(ове) към оригиналните страници или документи.
- Ако няма достатъчно информация, просто кажи: "Не намерих подробности в сайта, но ето най-близкото, което открих."
- Използвай HTML формат за линковете: <a href="URL" target="_blank">име</a>.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Грешка при AI обработка: {str(e)}"

# ----------------------------
# Рутове на Flask
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query", "")

    # Търсим информация в Google
    search_results = google_search(query)

    # Генерираме отговор от AI
    ai_response = generate_ai_response(query, search_results)

    return jsonify({"answer": ai_response})

# ----------------------------
# Стартиране на приложението
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)

