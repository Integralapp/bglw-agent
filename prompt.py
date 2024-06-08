from typing import Dict, List, TypedDict


class Functions(TypedDict):
    function_name: str
    function_inputs: List[Dict[str, str]]
    function_outputs: List[Dict[str, str]]

    def __str__(self):
        inputs = ', '.join([f"{name}: {typ}" for input in self['function_inputs'] for name, typ in input.items()])
        outputs = ', '.join([f"{name}: {typ}" for output in self['function_outputs'] for name, typ in output.items()])
        return f"Function Name: {self['function_name']}\nInputs: {inputs}\nOutputs: {outputs}"

def system_prompt_with_functions(functions: List[Functions], *args, **kwargs):
    prompt = """
    You are a large language model whose job is to output a function with a JSON containing the keys and values of parameters needed for that function.

    You will be provided a user query, and given that query you are to justify which function to use.

    I will provide you with the necessary context and functionality to determine what function should be called next.

    Here are the available functions:
    """

    function_descriptions = [str(function) for function in functions]
    
    prompt += "\n\n".join(function_descriptions)
    
    return prompt

