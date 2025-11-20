from flask import current_app
from app.extensions import db
from app.models.chat import Bot


def seed_bots() -> None:
    current_app.logger.info("Starting bot seeding...")
    bots = [
        Bot(
            name="EmailBot",
            role="Email Assistant",
            system_prompt="You are an expert at writing professional emails. Help the user draft, edit, or reply to emails.",
        ),
        Bot(
            name="CodeBot",
            role="Coding Assistant",
            system_prompt="You are an expert software developer. Help the user write, debug, and explain code.",
        ),
        Bot(
            name="AccountingBot",
            role="Accountant",
            system_prompt="You are an accountant. Help the user with financial questions, bookkeeping, and taxes.",
        ),
        Bot(
            name="JokeBot",
            role="Comedian",
            system_prompt="You are a comedian. Respond to everything with a joke or a funny observation.",
        ),
    ]
    for bot in bots:
        db.session.add(bot)
        current_app.logger.debug(f"Added bot to session: {bot.name}")

    db.session.commit()
    current_app.logger.info(f"Successfully seeded {len(bots)} bots.")
