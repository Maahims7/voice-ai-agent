"""
utils.py - Utility Functions & Shared Helpers
----------------------------------------------
Shared helper utilities used across the project:
  - Session memory management
  - Logging configuration
  - Status/result formatting
  - Ollama health check (IMPROVED: fixed timeout handling)
  - Audio validation (IMPROVED: better format support & validation)
  - Compound command parsing (BONUS FEATURE)
"""

import os
import logging
import time
import re
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------

def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure application-wide logging with a clean, readable format.

    Args:
        level (str): Log level ("DEBUG", "INFO", "WARNING", "ERROR")

    Returns:
        logging.Logger: Configured root logger
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("voice_agent")


# ---------------------------------------------------------------------------
# Session Memory with Compound Command Support
# ---------------------------------------------------------------------------

class SessionMemory:
    """
    Maintains an in-session history of all voice interactions.
    Stored as a list of interaction records — NOT persisted to disk.

    BONUS FEATURE: Supports compound commands tracking and context.

    Each record structure:
    {
        "id": int,
        "timestamp": str,
        "input": str,           # What the user said
        "intent": str,          # Detected intent
        "compound": bool,       # Is this part of a compound command?
        "action": str,          # Action taken
        "result_summary": str,  # Short summary of result
        "success": bool,
    }
    """

    def __init__(self, max_history: int = 20):
        self.history: list[dict] = []
        self.max_history = max_history
        self._counter = 0

    def add(
        self,
        user_input: str,
        intent: str,
        action: str,
        result: str,
        success: bool,
        compound: bool = False,
    ) -> None:
        """Add a new interaction to memory."""
        self._counter += 1
        entry = {
            "id": self._counter,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "input": user_input,
            "intent": intent,
            "compound": compound,
            "action": action,
            # Keep result short in memory to save space
            "result_summary": (
                result[:200] + "..." if len(result) > 200 else result
            ),
            "success": success,
        }
        self.history.append(entry)

        # Trim if we exceed max history
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_history(self) -> list[dict]:
        """Return all history entries."""
        return self.history

    def get_last_n(self, n: int = 5) -> list[dict]:
        """Return the last N entries."""
        return self.history[-n:]

    def clear(self) -> None:
        """Clear all history."""
        self.history.clear()
        self._counter = 0

    def to_context_string(self) -> str:
        """
        Format recent history as a string for LLM context injection.
        Useful for compound commands and follow-up queries.
        """
        if not self.history:
            return "No previous interactions."

        lines = ["Recent interactions:"]
        for entry in self.get_last_n(5):
            compound_mark = "[COMPOUND]" if entry.get("compound") else ""
            lines.append(
                f"[{entry['timestamp']}] {compound_mark} User: {entry['input'][:80]}"
                f" → Intent: {entry['intent']}"
                f" → {'✅' if entry['success'] else '❌'}"
            )
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self.history)


# ---------------------------------------------------------------------------
# Ollama Health Check (FIXED: Better timeout & error handling)
# ---------------------------------------------------------------------------

def check_ollama_status() -> dict:
    """
    Check if Ollama is running and which models are available.
    FIXED: Properly handles timeouts and connection errors.

    Returns:
        dict: {
            "running": bool,
            "models": list[str],
            "message": str
        }
    """
    try:
        import requests

        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

        try:
            # Try to get list of available models with timeout
            response = requests.get(
                f"{ollama_url}/api/tags",
                timeout=3,
            )
            if response.status_code == 200:
                data = response.json()
                models = [
                    m.get("name", "unknown")
                    for m in data.get("models", [])
                ]
                if models:
                    model_str = ", ".join(models[:3])
                    if len(models) > 3:
                        model_str += f" +{len(models)-3} more"
                else:
                    model_str = "none pulled yet"

                return {
                    "running": True,
                    "models": models,
                    "message": f"✅ Ollama is running | Models: {model_str}",
                }
            # Returned but no usable model data
            return {
                "running": False,
                "models": [],
                "message": "⚠️ Ollama is reachable but no model data was returned.",
            }
        except requests.exceptions.Timeout:
            return {
                "running": False,
                "models": [],
                "message": "⏱️ Ollama endpoint timeout (check if running)",
            }
        except requests.exceptions.ConnectionError:
            return {
                "running": False,
                "models": [],
                "message": "❌ Ollama connection failed. Ensure the server is running.",
            }

    except ImportError:
        pass
    except Exception as e:
        return {
            "running": False,
            "models": [],
            "message": f"❌ Error checking Ollama: {str(e)[:50]}",
        }

    return {
        "running": False,
        "models": [],
        "message": "❌ Ollama not running. Start with: `ollama serve`",
    }


