from app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    debug_mode = Config.APP_DEBUG
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
