import os
from dotenv import find_dotenv
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI

# Load the environment variables
load_dotenv(find_dotenv())

# Set the OpenAI API key and model name
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default")
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "default")


# Create the OpenAI chat model
class ChatModel:
    chat_model = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=MODEL_NAME,
        temperature=0,
        verbose=True,
    )