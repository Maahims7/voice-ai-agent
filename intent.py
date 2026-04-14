"""
intent.py - Intent Classification Module
------------------------------------------
Analyzes transcribed text and classifies the user's intent using a
local LLM (via Ollama) or falls back to keyword-based matching.

Supported Intents:
  - CREATE_FILE      : User wants to create a new file
  - WRITE_CODE       : User wants to generate/write code to a file
  - SUMMARIZE_TEXT   : User wants to summarize provided content
  - GENERAL_CHAT     : General conversation / questions
  - UNKNOWN          : Could not determine intent

Usage:
    from intent import classify_intent
    result = classify_intent("Create a Python file with a hello world function")
"""

import re
import json
import logging
import os

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent constants — used throughout the project for consistency
# ---------------------------------------------------------------------------
INTENT_CREATE_FILE = "CREATE_FILE"
INTENT_WRITE_CODE = "WRITE_CODE"
INTENT_SUMMARIZE = "SUMMARIZE_TEXT"
INTENT_GENERAL_CHAT = "GENERAL_CHAT"
INTENT_UNKNOWN = "UNKNOWN"

ALL_INTENTS = [
    INTENT_CREATE_FILE,
    INTENT_WRITE_CODE,
    INTENT_SUMMARIZE,
    INTENT_GENERAL_CHAT,
]

# ---------------------------------------------------------------------------
# Prompt sent to the LLM for intent classification
# ---------------------------------------------------------------------------
INTENT_SYSTEM_PROMPT = """You are an intent classification assistant for a voice-controlled AI agent.

Given a user's transcribed voice command, identify the PRIMARY intent.

Return ONLY a valid JSON object with these exact keys:
{
  "intent": "<INTENT>",
  "confidence": <0.0 to 1.0>,
  "filename": "<suggested filename or null>",
  "language": "<programming language or null>",
  "summary_target": "<text to summarize or null>",
  "reasoning": "<brief explanation>"
}

Available intents:
- CREATE_FILE     : User wants to create a new empty file or text file
- WRITE_CODE      : User wants to generate code and save it to a file
- SUMMARIZE_TEXT  : User wants to summarize some text/content
- GENERAL_CHAT    : General question, greeting, or conversation

Rules:
- If user mentions writing/generating code → WRITE_CODE
- If user mentions creating a file (no code implied) → CREATE_FILE
- If user mentions "summarize" → SUMMARIZE_TEXT
- Otherwise → GENERAL_CHAT
- Be conservative: when unsure between WRITE_CODE and CREATE_FILE, pick WRITE_CODE
"""


def classify_intent(text: str, use_ollama: bool = True) -> dict:
    """
    Classify the intent of a transcribed voice command.

    Args:
        text (str): The transcribed text from the user
        use_ollama (bool): Whether to try Ollama LLM first

    Returns:
        dict: {
            "intent": str,
            "confidence": float,
            "filename": str | None,
            "language": str | None,
            "summary_target": str | None,
            "reasoning": str,
            "method": str
        }
    """
    if not text or not text.strip():
        return _unknown_result("Empty input text", "none")

    if use_ollama:
        result = _classify_with_ollama(text)
        if result["intent"] != INTENT_UNKNOWN:
            return result

    # Fall back to keyword-based matching if Ollama fails
    logger.warning("Falling back to keyword-based intent matching.")
    return _classify_with_keywords(text)


def _classify_with_ollama(text: str) -> dict:
    """
    Use local Ollama LLM (llama3 model) for intent classification.
    Ollama must be running: `ollama serve`
    Model must be pulled: `ollama pull llama3`
    """
    try:
        import requests

        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

        payload = {
            "model": os.environ.get("OLLAMA_MODEL", "llama3"),
            "prompt": f"{INTENT_SYSTEM_PROMPT}\n\nUser command: \"{text}\"\n\nJSON response:",
            "stream": False,
            "format": "json",  # Forces Ollama to return valid JSON
        }

        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=(10, 180),  # connect/read timeout for slower local model inference
        )

        if response.status_code != 200:
            logger.error(f"Ollama returned status {response.status_code}")
            return _unknown_result("Ollama request failed", "ollama")

        raw = response.json().get("response", "")
        parsed = _safe_parse_json(raw)

        if parsed and "intent" in parsed:
            intent = parsed.get("intent", INTENT_UNKNOWN).upper()
            # Validate the intent is one we recognize
            if intent not in ALL_INTENTS:
                intent = INTENT_GENERAL_CHAT

            return {
                "intent": intent,
                "confidence": float(parsed.get("confidence", 0.8)),
                "filename": parsed.get("filename"),
                "language": parsed.get("language"),
                "summary_target": parsed.get("summary_target"),
                "reasoning": parsed.get("reasoning", "Classified by Ollama LLM"),
                "method": "ollama_llm",
            }

    except requests.exceptions.ConnectionError:
        logger.warning("Ollama not running. Start with: ollama serve")
    except Exception as e:
        logger.error(f"Ollama classification error: {e}")

    return _unknown_result("Ollama unavailable", "ollama")


