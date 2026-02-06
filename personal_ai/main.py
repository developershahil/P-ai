from core.assistant import speak, listen_text, handle_text

if __name__ == "__main__":
    speak("hello")
    while True:
        try:
            text = listen_text()
            handle_text(text)
        except KeyboardInterrupt:
            speak("Exiting.")
            break
