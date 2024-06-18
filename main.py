from config import BT_API_KEY, MODEL_ID
from src.llm import generate
from src.functions import retrieve_functions
from src.prompt import system_prompt_with_functions

from src.google_email import email_thread_to_messages
import requests

# @Shrey Bohra we need to turn this into a webhook
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    conversation_id = "PLACEHOLDER"

    # Retrieve functions from a specific API documentation
    functions = retrieve_functions()

    # Inject system prompt without functions (passed into Groq directly)
    prompt = system_prompt(additional_context="")

    # Retrieve full email thread and transform to OpenAI message format
    messages = email_thread_to_messages(conversation_id=conversation_id)

    available_functions = {func["name"]: func.func for func in functions}

    generation = generate(
        [{"role": "system", "content": prompt}, *messages],
        available_functions,
        stream=False,
    )
    print(generation)
