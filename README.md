# 🎙️ Voice-Controlled Local AI Agent

> A production-ready voice assistant that transcribes speech, understands intent, and executes local actions — all running on your machine.

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Setup Instructions](#setup-instructions)
6. [Running the App](#running-the-app)
7. [How to Use](#how-to-use)
8. [Example Inputs & Outputs](#example-inputs--outputs)
9. [Hardware Notes & Fallbacks](#hardware-notes--fallbacks)
10. [Bonus Features Implemented](#bonus-features-implemented)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This project is a **fully local, voice-controlled AI agent** built for the AI/ML & Generative AI Development assignment. It demonstrates a complete end-to-end pipeline:

```
Audio Input → Speech-to-Text → Intent Classification → Tool Execution → Results UI
```

Key capabilities:
- 🎤 Accept audio via **microphone recording** or **file upload**
- 🔊 Transcribe audio with **OpenAI Whisper** (local, offline)
- 🧠 Classify intent using **Ollama + LLaMA3** (fully local LLM)
- ⚙️ Execute actions: create files, write code, summarize text, or chat
- 🔒 **Safety-first**: all file operations are sandboxed to the `output/` folder
- 💬 Session memory maintains history across interactions
- ✅ Optional confirmation dialog before file/code creation

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (app.py)                     │
│  ┌──────────────┐              ┌──────────────────────────┐  │
│  │  Audio Input │              │     Results Display       │  │
│  │  (mic/file)  │              │  • Transcription         │  │
│  └──────┬───────┘              │  • Intent + Confidence   │  │
│         │                     │  • Action Taken          │  │
│         ▼                     │  • Final Output          │  │
│  ┌──────────────┐              └──────────────────────────┘  │
│  │   stt.py     │                                            │
│  │  (Whisper)   │◄── .wav/.mp3/.m4a                         │
│  └──────┬───────┘                                            │
│         │ Transcribed Text                                   │
│         ▼                                                    │
│  ┌──────────────┐                                            │
│  │  intent.py   │◄── Ollama (llama3) or keyword fallback    │
│  │ (LLM / rules)│                                            │
│  └──────┬───────┘                                            │
│         │ Intent + Metadata                                  │
│         ▼                                                    │
│  ┌──────────────────────────────────┐                        │
│  │           tools.py               │                        │
│  │  ┌──────────┐  ┌──────────────┐  │                        │
│  │  │create_   │  │write_code_   │  │                        │
│  │  │file()    │  │to_file()     │  │                        │
│  │  └──────────┘  └──────────────┘  │                        │
│  │  ┌──────────┐  ┌──────────────┐  │                        │
│  │  │summarize_│  │general_      │  │                        │
│  │  │text()    │  │chat()        │  │                        │
│  │  └──────────┘  └──────────────┘  │                        │
│  └──────────────────────────────────┘                        │
│         │ All files → output/ folder only                   │
│  ┌──────────────┐                                            │
│  │   utils.py   │◄── Session memory, logging, formatting    │
│  └──────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline Flow:
1. **Audio Input**: User uploads a file or records via microphone
2. **STT (stt.py)**: Whisper model converts audio → text
3. **Intent (intent.py)**: Ollama LLM analyzes text and returns structured intent JSON
4. **Tools (tools.py)**: Appropriate tool is called based on intent
5. **UI (app.py)**: Results displayed in a clean, step-by-step Streamlit interface

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Streamlit | Web interface |
| STT (local) | OpenAI Whisper | Audio → text (offline) |
| STT (fallback) | Groq API | Cloud transcription fallback |
| LLM | Ollama + LLaMA3 | Intent classification + code generation |
| File Ops | Python stdlib | Create/write files safely |
| Backend | Python 3.10+ | All processing logic |

---

## Project Structure

```
voice_agent/
├── app.py              # 🖥️  Streamlit UI — main entry point
├── stt.py              # 🔊  Speech-to-Text (Whisper + Groq fallback)
├── intent.py           # 🧠  Intent classification (Ollama + keywords)
├── tools.py            # ⚙️  Tool execution (file, code, summarize, chat)
├── utils.py            # 🛠️  Utilities (memory, logging, formatting)
├── requirements.txt    # 📦  Python dependencies
├── .env.example        # 🔐  Environment variable template
├── README.md           # 📖  This file
└── output/             # 📁  All generated files are saved here (safe)
    └── .gitkeep
```

---

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd voice_agent
```

### Step 2: Create a Virtual Environment
```bash
python -m venv venv

# Activate it:
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ Whisper requires `ffmpeg`. Install it first:
> - **macOS**: `brew install ffmpeg`
> - **Ubuntu**: `sudo apt install ffmpeg`
> - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org) or `winget install ffmpeg`

### Step 4: Install Ollama (Local LLM)

1. Download from [ollama.com](https://ollama.com)
2. Pull the LLaMA3 model:
   ```bash
   ollama pull llama3
   ```
3. Start the Ollama server (keep this running):
   ```bash
   ollama serve
   ```

### Step 5: Set Up Environment Variables (Optional)
```bash
cp .env.example .env
# Edit .env with your settings if needed
```

---

## Running the App

```bash
# Make sure Ollama is running first:
ollama serve

# In a new terminal, start the app:
streamlit run app.py
```

The app opens at: **http://localhost:8501**

---

## How to Use

### Method 1: Upload an Audio File
1. Select **"Upload audio file"**
2. Upload a `.wav`, `.mp3`, or `.m4a` file
3. Click **"🎙️ Process Command"**
4. Watch the pipeline: transcription → intent → action → result

### Method 2: Record with Microphone
1. Select **"Record with microphone"**
2. Click the microphone icon and speak your command
3. Click **"🎙️ Process Command"**

### Method 3: Type a Command (Text Fallback)
1. Type in the text area at the bottom of the input panel
2. Click **"▶️ Process Text"**

### Method 4: Use Sample Prompts
Click any of the quick-start sample prompt buttons to test instantly.

---

## Example Inputs & Outputs

### 1. Create File
**Input**: *"Create a new text file called meeting_notes.txt"*

**Pipeline**:
- Intent: `CREATE_FILE` (confidence: 90%)
- Action: Create file → `output/meeting_notes.txt`
- Output: `✅ File 'meeting_notes.txt' was successfully created`

---

### 2. Write Code
**Input**: *"Write a Python function to calculate fibonacci numbers and save it"*

**Pipeline**:
- Intent: `WRITE_CODE` (confidence: 95%)
- Language: Python
- Action: LLM generates code → saved to `output/fibonacci.py`
- Output: Full Python code displayed + file saved

---

### 3. Summarize Text
**Input**: *"Summarize: Machine learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed..."*

**Pipeline**:
- Intent: `SUMMARIZE_TEXT` (confidence: 92%)
- Action: Ollama LLM generates bullet-point summary
- Output: Key points displayed in UI

---

### 4. General Chat
**Input**: *"What is the difference between supervised and unsupervised learning?"*

**Pipeline**:
- Intent: `GENERAL_CHAT` (confidence: 85%)
- Action: Ollama LLM generates response
- Output: Conversational AI response displayed

---

## Hardware Notes & Fallbacks

### Local Whisper Model
- **Default**: `whisper-base` model (~74M params) — fast on CPU
- **Better accuracy**: Change to `whisper-small` or `whisper-medium` in `stt.py` (line 42)
- Runs entirely offline after first download

### Groq API Fallback (for slow hardware)
If your machine struggles with local Whisper:
1. Toggle **"Use Groq API for STT"** in the sidebar
2. Enter your free Groq API key (get it at [console.groq.com](https://console.groq.com))
3. The system uses `whisper-large-v3` via Groq's fast inference

### Ollama Fallback
If Ollama is not running:
- Intent classification falls back to **keyword-based matching** (rule-based)
- Code generation uses **template-based fallback** code
- A warning is shown in the sidebar

---

## Bonus Features Implemented

| Feature | Status | Details |
|---------|--------|---------|
| ✅ Confirmation dialog | Implemented | Toggle in sidebar; prompts before file ops |
| ✅ Compound intent detection | Implemented | LLM extracts filename + language in one pass |
| ✅ Session memory | Implemented | Full history panel in sidebar |
| ✅ Graceful degradation | Implemented | Keyword fallback when Ollama is down |
| ✅ Error handling | Implemented | Invalid audio, unknown intent, API failures |
| ✅ Download generated files | Implemented | Download buttons in sidebar Output Files |

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `Ollama not running` | Run `ollama serve` in a terminal |
| `Model not found` | Run `ollama pull llama3` |
| `ffmpeg not found` | Install ffmpeg (see setup Step 3) |
| `Whisper slow` | Switch to Groq API STT in settings |
| `No audio recorded` | Check browser microphone permissions |
| `File not created` | Check write permissions on `output/` folder |
| `GROQ_API_KEY error` | Enter your key in the sidebar settings |

---

## Architecture Decisions

1. **Local-first**: Whisper + Ollama run entirely offline — no data leaves your machine
2. **Modular**: Each module (stt, intent, tools, utils) is independently testable
3. **Safe**: Path sanitization prevents any file operations outside `output/`
4. **Resilient**: Every component has a fallback when the primary method fails
5. **Beginner-friendly**: Every function has clear docstrings and inline comments

---

*Built with ❤️ for the AI/ML & Generative AI Development Internship Assignment*
