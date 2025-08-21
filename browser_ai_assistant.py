import os
import webbrowser
import subprocess
import requests   # kept (unused now), per your request not to change other parts
import base64     # kept (unused now)
from difflib import get_close_matches
import speech_recognition as sr
import pyttsx3
from datetime import datetime

# === NEW: Gemini imports (minimal addition) ==========================
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
# =====================================================================

# -------------------- SETTINGS --------------------
FOLDER_PATHS = {
    "downloads": r"C:\Users\PCS\Downloads",
    "documents": r"C:\Users\PCS\Documents",
    "desktop":   r"C:\Users\PCS\Desktop",
    "d drive":   r"D:\\",
    "voice agent": r"D:\Voice-driven agent",
    "pictures":  r"C:\Users\PCS\Pictures",
    "bandicam":  r"C:\Users\PCS\Documents\Bandicam",
    "music":     r"C:\Users\PCS\Music",
    "videos":    r"C:\Users\PCS\Videos",
}

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "instagram": "https://www.instagram.com",
    "canva": "https://www.canva.com",
    "linkedin": "https://www.linkedin.com",
    "google": "https://www.google.com",
}

APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",   # safer than Paint3D.exe
}

# === NEW: Initialize Gemini client (reads your .env) =================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()
# =====================================================================

# -------------------- SPEECH ENGINE --------------------
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# -------------------- FUZZY MATCH --------------------
def fuzzy_lookup(command, mapping):
    matches = get_close_matches(command, mapping.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None

# -------------------- IMAGE GENERATION (SWITCHED TO GEMINI) ----------
def generate_image(prompt: str):
    """
    Replaced Vyro with Gemini 2.0 Flash Preview Image Generation.
    Saves PNG to Generated_Images and opens it (your previous behavior).
    """
    # Safety: ensure API key is present
    if not API_KEY:
        speak("Gemini API key is not set. Please add it to your .env file.")
        return

    try:
        # Ask for text + image response (matches the sample you verified)
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )

        got_image = False
        # Iterate over parts: optional descriptive text + the image blob
        for part in response.candidates[0].content.parts:
            if getattr(part, "text", None):
                print("📝 Gemini says:", part.text)
                # also speak back the text so you hear the description
                speak(part.text)

            if getattr(part, "inline_data", None) and getattr(part.inline_data, "mime_type", "").startswith("image/"):
                # NOTE: inline_data.data is already bytes for the SDK you're using.
                image = Image.open(BytesIO(part.inline_data.data))
                image.load()  # make sure it’s fully decoded

                os.makedirs("Generated_Images", exist_ok=True)
                filename = f"Generated_Images/gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                image.save(filename, format="PNG")
                print(f"✅ Image saved at {filename}")
                speak("Here is your generated image.")
                try:
                    os.startfile(filename)  # preserves your current workflow (e.g., Canva pickup)
                except Exception:
                    pass
                got_image = True

        if not got_image:
            speak("I did not receive an image from Gemini for that request.")

    except Exception as e:
        print(f"❌ Error generating image: {e}")
        speak("There was an error in generating the image.")

# -------------------- MAIN COMMAND HANDLER --------------------
def handle_command(command):
    command = command.lower()

    # === MINOR ADD: extra exit words as requested ====================
    if any(x in command for x in ["exit", "quit", "goodbye", "bye"]):
        speak("Goodbye Mariam, see you soon.")
        exit()
    # =================================================================

    # Folders
    folder = fuzzy_lookup(command, FOLDER_PATHS)
    if folder:
        path = FOLDER_PATHS[folder]
        if os.path.exists(path):
            os.startfile(path)
            speak(f"Opening {folder}")
            return

    # Websites
    site = fuzzy_lookup(command, WEBSITES)
    if site:
        webbrowser.open(WEBSITES[site])
        speak(f"Opening {site}")
        return

    # Applications
    app = fuzzy_lookup(command, APPS)
    if app:
        try:
            subprocess.Popen(APPS[app])
            speak(f"Opening {app}")
        except Exception:
            speak(f"Cannot open {app}")
        return

    # Image Generation (same triggers you already had)
    if any(phrase in command for phrase in ["generate image", "create an image", "make an image", "draw", "imagine"]):
        prompt = command
        for phrase in ["generate image of", "generate image", "create an image of", "create an image",
                       "make an image of", "make an image", "draw", "imagine"]:
            prompt = prompt.replace(phrase, "").strip()
        if prompt:
            generate_image(prompt)
        else:
            speak("What should I create an image of?")
        return

    # Default
    speak("Sorry, I didn't understand that command.")

# -------------------- LISTENING LOOP --------------------
def listen():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Speech recognition service error.")
        return ""

if __name__ == "__main__":
    speak("Hello Mariam, your voice agent is ready.")
    while True:
        print("Listening...")
        cmd = listen()
        if cmd:
            print("You said:", cmd)
            handle_command(cmd)
