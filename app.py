from flask import Flask, send_from_directory, jsonify, request

# Увери се, че името на променливата е точно `app` — gunicorn търси app:app
app = Flask(__name__, static_folder='static', static_url_path='')

@app.route("/")
def index():
    # Ако имаш static/index.html (напр. React build), той ще се сервира автоматично
    try:
        return send_from_directory('static', 'index.html')
    except Exception:
        return "<h1>Добре дошли в Dimitrovgrad Chatbot!</h1><p>Ботът е активен ✅</p>"

@app.route("/api/health")
def health():
    return jsonify(status="ok")

# Примерен API endpoint (замени с логиката на твоя бот)
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    # временно поведение — върни примерен отговор
    return jsonify({"reply": "Това е тестов отговор. Заменете с реалната логика."})
