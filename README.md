# AI Browser Voice Agent; Python Script Explanation 🎯

## Introduction 🚨
This Python script implements a simple voice-activated browser assistant that runs in the system tray. It uses speech recognition to listen for commands, text-to-speech to respond, and can open predefined websites or applications based on user input. The assistant also supports a fallback Google search for unrecognized commands. The script leverages libraries like `pyttsx3` for TTS, `speech_recognition` for STT, and `pystray` for the system tray icon.

The code is structured into sections for speech handling, listening, browser actions, the main assistant loop, and tray icon setup. It runs threads for concurrent operations to ensure responsiveness.

Below is a professional, step-by-step explanation of the code, including relevant code snippets, emojis for visual emphasis, and a final summary.

## Step-by-Step Explanation 🛰️

### 1. Importing Libraries 📚
The script begins by importing necessary modules. These handle OS interactions, threading, speech synthesis/recognition, system tray functionality, and image processing for the tray icon.

```python
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
```

- **Purpose**:💼
  - `os`, `sys`, `time`: For system operations, exiting, and delays.
  - `webbrowser`: To open URLs in the default browser.
  - `threading` and `queue`: For concurrent execution (e.g., speech queue) without blocking the main thread.
  - `pyttsx3`: Text-to-speech engine using SAPI5 (Windows-specific).
  - `speech_recognition as sr`: For voice input via Google Speech Recognition.
  - `pystray`: Creates a system tray icon with a menu.
  - `PIL.Image`: Handles the tray icon image.

### 2. Speech Engine Setup 🗣️
A queue is used to manage speech output, ensuring threads can safely add text to be spoken. The TTS engine is initialized with the default voice.

```python
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
```

- **Explanation**:🎤
  - `speech_queue`: A FIFO queue for TTS tasks to prevent race conditions in multi-threaded environments.
  - `engine`: Initialized with SAPI5 (Speech API for Windows). Sets the first available voice.
  - `speech_loop()`: Runs in a thread, continuously pulling text from the queue and speaking it until a `None` sentinel is received.
  - `speak(text)`: Prints the response to console and adds it to the queue for TTS. This function is called throughout the script for user feedback.

### 3. Listening Function 🎙️
This function captures audio from the microphone and recognizes speech using Google's API.

```python
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
```

- **Explanation**:🎤
  - `sr.Recognizer()`: Creates a recognizer instance.
  - `sr.Microphone()`: Uses the default microphone.
  - Listening parameters: Pauses after 1 second of silence; times out after 5 seconds; limits phrase to 8 seconds.
  - `recognize_google()`: Sends audio to Google's free API (English-India language).
  - Returns the recognized query or an empty string on failure (e.g., no speech detected or network issues).

### 4. Browser Function 🌐
Handles opening specific sites or apps from a dictionary, with a fallback to Google search.

```python
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
```

- **Explanation**:🎤
  - `d1`: A dictionary mapping keywords (e.g., "youtube") to URLs or commands.
  - If the key exists:
    - For "notepad", uses `os.system()` to launch the app.
    - For others, opens in a new browser tab.
    - Speaks success/failure feedback.
  - Fallback: Opens a Google search for the query if not in the dictionary.

### 5. Assistant Loop 🔄
The core loop that listens for commands and processes them.

```python
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
```

- **Explanation**:🎤
  - Starts with a welcome message.
  - Infinite loop: Listens, processes lowercase query.
  - Exit: Checks for keywords and terminates the program.
  - Commands:
    - "open [site]": Extracts site and calls `browser()`.
    - Single word: Assumes it's a site name and calls `browser()`.
    - Multi-word: Treats as a search query and opens Google.
  - `time.sleep(1)`: Brief pause to avoid rapid looping.

### 6. System Tray Icon Setup 🛡️
Creates a tray icon with a menu for starting/quitting the assistant.

```python
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
```

- **Explanation**:🎤
  - `on_quit()`: Speaks farewell, stops speech loop, and exits.
  - `on_start()`: Launches the assistant loop in a thread.
  - `setup_tray()`: Loads an icon image (falls back to a blue square if missing). Creates a menu with "Start" and "Quit" options, then runs the icon.

### 7. Main Execution Block 🚀
The entry point that starts threads and sets up the tray.

```python
# ------------------- MAIN -------------------
if __name__ == "__main__":
    threading.Thread(target=speech_loop, daemon=True).start()

    # FIX 👉 start assistant automatically at launch
    threading.Thread(target=assistant_loop, daemon=True).start()

    setup_tray()
```

- **Explanation**:🎤
  - Starts the speech loop thread.
  - Automatically starts the assistant loop (noted as a "FIX" to launch on startup).
  - Calls `setup_tray()` to display the icon and block until quit.

  # Voice Assistant Demo Video 📹

To showcase the functionality of the Voice Assistant, a demo video has been added to the project repository. The video demonstrates the assistant's key features, including voice command recognition, opening websites and applications, and system tray interactions.


## Demo Video 🎥
Watch the demo video here: [📺Voice Assistant Demo](AI-browser.mp4)

This video provides a step-by-step walkthrough of how to use the assistant, including:
- Launching the assistant from the system tray.
- Issuing voice commands like "open youtube" or "exit".
- Observing the assistant's text-to-speech responses.
- Handling fallback Google searches for unrecognized commands.

For the best experience, ensure your microphone and speakers are configured correctly before running the assistant. Refer to the main README for setup instructions. 🚀

## Summary 🛑
This script creates a voice-controlled assistant that minimizes to the system tray, listens for commands like "open youtube" or "exit", and responds via speech while opening sites/apps. It uses threading for non-blocking operations, a queue for safe speech handling, and fallback mechanisms for robustness. Potential improvements include error handling for microphone access, expanding the site dictionary, or adding more commands. Overall, it's a lightweight, Windows-focused tool demonstrating integration of speech tech with desktop utilities. 🚀🗣️