# ---------------------------------------------------------------------------
# Audio Validation (IMPROVED: Better error messages & format support)
# ---------------------------------------------------------------------------

def validate_audio_file(file_path: str) -> dict:
    """
    Comprehensive validation for audio files before passing to STT.
    IMPROVED: Better error messages and extended format support.

    Args:
        file_path (str): Path to the audio file

    Returns:
        dict: {"valid": bool, "message": str}
    """
    supported_formats = {
        ".wav",
        ".mp3",
        ".m4a",
        ".ogg",
        ".flac",
        ".webm",
        ".wma",
        ".aac",
    }

    path = Path(file_path)

    if not path.exists():
        return {"valid": False, "message": "❌ Audio file does not exist."}

    suffix = path.suffix.lower()
    if suffix not in supported_formats:
        return {
            "valid": False,
            "message": f"❌ Unsupported format '{suffix}'. Try: {', '.join(supported_formats)}",
        }

    # Check file size (max 25 MB to avoid memory issues)
    max_size_mb = 25
    try:
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return {
                "valid": False,
                "message": f"❌ File too large ({file_size_mb:.1f} MB). Max: {max_size_mb} MB.",
            }
        if file_size_mb < 0.01:  # Less than 10 KB
            return {
                "valid": False,
                "message": "❌ Audio file is too small or empty.",
            }
    except OSError as e:
        return {"valid": False, "message": f"❌ Could not read file: {str(e)}"}

    return {"valid": True, "message": "✅ Audio file is valid."}


# ---------------------------------------------------------------------------
# Compound Command Parsing (BONUS FEATURE)
# ---------------------------------------------------------------------------

def parse_compound_commands(text: str) -> list[str]:
    """
    BONUS FEATURE: Parse compound commands from user input.
    Splits commands separated by keywords like "then", "and", "also", "next".

    Example:
        "Create a file, then write code to it, then summarize"
        → ["Create a file", "write code to it", "summarize"]

    Args:
        text (str): User command that may contain multiple intents

    Returns:
        list[str]: List of individual commands
    """
    # Separators that indicate multiple commands
    separators = [r"\bthen\b", r"\band\b", r"\balso\b", r"\bnext\b", r",\s+(?:then)?"]

    commands = re.split("|".join(separators), text, flags=re.IGNORECASE)
    commands = [cmd.strip() for cmd in commands if cmd.strip()]

    return commands


def is_compound_command(text: str) -> bool:
    """
    Check if the user input appears to be a compound command.

    Args:
        text (str): User input text

    Returns:
        bool: True if multiple commands detected
    """
    separators = [r"\bthen\b", r"\band\b", r"\balso\b", r"\bnext\b"]
    return any(
        re.search(sep, text, re.IGNORECASE) for sep in separators
    )


# ---------------------------------------------------------------------------
# Result Formatting Utilities
# ---------------------------------------------------------------------------

def format_intent_badge(intent: str) -> str:
    """Return an emoji badge for display next to the intent label."""
    badges = {
        "CREATE_FILE": "📁",
        "WRITE_CODE": "💻",
        "SUMMARIZE_TEXT": "📝",
        "GENERAL_CHAT": "💬",
        "UNKNOWN": "❓",
    }
    return badges.get(intent, "🔹")


def format_confidence_bar(confidence: float) -> str:
    """Return a text-based confidence bar (e.g., '████░░ 65%')"""
    filled = int(confidence * 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"{bar} {int(confidence * 100)}%"


def get_intent_description(intent: str) -> str:
    """Return a human-readable description of the intent."""
    descriptions = {
        "CREATE_FILE": "Create a new file in the output folder",
        "WRITE_CODE": "Generate code and save it to a file",
        "SUMMARIZE_TEXT": "Summarize the provided text content",
        "GENERAL_CHAT": "Answer a general question or have a conversation",
        "UNKNOWN": "Intent could not be determined",
    }
    return descriptions.get(intent, "Unknown action")


# ---------------------------------------------------------------------------
# Timing Utility
# ---------------------------------------------------------------------------

class Timer:
    """Simple context manager for timing code blocks."""

    def __init__(self, name: str = ""):
        self.name = name
        self.elapsed = 0.0

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed = time.time() - self._start

    def __str__(self):
        return f"{self.name}: {self.elapsed:.2f}s"
