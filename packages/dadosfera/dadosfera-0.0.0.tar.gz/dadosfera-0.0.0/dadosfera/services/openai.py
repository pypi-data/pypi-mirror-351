import openai


def generate_response(prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0) -> str:
    """
    Generates a response using OpenAI's ChatGPT models based on a given prompt.
    
    Args:
        prompt (str): The input text prompt to generate a response from
        model (str, optional): The OpenAI model to use. Defaults to "gpt-3.5-turbo"
        temperature (float, optional): Controls randomness in the response. 
            0 is most deterministic, 1 is most creative. Defaults to 0
    
    Returns:
        str: The generated response text from the model
    
    Example:
        response = generate_response("Summarize this article:", model="gpt-4", temperature=0.7)
        print(response)
    
    Note:
        - Requires the 'openai' library and valid API credentials
        - Uses ChatCompletion API which is optimized for dialogue
        - Lower temperature (0-0.3) is better for factual/analytical tasks
        - Higher temperature (0.7-1.0) is better for creative tasks
        - Does not handle API errors, caller should implement error handling
    """
    response = openai.ChatCompletion.create(
        model=model,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content