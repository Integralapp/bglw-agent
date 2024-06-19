from typing import Dict, List, TypedDict
from src.functions import Functions


def system_prompt(additional_context: str = "", *args, **kwargs):
    prompt = """
    You are a large language model whose job is to output a function with a JSON containing the keys and values of parameters needed for that function.

    You will be provided a list of user and assistant back and forth, and then a final user message in which you are to determine whether tool use is necessary to be executed before passing back a message

    I will provide you with the necessary context through user and assistant messages and functionality to determine what function should be called next.
    """

    prompt += additional_context

    return prompt


def system_prompt_with_functions(functions: List[Functions], *args, **kwargs):
    prompt = """
    You are a large language model whose job is to output a function with a JSON containing the keys and values of parameters needed for that function.

    You will be provided a user query, and given that query you are to justify which function to use.

    I will provide you with the necessary context and functionality to determine what function should be called next.

    Here are the available functions:
    """

    function_descriptions = [str(function) for function in functions]

    prompt += "\n\n".join(function_descriptions)

    prompt += "\n\n Please make sure that your output is in this structure: \n\n{Function Name}\n{input_1}\n{input_2}\n{input_3}\n to fill out as many inputs as needed"

    return prompt
