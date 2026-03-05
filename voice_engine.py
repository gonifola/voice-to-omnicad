# Voice Engine — Voice to OmniCAD
# Speech-to-text capture (Whisper-ready stub)

import bpy

class VoiceCapture:
    """Handles microphone input and speech-to-text conversion."""

    def __init__(self):
        self.is_listening = False
        self._engine = None

    def start_listening(self):
        self.is_listening = True
        print("[OmniCAD] Voice capture started")
        # TODO Phase 2: integrate speech_recognition / Whisper API
        # Example:
        #   import speech_recognition as sr
        #   r = sr.Recognizer()
        #   with sr.Microphone() as source:
        #       audio = r.listen(source)
        #   text = r.recognize_whisper_api(audio, api_key=config.OPENAI_API_KEY)

    def stop_listening(self):
        self.is_listening = False
        print("[OmniCAD] Voice capture stopped")

    def process_audio(self, audio_bytes=None):
        """Convert audio bytes to text. Returns placeholder until Whisper is wired."""
        if audio_bytes is None:
            return "create a sphere"  # placeholder for manual testing
        # TODO: send to Whisper API or local Whisper model
        return ""
