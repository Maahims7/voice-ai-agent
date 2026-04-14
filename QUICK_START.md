"""
QUICK START GUIDE - Voice-Controlled Local AI Agent
================================================

Get up and running in 5 minutes!
"""

# ==============================================================================
# STEP 1: PREREQUISITES (5 minutes)
# ==============================================================================

## Windows Users:
```powershell
# Install FFmpeg (required for audio)
winget install ffmpeg

# Install Ollama from: https://ollama.com
# Run installer and follow prompts
```

## Mac Users:
```bash
# Install FFmpeg and audio libraries
brew install ffmpeg portaudio

# Install Ollama from: https://ollama.com
# Run installer and follow prompts
```

## Linux Users:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg portaudio19-dev

# Fedora/RHEL
sudo yum install ffmpeg portaudio-devel

# Install Ollama from: https://ollama.com
```

# ==============================================================================
# STEP 2: DOWNLOAD THE MODEL (3 minutes)
# ==============================================================================

Open a terminal/PowerShell and run:

```bash
ollama pull llama3
```

This downloads the LLaMA 3 model (~4.7GB). You only do this once!

Expected output:
```
pulling manifest
pulling 8934d8725065... 100% |████████████████| 3.8 GB
pulling c3d6ae224ae4... 100% |████████████████| 31 MB
verifying sha256 digest
writing manifest
success
```

# ==============================================================================
# STEP 3: SETUP PROJECT (5 minutes)
# ==============================================================================

```bash
# Navigate to project directory
cd d:\voice_agent  # or your path

# Create virtual environment
python3 -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Expected: ~2 minutes download time

# ==============================================================================
# STEP 4: RUN EVERYTHING (Quick Start)
# ==============================================================================

### Quick Reference - Run Everything:

**You need TWO separate terminal windows open simultaneously.**

```bash
# In the project folder (d:\voice_agent), activate venv first:
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

Then open these in two different terminal windows:

**TERMINAL 1 - Ollama Server:**
```bash
ollama serve
```
Expected output:
```
time=2026-04-14T17:26:37 level=INFO msg="Listening on 127.0.0.1:11434"
```
✅ Ollama is ready at `http://localhost:11434`

**TERMINAL 2 - Streamlit App (from project directory with venv activated):**
```bash
streamlit run app.py
```
Expected output:
```
Local URL: http://localhost:8501
```
✅ Open http://localhost:8501 in your browser

### Full Step-by-Step:

**Step 1: Open PowerShell/Terminal #1**
```bash
cd d:\voice_agent
venv\Scripts\activate
ollama serve
```
→ Leave this running (you'll see Ollama startup messages)

**Step 2: Open PowerShell/Terminal #2** (new window)
```bash
cd d:\voice_agent
venv\Scripts\activate
streamlit run app.py
```
→ Your browser opens to http://localhost:8501 automatically

**Both terminals must stay running!** Ctrl+C in either one will stop that service.

# ==============================================================================
# STEP 5: TEST IT OUT (5 minutes)
# ==============================================================================

In the Streamlit app:

1. **Click the microphone icon** (top right of "Choose input method")
2. **Speak clearly**: "Write a Python function to calculate fibonacci numbers"
3. **Click "🎙️ Process Command"** button
4. **Watch the pipeline execute**:
   - Transcribed Input ✅
   - Detected Intent ✅
   - Action Executed ✅
   - Final Output ✅
5. **Check /output folder** for generated fibonacci.py file

You did it! 🎉

# ==============================================================================
# TROUBLESHOOTING
# ==============================================================================

### Error: "Ollama not running"
→ Make sure Terminal 1 is still running `ollama serve`
→ Check: Open browser to http://localhost:11434/api/tags
→ Should see your models listed

### Error: "Whisper not installed"
→ Run: `pip install openai-whisper torch torchaudio`

### Error: "Port 8501 already in use"
→ Use different port: `streamlit run app.py --server.port 8502`

### Audio won't record
→ Check microphone permissions (Settings → Privacy)
→ Try file upload instead of microphone recording

### App runs slow
→ First time uses large models (3-5GB downloads)
→ Subsequent runs are faster
→ Check internet connection

# ==============================================================================
# SAMPLE COMMANDS TO TRY
# ==============================================================================

**File Creation:**
"Create a todo list file"
→ /output/todo_list.txt created

**Code Generation:**
"Write JavaScript code to validate email addresses"
→ /output/validate_email.js created

**Summarization:**
"Summarize this: AI is transforming industries by automating tasks..."
→ Summary displayed with key points

**General Chat:**
"What's the difference between machine learning and deep learning?"
→ AI answers the question

**Compound (Advanced):**
"Create a file, then write Python code to parse JSON, then chat about what we did"
→ All three executed sequentially

# ==============================================================================
# ENVIRONMENT SETUP (OPTIONAL - FOR GROQ API FALLBACK)
# ==============================================================================

If you want cloud fallback for speech recognition:

1. Get free API key: https://console.groq.com
2. Create .env file in project root:

```
GROQ_API_KEY=gsk_your_key_here_from_console_groq_com
```

3. In the Streamlit app, toggle "Use Groq API for STT"

This is optional - the app works fine without it!

# ==============================================================================
# NEXT STEPS
# ==============================================================================

1. **Read the full README**: More details in README.md
2. **Watch the included VIDEO_SCRIPT.md**: For demo ideas
3. **Read TECH_ARTICLE.md**: Understand the architecture
4. **Explore the code**: Each file has detailed comments
5. **Try compound commands**: The bonus feature!
6. **Share it**: Show friends/colleagues what you built!

# ==============================================================================
# FILE DESCRIPTIONS
# ==============================================================================

app.py         - Streamlit web interface (user-facing)
stt.py         - Speech-to-text using Whisper or Groq
intent.py      - Intent classification using Ollama or keywords
tools.py       - Tool execution (file creation, code gen, etc.)
utils.py       - Helper functions and utilities
README.md      - Complete documentation
requirements.txt - Python dependencies list
/output        - Where generated files are saved

# ==============================================================================
# IMPORTANT NOTES
# ==============================================================================

✅ All runs LOCALLY - no data sent to cloud (unless Groq enabled)
✅ Works OFFLINE - after models are downloaded
✅ SECURE - files only created in /output folder
✅ FREE - $0 per use (except optional Groq API)
✅ CUSTOMIZABLE - modify prompts, models, tools

# ==============================================================================
# SUPPORT
# ==============================================================================

If stuck:
1. Check Troubleshooting section above
2. Read full README.md for detailed explanations
3. Check your internet connection
4. Ensure Ollama is running in Terminal 1
5. Try restarting both terminals

# ==============================================================================
# CONGRATULATIONS!
# ==============================================================================

You now have a production-grade AI agent running locally!

Next: Impress your interviewer with this project! 🚀

Questions? Check the README.md or inline code comments.

Good luck! ⭐