def _classify_with_keywords(text: str) -> dict:
    """
    Simple rule-based keyword matching as a fallback when Ollama isn't available.
    Less accurate but always works without any external dependencies.
    """
    text_lower = text.lower()

    # --- WRITE_CODE keywords ---
    code_keywords = [
        "write code", "generate code", "create code", "write a script",
        "python script", "python file", "javascript", "function", "class",
        "program", "algorithm", "implement", "code for", "write a program",
        "generate a", "make a function", "create a function",
    ]

    # --- CREATE_FILE keywords ---
    file_keywords = [
        "create a file", "make a file", "new file", "create file",
        "empty file", "text file", "create a text", "make a text",
        "create a new file", "touch file",
    ]

    # --- SUMMARIZE keywords ---
    summary_keywords = [
        "summarize", "summary", "brief", "tldr", "condense",
        "key points", "main points", "short version", "overview",
    ]

    # Check in order of specificity
    if any(kw in text_lower for kw in code_keywords):
        lang = _extract_language(text_lower)
        fname = _extract_filename(text) or f"output.{_lang_to_ext(lang)}"
        return {
            "intent": INTENT_WRITE_CODE,
            "confidence": 0.75,
            "filename": fname,
            "language": lang,
            "summary_target": None,
            "reasoning": "Keyword match: code generation detected",
            "method": "keyword_fallback",
        }

    if any(kw in text_lower for kw in file_keywords):
        fname = _extract_filename(text) or "new_file.txt"
        return {
            "intent": INTENT_CREATE_FILE,
            "confidence": 0.75,
            "filename": fname,
            "language": None,
            "summary_target": None,
            "reasoning": "Keyword match: file creation detected",
            "method": "keyword_fallback",
        }

    if any(kw in text_lower for kw in summary_keywords):
        return {
            "intent": INTENT_SUMMARIZE,
            "confidence": 0.75,
            "filename": None,
            "language": None,
            "summary_target": text,
            "reasoning": "Keyword match: summarization requested",
            "method": "keyword_fallback",
        }

    # Default to general chat
    return {
        "intent": INTENT_GENERAL_CHAT,
        "confidence": 0.6,
        "filename": None,
        "language": None,
        "summary_target": None,
        "reasoning": "No specific intent keywords found; defaulting to chat",
        "method": "keyword_fallback",
    }


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _safe_parse_json(text: str) -> dict | None:
    """Extract and parse the first JSON object found in a string."""
    try:
        # Try direct parse first
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block within text
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _unknown_result(reason: str, method: str) -> dict:
    """Return a standard UNKNOWN intent result."""
    return {
        "intent": INTENT_UNKNOWN,
        "confidence": 0.0,
        "filename": None,
        "language": None,
        "summary_target": None,
        "reasoning": reason,
        "method": method,
    }


def _extract_language(text: str) -> str:
    """Guess programming language from text."""
    lang_map = {
        "python": "python",
        "javascript": "javascript",
        "js": "javascript",
        "typescript": "typescript",
        "java": "java",
        "c++": "cpp",
        "cpp": "cpp",
        "rust": "rust",
        "go": "go",
        "bash": "bash",
        "shell": "bash",
        "html": "html",
        "css": "css",
        "sql": "sql",
    }
    for keyword, lang in lang_map.items():
        if keyword in text:
            return lang
    return "python"  # Default to Python


def _lang_to_ext(lang: str) -> str:
    """Map language name to file extension."""
    ext_map = {
        "python": "py",
        "javascript": "js",
        "typescript": "ts",
        "java": "java",
        "cpp": "cpp",
        "rust": "rs",
        "go": "go",
        "bash": "sh",
        "html": "html",
        "css": "css",
        "sql": "sql",
    }
    return ext_map.get(lang, "py")


def _extract_filename(text: str) -> str | None:
    """Try to extract an explicit filename from the user's command."""
    # Match patterns like: "called X.py", "named X.py", "file X.py", "save as X.py"
    patterns = [
        r'(?:called|named|as|file)\s+([\w\-]+\.\w+)',
        r'([\w\-]+\.(?:py|js|ts|java|cpp|go|rs|sh|txt|md|html|css|sql))',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None
