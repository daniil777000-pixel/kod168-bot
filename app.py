from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "KOD 168 CRM BOT ONLINE 🔥"

@app.route("/health")
def health():
    return {
        "status": "ok",
        "project": "KOD 168 CRM"
    }

if __name__ == "__main__":
    # БЕРЁМ ПОРТ ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ RENDER
    port = int(os.environ.get("PORT", 10000))
    # СЛУШАЕМ НА ВСЕХ ИНТЕРФЕЙСАХ (0.0.0.0)
    app.run(host="0.0.0.0", port=port)