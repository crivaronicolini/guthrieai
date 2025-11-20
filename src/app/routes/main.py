from flask import Blueprint, render_template, request, jsonify, Response, current_app
from typing import Union, List
from app.extensions import db
from app.models.chat import Bot, Conversation, Message
from app.services.llm_service import LLMService

main_bp = Blueprint("main", __name__)
llm_service = LLMService()


@main_bp.route("/")
def index() -> str:
    current_app.logger.info("Accessing index page")
    conversations: List[Conversation] = Conversation.query.order_by(
        Conversation.created_at.desc()
    ).all()
    bots: List[Bot] = Bot.query.all()
    return render_template("index.html", conversations=conversations, bots=bots)


@main_bp.route("/conversations", methods=["POST"])
def create_conversation() -> str:
    name: str = request.form.get("name", "New Chat")
    current_app.logger.info(f"Creating new conversation: {name}")
    conversation = Conversation(name=name)
    db.session.add(conversation)
    db.session.commit()
    current_app.logger.debug(f"Conversation created with ID: {conversation.id}")
    return render_template("partials/conversation_item.html", conversation=conversation)


@main_bp.route("/conversations/<int:conversation_id>")
def get_conversation(conversation_id: int) -> str:
    current_app.logger.debug(f"Fetching conversation {conversation_id}")
    conversation: Conversation = Conversation.query.get_or_404(conversation_id)
    messages: List[Message] = (
        Message.query.filter_by(conversation_id=conversation_id)
        .order_by(Message.timestamp)
        .all()
    )
    return render_template(
        "partials/chat_window.html", conversation=conversation, messages=messages
    )


@main_bp.route("/conversations/<int:conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id: int) -> str:
    conversation: Conversation = Conversation.query.get_or_404(conversation_id)
    current_app.logger.info(f"Deleting conversation {conversation_id}")

    # Delete associated messages first
    Message.query.filter_by(conversation_id=conversation_id).delete()

    db.session.delete(conversation)
    db.session.commit()

    current_app.logger.debug(f"Conversation {conversation_id} deleted")
    return ""


@main_bp.route("/message", methods=["POST"])
def send_message() -> Union[str, tuple[Response, int]]:
    conversation_id = request.form.get("conversation_id")
    content = request.form.get("content")

    if not conversation_id or not content:
        current_app.logger.warning("Attempted to send message with missing data")
        return jsonify({"error": "Missing data"}), 400

    current_app.logger.info(f"Processing message for conversation {conversation_id}")

    user_msg = Message(
        conversation_id=int(conversation_id), sender="user", content=content
    )
    db.session.add(user_msg)
    db.session.commit()
    current_app.logger.debug("User message saved")

    # Determine which bot to respond
    bots: List[Bot] = Bot.query.all()
    target_bot_name = llm_service.route_message(content, bots)
    target_bot = Bot.query.filter_by(name=target_bot_name).first()

    if not target_bot:
        current_app.logger.warning(
            f"Target bot '{target_bot_name}' not found. Falling back to first bot."
        )
        target_bot = bots[0]  # Fallback

    current_app.logger.info(f"Routed to bot: {target_bot.name}")

    # Get history
    history = [
        m.to_dict()
        for m in Message.query.filter_by(conversation_id=int(conversation_id))
        .order_by(Message.timestamp)
        .all()
    ]
    # Remove the just added user message from history to avoid double counting
    history = history[:-1]

    response_content = llm_service.get_bot_response(target_bot, history, content)

    bot_msg = Message(
        conversation_id=int(conversation_id),
        sender=target_bot.name,
        content=response_content,
    )
    db.session.add(bot_msg)
    db.session.commit()
    current_app.logger.debug("Bot response saved")

    # Return the two new messages (user and bot) rendered
    return render_template(
        "partials/message_pair.html", user_msg=user_msg, bot_msg=bot_msg
    )


@main_bp.route("/bots", methods=["POST"])
def create_bot() -> Union[str, tuple[str, int]]:
    name = request.form.get("name")
    role = request.form.get("role")
    system_prompt = request.form.get("system_prompt")
    model = request.form.get("model")

    if not name or not role or not system_prompt:
        current_app.logger.warning("Failed to create bot: missing fields")
        return "Missing fields", 400

    if Bot.query.filter_by(name=name).first():
        current_app.logger.warning(
            f"Failed to create bot: name '{name}' already exists"
        )
        return "Bot name already exists", 400

    current_app.logger.info(f"Creating new bot: {name}")
    bot = Bot(name=name, role=role, system_prompt=system_prompt, model=model)
    db.session.add(bot)
    db.session.commit()

    return render_template("partials/bot_item.html", bot=bot)


@main_bp.route("/bots/<int:bot_id>", methods=["PUT"])
def update_bot(bot_id: int) -> str:
    bot: Bot = Bot.query.get_or_404(bot_id)
    new_model = request.form.get("model", bot.model)
    current_app.logger.info(f"Updating bot {bot.name} model to {new_model}")
    bot.model = new_model
    db.session.commit()
    return "Updated"
