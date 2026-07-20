from flask import Flask

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
    app.run(
        host="0.0.0.0",
        port=10000
    )
