"""
tools.py - Tool Execution Module
----------------------------------
Executes actions based on the detected intent:
  1. CREATE_FILE      → Create a new empty (or text) file in /output
  2. WRITE_CODE       → Generate code with Ollama LLM and save to /output
  3. SUMMARIZE_TEXT   → Summarize content using Ollama LLM
  4. GENERAL_CHAT     → Respond to general questions using Ollama LLM

SAFETY: All file operations are restricted to the /output folder only.
        No files can be written outside this boundary.
"""

import os
import re
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Safety: ALL files must be created inside this folder
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)  # Create if it doesn't exist


# ---------------------------------------------------------------------------
# Public API — called by app.py based on intent
# ---------------------------------------------------------------------------

def execute_action(intent: str, user_text: str, intent_data: dict) -> dict:
    """
    Route execution to the appropriate tool based on detected intent.

    Args:
        intent (str): The detected intent constant (e.g., "WRITE_CODE")
        user_text (str): Original transcribed text from the user
        intent_data (dict): Full intent classification result (from intent.py)

    Returns:
        dict: {
            "success": bool,
            "action": str,
            "result": str,
            "filepath": str | None
        }
    """
    from intent import (
        INTENT_CREATE_FILE, INTENT_WRITE_CODE,
        INTENT_SUMMARIZE, INTENT_GENERAL_CHAT
    )

    if intent == INTENT_CREATE_FILE:
        return create_file(intent_data.get("filename") or "new_file.txt", user_text)

    elif intent == INTENT_WRITE_CODE:
        return write_code_to_file(
            user_text,
            filename=intent_data.get("filename"),
            language=intent_data.get("language", "python"),
        )

    elif intent == INTENT_SUMMARIZE:
        return summarize_text(user_text)

    elif intent == INTENT_GENERAL_CHAT:
        return general_chat(user_text)

    else:
        return {
            "success": False,
            "action": "No action taken",
            "result": f"Unknown intent '{intent}'. Please try again with a clearer command.",
            "filepath": None,
        }


# ---------------------------------------------------------------------------
# Tool 1: Create File
# ---------------------------------------------------------------------------

def create_file(filename: str, content: str = "") -> dict:
    """
    Create a new file inside the output/ directory.

    Args:
        filename (str): Name of the file to create (e.g., "notes.txt")
        content (str): Optional initial content for the file

    Returns:
        dict: Result with filepath and status
    """
    # Sanitize filename: strip directory traversal attempts
    safe_name = _sanitize_filename(filename)
    filepath = OUTPUT_DIR / safe_name

    try:
        # If content looks like a plain "create file" command,
        # just create an empty file or with a minimal header
        file_content = content if len(content) < 200 else ""

        filepath.write_text(file_content, encoding="utf-8")
        logger.info(f"Created file: {filepath}")

        return {
            "success": True,
            "action": f"Created file: {safe_name}",
            "result": f"✅ File '{safe_name}' was successfully created in the output folder.\n\nPath: {filepath}",
            "filepath": str(filepath),
        }

    except Exception as e:
        logger.error(f"File creation failed: {e}")
        return {
            "success": False,
            "action": "File creation failed",
            "result": f"❌ Could not create file: {str(e)}",
            "filepath": None,
        }


# ---------------------------------------------------------------------------
# Tool 2: Write Code to File
# ---------------------------------------------------------------------------

def write_code_to_file(user_text: str, filename: str = None, language: str = "python") -> dict:
    """
    Generate code using Ollama LLM and save it to a file in output/.

    Args:
        user_text (str): The user's code generation request
        filename (str): Suggested filename (optional, auto-generated if None)
        language (str): Programming language for code generation

    Returns:
        dict: Result with generated code and filepath
    """
    # Step 1: Generate code using LLM
    code_result = _generate_code_with_llm(user_text, language)

    if not code_result["success"]:
        return {
            "success": False,
            "action": "Code generation failed",
            "result": code_result["error"],
            "filepath": None,
        }

    generated_code = code_result["code"]

    # Step 2: Determine filename
    ext_map = {
        "python": "py", "javascript": "js", "typescript": "ts",
        "java": "java", "cpp": "cpp", "go": "go", "rust": "rs",
        "bash": "sh", "html": "html", "css": "css", "sql": "sql",
    }
    ext = ext_map.get(language, "py")

    if not filename:
        filename = _derive_filename_from_text(user_text) + f".{ext}"
    safe_name = _sanitize_filename(filename)

    # Ensure correct extension
    if not safe_name.endswith(f".{ext}") and "." not in safe_name:
        safe_name = f"{safe_name}.{ext}"

    filepath = OUTPUT_DIR / safe_name

    # Step 3: Save code to file
    try:
        filepath.write_text(generated_code, encoding="utf-8")
        logger.info(f"Code written to: {filepath}")

        return {
            "success": True,
            "action": f"Generated {language} code → saved to {safe_name}",
            "result": f"✅ Code saved to '{safe_name}'\n\n```{language}\n{generated_code}\n```",
            "filepath": str(filepath),
        }

    except Exception as e:
        return {
            "success": False,
            "action": "Failed to save code",
            "result": f"❌ Code generated but could not save: {str(e)}\n\n```{language}\n{generated_code}\n```",
            "filepath": None,
        }


# ---------------------------------------------------------------------------
# Tool 3: Summarize Text
# ---------------------------------------------------------------------------

