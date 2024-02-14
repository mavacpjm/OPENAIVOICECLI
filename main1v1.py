import requests
import json
import pyttsx3
import pygame
import io
import os

url = "http://localhost:11434/api/generate"

# Initialize pygame mixer
pygame.mixer.init()

def play_audio(audio_text):
    with io.BytesIO(audio_text) as file:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

def generate_response(prompt):
    response = requests.post(url, json={"model": "mistral", "stream": False, "prompt": prompt}, stream=True)
    
    accumulated_response = ""
    audio_data = b""
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if "response" in data:
                response_text = data["response"]
                if accumulated_response.endswith(" ") and response_text.startswith(" "):
                    accumulated_response += response_text[1:]  # Add the response without the initial space
                else:
                    accumulated_response += response_text
                
                # Speak the accumulated response outside the loop
                engine = pyttsx3.init()
                engine.save_to_file(accumulated_response, 'temp.mp3')
                engine.runAndWait()
                with open('temp.mp3', 'rb') as f:
                    audio_data += f.read()
                
                yield accumulated_response
                
                # Delete the temp.mp3 file after using it
                os.remove('temp.mp3')
                
                # Create a new empty temp.mp3 file for the next use
                open('temp.mp3', 'w').close()
                
            if "done" in data and data["done"]:
                break
    
    # Play the accumulated audio after the response has been fully accumulated
    if audio_data:
        play_audio(audio_data)

def main():
    while True:
        prompt = input("Enter your prompt here: ")
        for response in generate_response(prompt):
            print(response)

if __name__ == "__main__":
    main()
