"""Application entry point for the Personal AI assistant."""

from .core.assistant import handle_text, listen_text, speak


def main() -> None:
    """Run the interactive assistant loop."""
    speak("hello")
    while True:
        try:
            text = listen_text()
            handle_text(text)
        except KeyboardInterrupt:
            speak("Exiting.")
            break


if __name__ == "__main__":
    main()
