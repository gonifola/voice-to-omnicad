# Voice Engine — Voice to OmniCAD
# Whisper API STT (OpenAI) — live mic capture

import bpy
import os
import tempfile
import threading

try:
    import requests
except ImportError:
    requests = None

try:
    from . import config
except ImportError:
    import config


class VoiceCapture:
    """Handles microphone input and Whisper speech-to-text conversion."""

    def __init__(self):
        self.is_listening   = False
        self._thread        = None
        self.last_transcript = ""
        self._callback      = None  # called with transcript string when ready

    # ── Start / Stop ───────────────────────────────────────────

    def start_listening(self, callback=None):
        """Start background mic capture. callback(text) fired when speech recognized."""
        self._callback   = callback
        self.is_listening = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        print("[OmniCAD] Voice capture started")

    def stop_listening(self):
        self.is_listening = False
        print("[OmniCAD] Voice capture stopped")

    # ── Internal capture loop ──────────────────────────────────

    def _capture_loop(self):
        """Background thread: record → Whisper → callback."""
        try:
            import speech_recognition as sr
        except ImportError:
            print("[OmniCAD] speech_recognition not installed — run: pip install SpeechRecognition")
            self.is_listening = False
            return

        r      = sr.Recognizer()
        r.pause_threshold = 1.0

        with sr.Microphone() as source:
            print("[OmniCAD] Adjusting for ambient noise…")
            r.adjust_for_ambient_noise(source, duration=1)
            while self.is_listening:
                try:
                    audio = r.listen(
                        source,
                        timeout=config.VOICE_TIMEOUT,
                        phrase_time_limit=config.VOICE_PHRASE_TIME_LIMIT
                    )
                    self._transcribe(audio.get_wav_data())
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"[OmniCAD] Mic error: {e}")
                    break

    def _transcribe(self, wav_bytes):
        """Send WAV bytes to Whisper API; fire callback with transcript."""
        if not requests:
            print("[OmniCAD] requests not available")
            return
        key = getattr(config, "OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
        if not key:
            # Fallback: use grok/claude to transcribe description
            print("[OmniCAD] No OPENAI_API_KEY — set it in config.py for voice input")
            return
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(wav_bytes)
                tmp_path = tmp.name

            with open(tmp_path, "rb") as f:
                resp = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {key}"},
                    files={"file": ("audio.wav", f, "audio/wav")},
                    data={"model": "whisper-1", "language": "en"},
                    timeout=30,
                )
            os.unlink(tmp_path)
            resp.raise_for_status()
            text = resp.json().get("text", "").strip()
            if text:
                self.last_transcript = text
                print(f"[OmniCAD] Heard: {text}")
                if self._callback:
                    self._callback(text)
        except Exception as e:
            print(f"[OmniCAD] Whisper error: {e}")

    def transcribe_file(self, filepath):
        """Transcribe an existing audio file. Returns text string."""
        if not requests:
            return ""
        key = getattr(config, "OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
        if not key:
            return ""
        try:
            with open(filepath, "rb") as f:
                resp = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {key}"},
                    files={"file": (os.path.basename(filepath), f)},
                    data={"model": "whisper-1", "language": "en"},
                    timeout=30,
                )
            resp.raise_for_status()
            return resp.json().get("text", "").strip()
        except Exception as e:
            print(f"[OmniCAD] Whisper file error: {e}")
            return ""