def summarize_text(user_text: str) -> dict:
    """
    Summarize the provided text using Ollama LLM.

    Args:
        user_text (str): Text to summarize (may be long)

    Returns:
        dict: Summary result
    """
    summary = _call_ollama(
        prompt=f"Please provide a clear and concise summary of the following text. "
               f"Highlight the key points in 3-5 bullet points:\n\n{user_text}",
        system="You are a helpful text summarization assistant. Be concise and clear."
    )

    if summary:
        return {
            "success": True,
            "action": "Text summarized",
            "result": f"📝 **Summary:**\n\n{summary}",
            "filepath": None,
        }
    else:
        # Simple extractive fallback if Ollama is unavailable
        sentences = user_text.split(". ")
        brief = ". ".join(sentences[:3]) + "..." if len(sentences) > 3 else user_text
        return {
            "success": True,
            "action": "Text summarized (basic)",
            "result": f"📝 **Brief Summary (offline mode):**\n\n{brief}",
            "filepath": None,
        }


# ---------------------------------------------------------------------------
# Tool 4: General Chat
# ---------------------------------------------------------------------------

def general_chat(user_text: str) -> dict:
    """
    Respond to a general conversation query using Ollama LLM.

    Args:
        user_text (str): The user's question or statement

    Returns:
        dict: Chat response
    """
    response = _call_ollama(
        prompt=user_text,
        system=(
            "You are a helpful AI assistant built into a voice-controlled local agent. "
            "Be friendly, concise, and helpful. If asked about your capabilities, "
            "mention you can create files, write code, summarize text, and have general conversations."
        )
    )

    if response:
        return {
            "success": True,
            "action": "General chat response",
            "result": f"💬 {response}",
            "filepath": None,
        }

    # Fallback response when Ollama is unavailable
    return {
        "success": True,
        "action": "General chat response (fallback)",
        "result": (
            "⚠️ I couldn't reach the local LLM right now, but I can still help with basic guidance. "
            "Please try again in a moment or use a different command."
        ),
        "filepath": None,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _call_ollama(prompt: str, system: str = "") -> str | None:
    """
    Make a request to the local Ollama API.

    Args:
        prompt (str): The user prompt
        system (str): Optional system message

    Returns:
        str | None: Model response text, or None on failure
    """
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "llama3")

    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
            },
            timeout=(10, 180),  # connect/read timeout for slower local model inference
        )

        if response.status_code == 200:
            response_payload = response.json()
            response_text = response_payload.get("response", "")
            if isinstance(response_text, str):
                return response_text.strip()
            return str(response_text).strip()

        # Log non-200 responses for debugging
        logger.warning(
            f"Ollama API returned {response.status_code}: {response.text[:500]}"
        )
    except requests.exceptions.Timeout:
        logger.warning("Ollama request timed out.")
    except requests.exceptions.ConnectionError:
        logger.warning("Ollama not reachable. Start with: ollama serve")
    except Exception as e:
        logger.error(f"Ollama call error: {e}")

    return None


def _generate_code_with_llm(user_text: str, language: str = "python") -> dict:
    """
    Generate code from natural language description using Ollama.
    Returns only the code block, no extra explanation.
    """
    prompt = (
        f"Write clean, well-commented {language} code for the following request:\n\n"
        f"{user_text}\n\n"
        f"Return ONLY the code. Do NOT include markdown backticks, explanations, "
        f"or any text outside the code itself."
    )

    system = (
        f"You are an expert {language} developer. "
        f"When asked to write code, output ONLY the raw code with comments. "
        f"No markdown formatting, no explanations outside code comments."
    )

    code = _call_ollama(prompt=prompt, system=system)

    if code:
        # Strip any accidental markdown code fences
        code = re.sub(r"```[\w]*\n?", "", code).strip()
        return {"success": True, "code": code}
    else:
        # Minimal fallback code template when Ollama is offline
        fallback = _generate_fallback_code(user_text, language)
        return {"success": True, "code": fallback}


def _generate_fallback_code(description: str, language: str) -> str:
    """Generate a minimal placeholder code file when LLM is unavailable."""
    templates = {
        "python": f'# Generated by Voice AI Agent\n# Request: {description}\n\ndef main():\n    # TODO: Implement logic here\n    print("Hello from generated code!")\n\nif __name__ == "__main__":\n    main()\n',
        "javascript": f'// Generated by Voice AI Agent\n// Request: {description}\n\nfunction main() {{\n  // TODO: Implement logic here\n  console.log("Hello from generated code!");\n}}\n\nmain();\n',
        "html": f'<!DOCTYPE html>\n<html>\n<head><title>Generated Page</title></head>\n<body>\n  <!-- Request: {description} -->\n  <h1>Hello World</h1>\n</body>\n</html>\n',
    }
    return templates.get(language, templates["python"])


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and invalid characters.
    SAFETY CRITICAL: Ensures no files are written outside /output.
    """
    # Remove any directory separators — this prevents path traversal attacks
    name = os.path.basename(filename)
    # Replace spaces and special chars with underscores
    name = re.sub(r'[^\w\.\-]', '_', name)
    # Remove leading dots to prevent hidden files
    name = name.lstrip('.')
    # Ensure it has a name
    return name if name else "output_file.txt"


def _derive_filename_from_text(text: str) -> str:
    """Generate a short snake_case filename from the user's request."""
    # Extract key nouns/verbs (simple approach)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    # Skip common filler words
    stopwords = {"create", "write", "make", "generate", "build", "with", "for",
                 "the", "and", "that", "this", "file", "code", "please", "can",
                 "you", "using", "function", "class", "python", "javascript"}
    keywords = [w for w in words if w not in stopwords][:3]
    return "_".join(keywords) if keywords else "generated_code"


def list_output_files() -> list[str]:
    """Return a list of files currently in the output/ directory."""
    try:
        return [f.name for f in OUTPUT_DIR.iterdir() if f.is_file()]
    except Exception:
        return []
