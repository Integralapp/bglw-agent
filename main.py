from config import BT_API_KEY, MODEL_ID
from src.llm import generate
from src.email import check_for_emails
from src.functions import retrieve_functions
from src.prompt import system_prompt_with_functions
import requests

# @Shrey Bohra we need to turn this into 
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # Retrieve functions from a specific API documentation
    functions = retrieve_functions()

    # Inject system prompt with relevant functions that can be used
    prompt = system_prompt_with_functions(functions)

    # @Shrey Bohra 

    generation = generate([{"role": "system", "content": prompt}, {"role": "user", "content": "How are you?"}], stream=False)
    print(generation)