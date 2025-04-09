""" Run a command in the terminal using a local LLM """
import os
import subprocess
import requests


def ask_llm_to_explain_error(command, error):
    """ Ask the local LLM to explain an error """
    system_instruction = "Provide a detailed explanation of the following error message." \
                         "This error message is caused by the command included in the prompt. " \
                         "Include possible causes and solutions. Do not include any code or commands." \
                         "Provide the responses as much compressed as possible." \
                         "Do not include any extra text or explanation."
    full_prompt = f"{system_instruction}\n\nCommand: {command}\n\nError: {error}\nExplanation:"
    try:
        response = requests.post(
            os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate'),
            json={
                'model': os.getenv('OLLAMA_MODEL', 'gemma3'),
                'prompt': full_prompt,
                'stream': False
            },
            timeout=30,
        )
        response.raise_for_status()
        response_json = response.json()
        if 'response' not in response_json:
            raise KeyError(f"'response' key not found in API response: {response_json}")
        return response_json['response'].strip()
    except requests.exceptions.ReadTimeout:
        return "Error: The request to the Ollama server timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the Ollama server. {str(e)}"


def ask_llm_for_command(prompt):
    """ Ask the local LLM to generate a safe terminal command """
    system_instruction = "Translate the following user request " \
                         "into a safe Linux terminal command. Only return " \
                         "the command. Do not explain or add extra text."
    full_prompt = f"{system_instruction}\n\nUser: {prompt}\nCommand:"

    try:
        response = requests.post(
            os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate'),
            json={
                'model': os.getenv('OLLAMA_MODEL', 'gemma3'),
                'prompt': full_prompt,
                'stream': False
            },
            timeout=5,
        )
        response.raise_for_status()
        response_json = response.json()
        if 'response' not in response_json:
            raise KeyError(f"'response' key not found in API response: {response_json}")
        return response_json['response'].strip()
    except requests.exceptions.ReadTimeout:
        return "Error: The request to the Ollama server timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the Ollama server. {str(e)}"


def run_command(command):
    """ Run the terminal command safely """
    try:
        result = subprocess.check_output(command, shell=True,
                                         stderr=subprocess.STDOUT,
                                         text=True, timeout=5)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"Command error:\n{e.output.strip()}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def run_ai_command(natural_prompt):
    """ List the files in the current directory """
    np_command = ask_llm_for_command(natural_prompt)
    print(f"🛠️  LLM Command: {np_command}")

    np_output = run_command(np_command)
    print("📂 Command Output:\n", np_output)
    return np_command, np_output


def prompt_ollama_http(prompt: str):
    """ Send a prompt to the local Ollama server and get the response """
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': os.getenv('OLLAMA_MODEL', 'gemma3'),
            'prompt': prompt,
            'stream': False
        },
        timeout=5,
    )
    return response.json()['response'].strip()
