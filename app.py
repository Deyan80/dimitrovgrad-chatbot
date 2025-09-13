from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"answer": "Моля, напишете въпрос."})
    # тестов отговор
    return jsonify({"answer": f"Получих въпроса: {query}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

