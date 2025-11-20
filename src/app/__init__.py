import logging
from flask import Flask
from config import Config
from app.extensions import db
from app.seeds import seed_bots


def create_app(config_class: type[Config] = Config) -> Flask:
    instance_path = "/tmp/instance" if Config.DOCKER_CONTAINER else None

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        instance_path=instance_path,
    )

    app.config.from_object(config_class)

    log_level = logging.DEBUG if Config.APP_DEBUG else logging.INFO
    logging.basicConfig(level=log_level)

    app.logger.info(f"Initializing application with log level {log_level}")

    db.init_app(app)
    app.logger.debug("Database extension initialized.")

    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.logger.debug("Main blueprint registered.")

    # Create database tables
    with app.app_context():
        from app.models.chat import Bot

        db.create_all()
        app.logger.info("Database tables created/verified.")

        # Seed default bots if they don't exist
        if not Bot.query.first():
            app.logger.info("No bots found. Seeding default bots...")
            seed_bots()
        else:
            app.logger.debug("Bots already exist. Skipping seed.")

    app.logger.info("Application startup complete.")
    return app
