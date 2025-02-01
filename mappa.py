import speech_recognition as sr
import pyttsx3
import requests
import json
import re
import subprocess
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
LLAMA_MODEL_PATH = os.getenv('LLAMA_MODEL_PATH')

engine = pyttsx3.init()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

def load_llama_model():
    try:
        # Load tokenizer
        tokenizer = LlamaTokenizer.from_pretrained(LLAMA_MODEL_PATH)
        
        # Load model
        model = LlamaForCausalLM.from_pretrained(
            LLAMA_MODEL_PATH,
            ignore_mismatched_sizes=True
        )
        
        print("Model and tokenizer loaded successfully.")
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."

def interpret_command_with_api(user_input):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{
            "role": "user",
            "content": f"""You are a terminal assistant. Translate the following command into a terminal command. Do not include any explanations or additional text, just the terminal command:
            User: {user_input}
            Assistant:"""
        }]
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        command = result["choices"][0]["message"]["content"].strip()
        command = re.sub(r"```(bash|shell)?", "", command).strip()
        return command
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "Error interpreting command."

def interpret_command_with_local_model(user_input, model, tokenizer):
    if model is None or tokenizer is None:
        return "Error: Model or tokenizer not loaded."
    
    try:
        prompt = f"""You are a terminal assistant. Translate the following command into a terminal command:
        User: {user_input}
        Assistant:"""
        
        # Tokenize the input
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Generate the output
        outputs = model.generate(**inputs, max_length=100)
        
        # Decode the output
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the assistant's response
        return response.split("Assistant:")[-1].strip()
    except Exception as e:
        return f"Error interpreting command: {e}"

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def initialize_repo():
    try:
        subprocess.run("git init", check=True, shell=True)
        subprocess.run("git remote add origin https://github.com/Ghruank/mappa_x.git", check=True, shell=True)
        subprocess.run("git add .", check=True, shell=True)
        subprocess.run('git commit -m "Initial commit"', check=True, shell=True)
        subprocess.run("git branch -M main", check=True, shell=True)
        subprocess.run("git push -u origin main", check=True, shell=True)
        print("Repository initialized and code pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Error initializing repo: {e}")

def speak(text):
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'female' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 150)  # Speed up the speech
    engine.say(text)
    engine.runAndWait()

def main():
    mode = input("Choose mode (local/api): ").strip().lower()
    
    if mode == "api":
        print("Using Groq API.")
        model, tokenizer = None, None
    elif mode == "local":
        print("Loading Llama 2 model...")
        model, tokenizer = load_llama_model()
        if model is None or tokenizer is None:
            print("Failed to load model. Exiting.")
            return
    else:
        print("Invalid mode. Exiting.")
        return
    
    print("Ready to assist!")
    speak("Mappa is Ready to assist!")
    
    while True:
        user_input = listen()
        if "initialise repository" in user_input.lower():
            initialize_repo()
            speak("Repository initialized and code pushed to GitHub.")
        elif "jarvis" in user_input.lower():
            if mode == "api":
                terminal_command = interpret_command_with_api(user_input)
            elif mode == "local":
                terminal_command = interpret_command_with_local_model(user_input, model, tokenizer)
            
            output = execute_command(terminal_command)
            print(f"{output}")

            speak(output)

if __name__ == "__main__":
    main()