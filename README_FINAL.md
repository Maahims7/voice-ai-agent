# 🎙️ Voice-Controlled Local AI Agent

> A production-grade voice AI agent that transcribes speech, detects intents, and executes actions—all running locally with no cloud dependencies.

**Status**: ⭐ Ready for internship submission | **Last Updated**: April 2026

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#-architecture)
- [Setup Instructions](#-setup-instructions)
- [Usage Guide](#-usage-guide)
- [Features](#-features)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)

---

## 🎯 Overview

**What it does:**
1. 🎤 Accepts audio input (microphone recording or file upload)
2. 🔊 Converts speech to text using OpenAI Whisper (local/offline)
3. 🧠 Detects user intent using Ollama LLM (llama3 model)
4. ⚙️ Executes corresponding actions:
   - **CREATE_FILE**: Create new text files
   - **WRITE_CODE**: Generate code in any language and save to file
   - **SUMMARIZE_TEXT**: Summarize large text into key points
   - **GENERAL_CHAT**: Answer questions and have conversations
5. 📊 Displays results in a beautiful Streamlit UI

**Why it's special:**
- ✅ 100% local execution (no data leaves your machine)
- ✅ Works offline (after models are downloaded)
- ✅ Beautiful production-grade UI with real-time feedback
- ✅ Session memory tracking
- ✅ Compound command support (bonus feature)
- ✅ Fallback mechanisms for reliability
- ✅ Proper error handling and validation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Web UI                   │
│            (Beautiful, responsive frontend)         │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────┐
        ▼            ▼            ▼          ▼
    ┌────────┐  ┌────────┐  ┌─────────┐  ┌─────┐
    │  STT   │  │ Intent │  │  Tools  │  │Utils│
    │(stt.py)│  │ClassV. │  │(tools.py)  │(utils│
    └────┬───┘  │(intent │  └────┬────┘  └─────┘
         │      │ .py)   │       │
    Whisper    └────┬───┘   Code Gen,
    or Groq        │      File Ops,
    API           LLM      Chat,
                  Call     Summary
                
    ┌─────────────────────────────────────────────┐
    │     Session Memory & Configuration          │
    │  (tracks interactions, manages state)        │
    └─────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────┐
    │         Output Folder (/output)             │
    │  (safe storage for generated files)         │
    └─────────────────────────────────────────────┘
```

### File Responsibilities

| File | Purpose | Key Functions |
|------|---------|---|
| `app.py` | Main Streamlit UI | Pipeline orchestration, UI rendering |
| `stt.py` | Speech-to-text conversion | Whisper integration, Groq API fallback |
| `intent.py` | Intent classification | LLM prompting, keyword fallback matching |
| `tools.py` | Action execution | File creation, code generation, chat, summarization |
| `utils.py` | Shared utilities | Logging, session memory, formatting, Ollama status |

---

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.10+** (3.13 recommended)
- **FFmpeg** (for audio processing)
- **Ollama** (for local LLM)
- **Git** (for cloning)

### Step 1: Install FFmpeg

**Windows:**
```bash
winget install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg portaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg portaudio19-dev
```

### Step 2: Install Ollama

Download from [https://ollama.com](https://ollama.com) and install.

Then pull the LLaMA 3 model:
```bash
ollama pull llama3
```

### Step 3: Clone & Setup Project

```bash
# Clone the repository
git clone https://github.com/yourusername/voice_agent.git
cd voice_agent

# Create a Python virtual environment
python3 -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Optional - Set Up Groq API (Fallback)

If you want cloud fallback for STT (when Whisper is unavailable):

1. Get a free API key from [https://console.groq.com](https://console.groq.com)
2. Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
3. The app will automatically use it if Whisper fails

---

## 💬 Usage Guide

### Running the Application

**Terminal 1 - Start Ollama server:**
```bash
ollama serve
```
Keep this running in the background. You should see output like:
```
binding 127.0.0.1:11434
...
Listening on [::]:11434
```

**Terminal 2 - Start the Streamlit app:**
```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

### Interface Overview

#### Left Panel (Controls)
- **System Status**: Shows if Ollama is running ✅
- **Settings**: Toggle API, select LLM model, confirmation mode
- **Session History**: All previous commands with timestamps
- **Output Files**: Download generated files

#### Right Panel (Pipeline)
Displays the full processing pipeline:
1. **Transcribed Input**: The converted speech-to-text
2. **Detected Intent**: What the AI understood you wanted to do
3. **Action Executed**: What was performed
4. **Final Output**: Results (files created, code generated, answers, etc.)

### Example Commands

**Create a File:**
```
"Create a new text file called my_notes.txt"
→ Creates /output/my_notes.txt
```

**Write Code:**
```
"Write a Python function to calculate fibonacci numbers and save it as fibonacci.py"
→ Generates code, saves to /output/fibonacci.py
```

**Summarize Text:**
```
"Summarize the following: Machine learning is a subset of artificial intelligence..."
→ Returns concise summary with key points
```

**General Chat:**
```
"What are the differences between supervised and unsupervised learning?"
→ Answers the question using the AI model
```

**Compound Command (Bonus):**
```
"Create a file, then write Python code to it, then summarize what we did"
→ Executes all three actions sequentially
```

---

## ✨ Features

### Core Features
- ✅ **Speech Recognition**: OpenAI Whisper (local, offline)
- ✅ **Intent Detection**: Ollama LLM with keyword fallback
- ✅ **Code Generation**: Any language, saved to `/output`
- ✅ **File Operations**: Safe creation restricted to `/output` folder
- ✅ **Text Summarization**: Extractive and abstractive modes
- ✅ **Chat Interface**: General Q&A with context

### Advanced Features
- ✅ **Session Memory**: Track all interactions with timestamps
- ✅ **Confidence Scoring**: See how confident the AI is about interpretations
- ✅ **API Fallback**: Use Groq's cloud Whisper if local model fails
- ✅ **Confirmation Dialogs**: Ask before file operations
- ✅ **Audio Validation**: Check file size, format, existence
- ✅ **Timeout Handling**: Prevent hanging on slow LLM responses
- 🎁 **Compound Commands**: Execute multiple intents in sequence (bonus)

### Security
- 🔒 Path traversal prevention (no files written outside `/output`)
- 🔒 Filename sanitization
- 🔒 No data sent to cloud (unless API fallback explicitly enabled)
- 🔒 Environment variables for sensitive keys

---

## 🔌 API Reference

### Speech-to-Text (`stt.py`)

```python
from stt import transcribe_audio

result = transcribe_audio(
    audio_path="path/to/audio.wav",
    use_api=False  # Set True to use Groq API fallback
)
# Returns: {"success": bool, "text": str, "method": str}
```

### Intent Classification (`intent.py`)

```python
from intent import classify_intent

result = classify_intent(
    text="Create a Python file",
    use_ollama=True  # Set False to use keyword fallback
)
# Returns: {
#   "intent": str,
#   "confidence": float,
#   "filename": str | None,
#   "language": str | None,
#   "reasoning": str,
#   "method": str
# }
```

### Tool Execution (`tools.py`)

```python
from tools import execute_action

result = execute_action(
    intent="WRITE_CODE",
    user_text="Write a hello world function",
    intent_data={...}
)
# Returns: {
#   "success": bool,
#   "action": str,
#   "result": str,
#   "filepath": str | None
# }
```

### Session Management (`utils.py`)

```python
from utils import SessionMemory

memory = SessionMemory(max_history=20)
memory.add(
    user_input="Create a file",
    intent="CREATE_FILE",
    action="File created",
    result="File successfully created",
    success=True
)
history = memory.get_history()
```

---

## 🐛 Troubleshooting

### Q: "❌ Ollama not running"

**Solution**: Start Ollama in a separate terminal:
```bash
ollama serve
```

### Q: "No speech detected in audio"

**Solution**: 
- Check audio quality and volume
- Try re-recording in a quieter environment
- Use audio file uploader instead of microphone

### Q: "Whisper not installed"

**Solution**: Install it manually:
```bash
pip install openai-whisper
# or with specific CUDA version:
pip install torch==2.1.2 torchaudio==2.1.2
pip install openai-whisper
```

### Q: Ollama keeps timing out

**Solution**:
- Run `ollama serve` again to restart
- Check `http://localhost:11434/api/tags` in your browser
- Try a smaller model: `ollama pull mistral`

### Q: App crashes with "Module not found"

**Solution**: Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### Q: Generated code is incomplete

**Solution**:
- Ollama model might be overloaded
- Try a more specific command
- Restart Ollama and try again

---

## 📁 Project Structure

```
voice_agent/
├── app.py                 # Main Streamlit application
├── stt.py                 # Speech-to-text module
├── intent.py              # Intent classification module
├── tools.py               # Tool execution (file, code, chat, summary)
├── utils.py               # Utility functions & shared helpers
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── output/                # Generated files (auto-created)
│   ├── example_code.py
│   ├── notes.txt
│   └──...
└── .env                   # Optional: API keys (create if using Groq)
```

---

## 🎓 How It Works - Internal Flow

### 1. Audio Input
```
User speaks → Microphone/File → Temporary WAV file
```

### 2. Transcription (STT)
```
Audio file → Whisper "base" model → Text transcription
           ↓ (if fails)
           → Groq API fallback → Text
```

### 3. Intent Classification
```
Text → System prompt → Ollama LLM → JSON response
                      ↓ (if fails)
                      → Keyword matching → Predefined intent
```

### 4. Tool Execution
```
Intent + Context → Route to appropriate tool:
  ├─ CREATE_FILE → Create /output/filename.ext
  ├─ WRITE_CODE → LLM generates code → Save to /output
  ├─ SUMMARIZE_TEXT → LLM creates summary → Display
  └─ GENERAL_CHAT → LLM responds → Display
```

### 5. Result Display
```
Results → Streamlit UI → User sees:
  - Transcribed text
  - Detected intent + confidence
  - Action taken + timing
  - Final output/file
```

---

## 📊 Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎙️ Voice-Controlled AI Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Transcribed Input
━━━━━━━━━━━━━━━━━━━━━━━━━
"Write a Python function to calculate fibonacci numbers"

Step 2: Detected Intent
━━━━━━━━━━━━━━━━━━━━━━━━━
💻 WRITE_CODE
Confidence: ████████░░ 92%
Method: ollama_llm
Reason: LLM detected code generation request

Step 3: Action Executed
━━━━━━━━━━━━━━━━━━━━━━━
Generated Python code → saved to fibonacci.py
Time: 2.34s

Step 4: Final Output
━━━━━━━━━━━━━━━━━━━
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

📁 Saved to: /output/fibonacci.py
```

---

## 🎬 Demo Scenarios

### Scenario 1: Code Generation
**User says**: "Write a JavaScript function to validate email addresses"

**Pipeline**:
1. STT: Converts speech to text
2. Intent: Detects WRITE_CODE + language=javascript
3. Tools: Generates email validation function
4. Output: Saves to `email_validator.js`

### Scenario 2: Compound Command
**User says**: "Create a file for my todo list, then write a Python script to parse it"

**Pipeline** (Bonus Feature):
1. STT: Transcribes both commands
2. Intent: Detects two separate intents
3. Tools: Executes both in sequence
4. Output: Creates file + generates parser code

---

## 🔐 Security & Privacy

- **No cloud uploads**: All data stays on your machine
- **Local LLM**: Ollama runs locally (no API calls unless explicitly configured)
- **Path safety**: Files can only be created in `/output`
- **Input validation**: All filenames sanitized for safety
- **Optional API**: Groq integration is opt-in via environment variable

---

## 📝 License

MIT License - Feel free to modify and distribute

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- More language models (Mistral, Phi, etc.)
- Additional tools (file reading, database operations)
- Enhanced UI features
- better audio preprocessing

---

## 👨‍💻 Author

Built as an internship-submission-ready project demonstrating:
- 🏆 Clean, modular Python architecture
- 🏆 Proper error handling & validation
- 🏆 Professional UI/UX design
- 🏆 Production-grade best practices
- 🏆 Advanced AI/ML integration

---

## 📞 Support

Having issues? Check:
1. [Troubleshooting](#troubleshooting) section above
2. Ollama is running: `curl http://localhost:11434/api/tags`
3. Python version: `python --version` (should be 3.10+)
4. Dependencies: `pip list | grep streamlit`

---

**Last updated**: April 2026 | **Status**: Production Ready ✅
