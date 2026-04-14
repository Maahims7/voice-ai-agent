"""
VIDEO SCRIPT - Voice-Controlled Local AI Agent (2-3 minutes)

SPEAKER NOTES FOR YOU:

Use an engaging, conversational tone. Speak clearly.
Pause for 1-2 seconds between major sections.
Direct viewer attention to the screen when showing features.
"""

# ============================================================================
# SCRIPT - Total Duration: ~2:45 min
# ============================================================================

[0:00-0:15] OPENING (Energetic, fast-paced)
----------------------------------------
"Hey everyone! Imagine controlling a local AI agent purely with your voice.

No cloud uploads. No API costs. Everything runs on YOUR machine.

Today I'm showing you how I built an open-source Voice-Controlled AI Agent
that transcribes speech, understands intent, and executes actions—all offline.

Let's dive in!"

[0:15-0:40] PROBLEM STATEMENT (Conversational)
----------------------------------------------
"Existing voice assistants have problems:
- They send your voice data to the cloud ☁️ (privacy concerns)
- They cost money per API call 💸 (expensive at scale)
- They're slow with poor internet 🌐 (unreliable)
- They can't run locally 🔒 (requires internet)

So I built something better."

[0:40-1:10] PROJECT OVERVIEW & ARCHITECTURE (Show diagram/architecture)
---------------------------------------------------------------------
"Here's how it works in 5 steps:

*Point to screen*

1️⃣ **Microphone input** - Record your voice OR upload an audio file

2️⃣ **Speech-to-Text** - Convert speech to text using OpenAI's Whisper model
                        (runs entirely locally, no cloud)

3️⃣ **Intent Detection** - AI understands what you want using Ollama LLM
                         (local LLaMA 3 model, also offline)

4️⃣ **Tool Execution** - Actually perform the action:
                       - Create files
                       - Generate code in any language
                       - Summarize text
                       - Answer questions

5️⃣ **Beautiful UI** - See results in real-time with a professional Streamlit interface

The entire pipeline is modular, secure, and production-grade."

[1:10-1:50] LIVE DEMO (Show actual app)
--------------------------------------
"Let me show you it in action.

*Open browser showing app at localhost:8501*

Here's the Streamlit interface. On the left, I have my controls and session history.
On the right, the full pipeline.

Let me record a voice command:

*Click microphone icon*
*Speak clearly:* 'Write a Python function to calculate fibonacci numbers and save it'

*App processes*

Watch what happens:

✅ Step 1: **Transcribed Input** - My speech became text
'Write a Python function to calculate fibonacci numbers and save it'

✅ Step 2: **Intent Detection** - AI detected: WRITE_CODE (92% confidence)
         - Language: Python
         - Suggested filename: fibonacci.py

✅ Step 3: **Action Executed** - Generated the code using Ollama
         - Took 2.3 seconds

✅ Step 4: **Result** - Here's the generated Python code, and it's 
         been automatically saved to /output/fibonacci.py

*Show generated code on screen*

I can even download it directly from the UI.

That's the complete flow from voice to working code—all local, all fast!"

[1:50-2:20] KEY FEATURES (Slideshow or text overlay)
---------------------------------------------------
"Key features that make this production-ready:

🔒 **100% Local Execution** - No data leaves your machine unless you enable it

⚡ **Fallback Logic** - If Whisper fails, uses Groq API. If Ollama times out, uses keywords.

📝 **Session Memory** - Tracks all interactions with timestamps

🎯 **Multi-Intent Support** - Create files, write code, summarize, chat

✅ **Input Validation** - Audio format checks, file size limits, filename sanitization

🎁 **Bonus: Compound Commands** - Chain multiple actions together

Example: 'Create a file, then write code to it, then summarize what we did'
→ Executes all three actions sequentially!"

[2:20-2:45] TECHNICAL STACK & CLOSING (Show tech stack graphic)
-------------------------------------------------------------
"**Tech Stack:**

🐍 Python 3.10+ (Clean, modern code)
🎙️ OpenAI Whisper (Speech recognition)
🧠 Ollama + LLaMA 3 (Local LLM)
🌐 Streamlit (Beautiful UI)
🔐 Multiple safety checks (Path validation, input sanitization)

**Perfect for:**
- ✅ AI researchers
- ✅ Indie developers
- ✅ Privacy-conscious users
- ✅ Internship projects

**The code is fully modularized:**
- stt.py: Speech-to-text
- intent.py: Intent classification
- tools.py: Action execution
- utils.py: Shared helpers

All error-handled, well-documented, and beginner-friendly.

---

This project demonstrates cutting-edge AI skills:
⭐ LLM integration (Ollama, prompt engineering)
⭐ Production-grade architecture (error handling, security)
⭐ Real-world problem solving (offline-first, fallbacks)
⭐ Clean code practices (modular, well-commented)

If you're interested in building something similar, check out:
- Ollama: ollama.com (download local LLMs)
- Whisper: github.com/openai/whisper
- Streamlit: streamlit.io

**Thanks for watching! Don't forget to star the repo!** ⭐

Any questions? Let me know in the comments!"

[2:45] OUTRO
-----------
(Smile at camera)
"See you in the next one! Now go build something amazing. 🚀"

# ============================================================================
# SPEAKER TIPS FOR RECORDING
# ============================================================================

1. **Practice first**: Read through 2-3 times before recording
2. **Speak clearly**: Enunciate! No one understands mumbling
3. **Watch the demo closely**: Point out where things happen on screen
4. **Use enthusiasm**: This is cool stuff—let it show!
5. **Pause strategically**: Gives viewers time to process
6. **B-roll ideas**:
   - Code in VS Code
   - Ollama startup
   - Generation time metrics
   - File creation confirmation
7. **Thumbnail text**: "Local AI Voice Agent | Zero Cloud ☁️❌"
8. **Video tags**: voice-ai, ollama, whisper, streamlit, python, ai-agent, offline

# ============================================================================
# EXPECTED AUDIENCE REACTION
# ============================================================================

"Wait, this all runs locally? No cloud? How?! 😲"
→ Explain Ollama (local LLM) + Whisper (offline STT)

"Is it as good as ChatGPT?"
→ Not commercial-grade, but surprisingly capable for local

"Can I use this for production?"
→ Yes! With proper error handling and monitoring (which we have)

"How long to set up?"
→ ~10 minutes with Ollama pre-installed, ~30 min first time

# ============================================================================
# CALL TO ACTION (End of video)
# ============================================================================

"👉 GitHub: [your-repo-link]
👉 Try it in 3 steps:
   1. git clone [repo]
   2. pip install -r requirements.txt
   3. streamlit run app.py

Full setup guide in README!

Like & Subscribe for more AI projects! 🎬"
