import os
import sys
import time
import webbrowser
import threading
import queue
import pyttsx3
import speech_recognition as sr
import pystray
from pystray import MenuItem as item
from PIL import Image

# ------------------- SPEECH ENGINE -------------------
speech_queue = queue.Queue()
engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)

def speech_loop():
    while True:
        text = speech_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        speech_queue.task_done()

def speak(text):
    print(f"Assistant: {text}")
    speech_queue.put(text)

# ------------------- LISTEN FUNCTION -------------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            query = r.recognize_google(audio, language="en-in")
            print(f"You said: {query}")
            return query
        except Exception:
            return ""

# ------------------- BROWSER FUNCTION -------------------
def browser(url):
    d1 = {
        "youtube": "https://www.youtube.com/",
        "wikipedia": "https://www.wikipedia.org/",
        "notepad": "notepad.exe",
        "chatgpt": "https://chatgpt.com/",
        "gmail": "https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox",
        "github": "https://github.com/mariam-2324",
        "linkedin": "http://www.linkedin.com/in/mariam-saad-b8645335b",
        "facebook": "https://www.facebook.com/",
    }

    brows = d1.get(url)
    if brows:
        try:
            if url == "notepad":
                os.system(brows)
            else:
                webbrowser.open_new_tab(brows)
            speak(f"Opening {url}")
        except Exception as e:
            speak(f"Failed to open {url}")
            print(f"Error opening {url}: {e}")
    else:
        # Fallback search
        speak(f"Searching for {url} on the internet")
        webbrowser.open_new_tab(f"https://www.google.com/search?q={url}")

# ------------------- ASSISTANT LOOP -------------------
def assistant_loop():
    speak("Voice browser assistant is active. Say your command.")
    while True:
        query = listen()
        if not query:
            continue

        query = query.lower().strip()
        print(f"Processing: {query}")

        # Exit command
        if any(exit_word in query for exit_word in ["exit", "stop", "bye", "quit"]):
            speak("Goodbye!")
            speech_queue.put(None)
            os._exit(0)

        # Handle "open ..." OR just saying site name
        if query.startswith("open "):
            site = query.replace("open", "").strip()
            if site:
                browser(site)
        else:
            # Try dictionary or fallback
            words = query.split()
            if len(words) == 1:  
                browser(words[0])
            else:
                speak("Processing your request...")
                webbrowser.open_new_tab(f"https://www.google.com/search?q={query}")

        time.sleep(1)

# ------------------- TRAY ICON -------------------
def on_quit(icon, item):
    speak("Assistant terminated.")
    speech_queue.put(None)
    icon.stop()
    os._exit(0)

def on_start(icon, item):
    threading.Thread(target=assistant_loop, daemon=True).start()
    speak("Listening started.")

def setup_tray():
    try:
        icon_image = Image.open("mic_icon.png")
    except:
        icon_image = Image.new("RGB", (64, 64), color="blue")

    menu = (item("Start", on_start), item("Quit", on_quit))
    icon = pystray.Icon("VoiceAssistant", icon_image, "Voice Assistant", menu)
    icon.run()

# ------------------- MAIN -------------------
if __name__ == "__main__":
    threading.Thread(target=speech_loop, daemon=True).start()

    # FIX 👉 start assistant automatically at launch
    threading.Thread(target=assistant_loop, daemon=True).start()

    setup_tray()
