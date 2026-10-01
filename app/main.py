from flask import Flask, jsonify

from .database import criar_banco
from .routes import api


def criar_app():
    app = Flask(__name__)

    criar_banco()

    app.register_blueprint(api)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
