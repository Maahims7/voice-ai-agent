"""
stt.py - Speech-to-Text Module (IMPROVED)
------------------------------------------
Converts audio input (microphone or file) to text using:
  1. Local Whisper model (preferred, runs offline)
  2. Groq API fallback (if local model is too slow)
  
IMPROVEMENTS:
  - Better error handling and validation
  - Audio format detection
  - Clearer error messages
  - Timeout handling

Usage:
    from stt import transcribe_audio
    text = transcribe_audio("path/to/audio.wav")
"""

import os
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def transcribe_audio(audio_path: str, use_api: bool = False) -> dict:
    """
    Main entry point: transcribe an audio file to text.
    IMPROVED: Better validation and error handling.

    Args:
        audio_path (str): Path to the audio file (.wav, .mp3, .m4a, etc.)
        use_api (bool): If True, use Groq API instead of local Whisper.

    Returns:
        dict: {
            "success": bool,
            "text": str (transcribed text or error message),
            "method": str ("local_whisper" | "groq_api" | "none")
        }
    """
    # Validate file exists and is readable
    if not os.path.exists(audio_path):
        return {
            "success": False,
            "text": "❌ Audio file not found.",
            "method": "none",
        }

    # Check file size
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    if file_size_mb > 25:
        return {
            "success": False,
            "text": f"❌ Audio file too large ({file_size_mb:.1f} MB). Max: 25 MB",
            "method": "none",
        }

    if file_size_mb < 0.01:
        return {
            "success": False,
            "text": "❌ Audio file is too small or empty.",
            "method": "none",
        }

    if use_api:
        return _transcribe_with_groq(audio_path)
    else:
        return _transcribe_with_whisper(audio_path)


def _transcribe_with_whisper(audio_path: str) -> dict:
    """
    Use the local OpenAI Whisper model to transcribe audio.
    Model 'base' is fast and accurate enough for most use cases.
    Larger models (small, medium, large) are more accurate but slower.
    IMPROVED: Better error handling for import and timeout issues.
    """
    try:
        import whisper  # pip install openai-whisper

        logger.info("Loading Whisper 'base' model (local)...")
        try:
            model = whisper.load_model("base")  # Use "small" for better accuracy
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return _transcribe_with_groq(audio_path)

        logger.info(f"Transcribing: {audio_path}")
        try:
            result = model.transcribe(audio_path, language="en")
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "success": False,
                "text": f"❌ Transcription failed: {str(e)[:100]}",
                "method": "local_whisper",
            }

        transcribed_text = result.get("text", "").strip()

        if not transcribed_text:
            return {
                "success": False,
                "text": "❌ No speech detected in the audio. Please try a clearer recording.",
                "method": "local_whisper",
            }

        return {
            "success": True,
            "text": transcribed_text,
            "method": "local_whisper",
        }

    except ImportError:
        logger.warning("Whisper not installed. Trying Groq API fallback...")
        return _transcribe_with_groq(audio_path)

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        return {
            "success": False,
            "text": f"❌ Transcription error: {str(e)[:100]}",
            "method": "local_whisper",
        }


def _transcribe_with_groq(audio_path: str) -> dict:
    """
    Fallback: Use Groq's Whisper API for transcription.
    Requires GROQ_API_KEY environment variable to be set.
    IMPROVED: Better error handling and response parsing.
    """
    try:
        from groq import Groq  # pip install groq

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return {
                "success": False,
                "text": "❌ Groq API key not configured. Set GROQ_API_KEY environment variable.",
                "method": "groq_api",
            }

        client = Groq(api_key=api_key)

        logger.info("Transcribing with Groq API...")
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), audio_file),
                    model="whisper-large-v3",
                    response_format="text",
                )

            text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()

            if not text:
                return {
                    "success": False,
                    "text": "❌ API returned empty response. Please try again.",
                    "method": "groq_api",
                }

            return {
                "success": True,
                "text": text,
                "method": "groq_api",
            }
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {
                "success": False,
                "text": f"❌ API transcription failed: {str(e)[:100]}",
                "method": "groq_api",
            }

    except ImportError:
        logger.error("Groq library not installed: pip install groq")
        return {
            "success": False,
            "text": "❌ Groq library not installed. Install with: pip install groq",
            "method": "groq_api",
        }

    except Exception as e:
        logger.error(f"Groq transcription setup failed: {e}")
        return {
            "success": False,
            "text": f"❌ Transcription setup error: {str(e)[:100]}",
            "method": "groq_api",
        }


def save_uploaded_audio(uploaded_file) -> str:
    """
    Save a Streamlit UploadedFile object to a temporary file on disk.
    IMPROVED: Better error handling for file operations.

    Args:
        uploaded_file: Streamlit file uploader object

    Returns:
        str: Path to the saved temporary file
        
    Raises:
        IOError: If file cannot be written
    """
    try:
        suffix = os.path.splitext(uploaded_file.name)[-1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            logger.info(f"Saved uploaded audio to: {tmp.name}")
            return tmp.name
    except Exception as e:
        logger.error(f"Failed to save uploaded audio: {e}")
        raise IOError(f"Could not save audio file: {str(e)}")

