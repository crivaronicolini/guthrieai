from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel
from flask import current_app
from app.models.chat import Bot


class LLMService:
    def __init__(self) -> None:
        pass

    def get_model(self, model_name: Optional[str] = None) -> BaseChatModel:
        if model_name is None:
            model_name = "gemma3"

        current_app.logger.debug(f"Initializing ChatOllama with model: {model_name}")
        return ChatOllama(
            base_url=current_app.config["OLLAMA_BASE_URL"], model=model_name
        )

    def route_message(self, message_content: str, available_bots: List[Bot]) -> str:
        """
        Decides which bot should handle the message.
        available_bots: List of Bot objects with name and role.
        """
        current_app.logger.debug(f"Routing message: '{message_content[:50]}...'")

        # Description of available bots
        bot_descriptions = "\n".join(
            [f"- {bot.name}: {bot.role}" for bot in available_bots]
        )

        system_prompt = (
            "You are a RouterBot. Your job is to analyze the user's message and decide which bot should respond.\n"
            "Available bots:\n"
            f"{bot_descriptions}\n"
            "Return ONLY the name of the bot that is best suited to handle the message. "
            "If no specific bot is suitable, default to 'JokeBot' or the most general one. "
            "Do not output any other text, just the bot name."
        )

        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "{input}")]
        )

        model = self.get_model()

        chain = prompt | model | StrOutputParser()

        try:
            response = chain.invoke({"input": message_content})
            bot_name = response.strip()
            current_app.logger.info(f"RouterBot suggested: {bot_name}")

            # Verify if the bot name exists
            bot_names = [b.name.lower() for b in available_bots]
            if bot_name.lower() in bot_names:
                return bot_name

            current_app.logger.warning(
                f"Suggested bot '{bot_name}' not in available bots. Defaulting to first bot."
            )
            # Default to first bot
            return available_bots[0].name
        except Exception as e:
            current_app.logger.error(f"Routing error: {e}", exc_info=True)
            return available_bots[0].name

    def get_bot_response(
        self, bot: Bot, message_history: List[Dict[str, Any]], user_message: str
    ) -> str:
        """
        Generates a response from a specific bot.
        bot: Bot object
        message_history: List of previous messages (dicts with 'sender' and 'content')
        user_message: The new message content
        """
        current_app.logger.info(f"Generating response from bot: {bot.name}")

        system_prompt = bot.system_prompt

        messages = [("system", system_prompt)]

        for msg in message_history:
            role = "human" if msg["sender"] == "user" else "ai"
            messages.append((role, msg["content"]))

        messages.append(("human", user_message))

        prompt = ChatPromptTemplate.from_messages(messages)

        model = self.get_model(model_name=bot.model)

        chain = prompt | model | StrOutputParser()

        try:
            response = str(chain.invoke({}))
            current_app.logger.debug(f"Bot response generated (len: {len(response)})")
            return response
        except Exception as e:
            current_app.logger.error(
                f"Error generating bot response: {e}", exc_info=True
            )
            return (
                "I apologize, but I encountered an error while processing your request."
            )
