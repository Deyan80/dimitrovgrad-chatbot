from flask import Flask, render_template, request, jsonify
import requests
import os  # За environment variables (за ключовете)

app = Flask(__name__)

# Ключове за Google Custom Search (замени с твоите или използвай Environment Variables)
API_KEY = os.environ.get('API_KEY', 'your_google_api_key_here')  # Добави в Render Environment
CX = os.environ.get('CX', 'your_cse_id_here')  # Добави в Render Environment

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'results': 'Моля, въведи въпрос.'})

    # Проверка за ключове
    if API_KEY == 'your_google_api_key_here' or CX == 'your_cse_id_here':
        return jsonify({'results': 'Грешка: Добави API_KEY и CX в Render Environment Variables.'})

    try:
        # URL за Google API
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}&num=5"
        response = requests.get(url)
        response.raise_for_status()

        results = response.json().get('items', [])
        if not results:
            return jsonify({'results': 'Няма намерени резултати. Опитай с по-конкретен въпрос за Община Димитровград.'})

        # Форматирай резултатите за чат
        formatted = []
        for item in results:
            title = item.get('title', 'Без заглавие')
            link = item.get('link', '#')
            snippet = item.get('snippet', 'Без описание')[:200] + '...'
            formatted.append(f"**{title}**\n{snippet}\n[Виж повече: {link}]")
        full_results = '\n\n---\n\n'.join(formatted)

        return jsonify({'results': full_results})

    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        if 'invalid API key' in error_msg.lower():
            return jsonify({'results': 'Грешка: Невалиден API ключ. Провери ключовете в Render.'})
        elif 'quotaExceeded' in error_msg.lower():
            return jsonify({'results': 'Грешка: Превишен лимит на запитванията за API. Опитай по-късно.'})
        return jsonify({'results': f'HTTP грешка: {error_msg}'})
    except Exception as e:
        return jsonify({'results': f'Грешка при търсенето: {str(e)}. Опитай пак.'})

if __name__ == '__main__':
    app.run(debug=True)
