"""
app.py - Voice-Controlled Local AI Agent
-----------------------------------------
Main Streamlit UI application.

Features:
  - Record audio via microphone OR upload an audio file
  - Transcribe speech to text using Whisper
  - Classify intent using Ollama LLM (with keyword fallback)
  - Execute actions (create file, write code, summarize, chat)
  - Display full pipeline results in a clean UI
  - Confirmation dialog before file operations
  - Session history / memory panel

Run:
    streamlit run app.py
"""

import os
import tempfile
import streamlit as st
from pathlib import Path

# Configure Streamlit page FIRST before any other st calls
st.set_page_config(
    page_title="Voice AI Agent",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import our modules
from stt import transcribe_audio, save_uploaded_audio
from intent import classify_intent
from tools import execute_action, list_output_files, OUTPUT_DIR
from utils import (
    SessionMemory,
    check_ollama_status,
    format_intent_badge,
    format_confidence_bar,
    get_intent_description,
    setup_logging,
    Timer,
)

# Setup logging
logger = setup_logging()

# ---------------------------------------------------------------------------
# Custom CSS for a cleaner, more professional look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ---- Global ---- */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* ---- Header ---- */
.main-header {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f2027 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(99, 179, 237, 0.2);
}
.main-header h1 {
    color: #63b3ed;
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
}
.main-header p {
    color: #a0aec0;
    margin: 0.25rem 0 0;
    font-size: 0.9rem;
}

/* ---- Pipeline Cards ---- */
.pipeline-card {
    background: #1a202c;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
.pipeline-card h4 {
    color: #63b3ed;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 0.5rem;
}
.pipeline-card .value {
    color: #e2e8f0;
    font-size: 1rem;
    font-family: 'JetBrains Mono', monospace;
}

/* ---- Intent Badge ---- */
.intent-badge {
    display: inline-block;
    background: linear-gradient(135deg, #2d3748, #1a202c);
    border: 1px solid #4a5568;
    border-radius: 8px;
    padding: 0.35rem 0.8rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: #68d391;
    font-family: 'JetBrains Mono', monospace;
}

/* ---- Status Indicators ---- */
.status-ok   { color: #68d391; }
.status-warn { color: #f6ad55; }
.status-err  { color: #fc8181; }

/* ---- Timeline entry ---- */
.history-entry {
    border-left: 3px solid #4a5568;
    padding: 0.5rem 0.75rem;
    margin-bottom: 0.5rem;
    background: #1a202c;
    border-radius: 0 8px 8px 0;
    font-size: 0.85rem;
}
.history-entry.success { border-color: #68d391; }
.history-entry.failed  { border-color: #fc8181; }

/* ---- Button overrides ---- */
div.stButton > button {
    background: linear-gradient(135deg, #2b6cb0, #1a365d);
    color: white;
    border: 1px solid #2b6cb0;
    border-radius: 10px;
    padding: 0.6rem 1.5rem;
    font-weight: 700;
    font-family: 'Syne', sans-serif;
    transition: all 0.2s ease;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #3182ce, #2b6cb0);
    border-color: #63b3ed;
    transform: translateY(-1px);
}

/* ---- Code block ---- */
.stCodeBlock { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization (FIXED: Persists across reruns)
# ---------------------------------------------------------------------------
if "memory" not in st.session_state:
    st.session_state.memory = SessionMemory(max_history=20)

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None  # For confirmation dialog

if "use_api_stt" not in st.session_state:
    st.session_state.use_api_stt = False

# ✅ Fix: Store pipeline outputs (prevents disappearing results)
if "pipeline_text" not in st.session_state:
    st.session_state.pipeline_text = None

if "pipeline_intent" not in st.session_state:
    st.session_state.pipeline_intent = None

if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

if "pipeline_action" not in st.session_state:
    st.session_state.pipeline_action = None

if "pipeline_method" not in st.session_state:
    st.session_state.pipeline_method = None

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🎙️ Voice-Controlled AI Agent</h1>
    <p>Speak a command → AI transcribes, understands intent, and executes actions locally</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar: Status + Settings + History
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ System Status")

    # Ollama status check
    ollama_status = check_ollama_status()
    if ollama_status["running"]:
        st.success(ollama_status["message"])
    else:
        st.warning(ollama_status["message"])
        st.caption("⚠️ Using fallback mode for intent detection and chat until Ollama is available.")

    st.divider()

    # Settings
    st.markdown("### 🔧 Settings")
    use_api_stt = st.toggle(
        "Use Groq API for STT",
        value=st.session_state.use_api_stt,
        help="Toggle ON to use Groq's cloud Whisper API instead of local model."
    )
    st.session_state.use_api_stt = use_api_stt

    if use_api_stt:
        groq_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get your free key at console.groq.com"
        )
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key

    ollama_model = st.selectbox(
        "Ollama Model",
        options=["llama3", "mistral", "phi3", "llama3.2", "codellama"],
        index=0,
        help="Select which local model to use. Must be pulled first."
    )
    os.environ["OLLAMA_MODEL"] = ollama_model

    # Confirmation toggle (bonus feature)
    require_confirm = st.toggle(
        "Confirm before file operations",
        value=True,
        help="Ask for confirmation before creating or writing files."
    )

    st.divider()

    # Session History
    st.markdown("### 📜 Session History")
    if len(st.session_state.memory) == 0:
        st.caption("No interactions yet.")
    else:
        for entry in reversed(st.session_state.memory.get_history()):
            icon = "✅" if entry["success"] else "❌"
            css_class = "success" if entry["success"] else "failed"
            st.markdown(
                f'<div class="history-entry {css_class}">'
                f'<b>{icon} [{entry["timestamp"]}]</b><br>'
                f'<span style="color:#a0aec0">{entry["input"][:60]}...</span><br>'
                f'<span style="color:#63b3ed;font-size:0.8rem">{entry["intent"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if st.button("🗑️ Clear History"):
            st.session_state.memory.clear()
            st.rerun()

    st.divider()

    # Output files panel
    st.markdown("### 📁 Output Files")
    output_files = list_output_files()
    if output_files:
        for fname in sorted(output_files):
            fpath = OUTPUT_DIR / fname
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                file_content = f.read()
            st.download_button(
                label=f"⬇️ {fname}",
                data=file_content,
                file_name=fname,
                mime="text/plain",
                key=f"dl_{fname}",
            )
    else:
        st.caption("No files generated yet.")

# ---------------------------------------------------------------------------
# Main Content: Two-column layout
# ---------------------------------------------------------------------------
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("## 🎤 Audio Input")

    input_method = st.radio(
        "Choose input method:",
        ["Upload audio file", "Record with microphone"],
        horizontal=True,
    )

    audio_path = None

    # --- File Upload ---
    if input_method == "Upload audio file":
        uploaded = st.file_uploader(
            "Upload audio (.wav, .mp3, .m4a, .ogg)",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            help="Upload a pre-recorded audio file to transcribe and process."
        )
        if uploaded:
            audio_path = save_uploaded_audio(uploaded)
            st.audio(uploaded, format=uploaded.type)
            st.success(f"✅ Uploaded: {uploaded.name}")

    # --- Microphone Input ---
    else:
        st.info("💡 Use the audio recorder below. Click the microphone to start recording.")
        audio_bytes = st.audio_input("Click to record your voice command")
        if audio_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes.read())
                audio_path = tmp.name
            st.success("✅ Audio captured! Click 'Process Command' below.")

    # --- Sample Prompts ---
    st.markdown("### 💡 Sample Prompts")
    sample_prompts = {
        "📁 Create file": "Create a new text file called notes.txt",
        "💻 Write Python": "Write a Python function to calculate fibonacci numbers and save it",
        "📝 Summarize": "Summarize the following: Machine learning is a branch of AI that enables systems to learn from data",
        "💬 Chat": "What is the difference between supervised and unsupervised learning?",
    }

    for label, prompt in sample_prompts.items():
        if st.button(label, key=f"sample_{label}", use_container_width=True):
            st.session_state.pending_action = {
                "text": prompt,
                "source": "sample_prompt",
                "from_audio": False,
            }
            st.rerun()

    # --- Text fallback input ---
    st.markdown("### ✏️ Or type a command")
    text_input = st.text_area(
        "Type your command:",
        placeholder="e.g. Write a Python script for sorting a list",
        height=80,
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        process_text = st.button("▶️ Process Text", use_container_width=True)
    with col_btn2:
        process_audio = st.button(
            "🎙️ Process Command",
            use_container_width=True,
            disabled=(audio_path is None),
        )

    # Trigger processing
    if process_audio and audio_path:
        with st.spinner("🔊 Transcribing audio..."):
            with Timer("STT") as t_stt:
                stt_result = transcribe_audio(audio_path, use_api=st.session_state.use_api_stt)

        if stt_result["success"]:
            st.session_state.pending_action = {
                "text": stt_result["text"],
                "source": f"audio ({stt_result['method']})",
                "from_audio": True,
                "stt_method": stt_result["method"],
                "stt_time": t_stt.elapsed,
            }
            st.rerun()
        else:
            st.error(f"❌ Transcription failed: {stt_result['text']}")

    if process_text and text_input.strip():
        st.session_state.pending_action = {
            "text": text_input.strip(),
            "source": "text input",
            "from_audio": False,
        }
        st.rerun()


# ---------------------------------------------------------------------------
# Output Column: Pipeline Results
# ---------------------------------------------------------------------------
with col_output:
    st.markdown("## 🔄 Pipeline Results")

    # Process pending action
    if st.session_state.pending_action:
        action_data = st.session_state.pending_action
        user_text = action_data["text"]

        # Step 1: Show transcribed text
        st.markdown("#### Step 1: Transcribed Input")
        st.markdown(
            f'<div class="pipeline-card">'
            f'<h4>🎙️ Transcribed Text</h4>'
            f'<div class="value">{user_text}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        if action_data.get("from_audio"):
            st.caption(f"STT Method: {action_data.get('stt_method', 'unknown')} | Time: {action_data.get('stt_time', 0):.2f}s")

        # Step 2: Classify Intent
        with st.spinner("🧠 Classifying intent..."):
            with Timer("Intent") as t_intent:
                intent_result = classify_intent(user_text, use_ollama=ollama_status["running"])

        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        badge = format_intent_badge(intent)
        conf_bar = format_confidence_bar(confidence)

        st.markdown("#### Step 2: Detected Intent")
        st.markdown(
            f'<div class="pipeline-card">'
            f'<h4>🎯 Intent Classification</h4>'
            f'<div class="value">{badge} <span class="intent-badge">{intent}</span></div>'
            f'<div style="color:#a0aec0;font-size:0.85rem;margin-top:0.5rem">'
            f'Confidence: {conf_bar}<br>'
            f'Method: {intent_result["method"]}<br>'
            f'Reason: {intent_result["reasoning"]}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Extra details from intent
        if intent_result.get("filename"):
            st.caption(f"📄 Suggested filename: `{intent_result['filename']}`")
        if intent_result.get("language"):
            st.caption(f"💻 Detected language: `{intent_result['language']}`")

        # Step 3: Confirmation Dialog (Bonus Feature)
        is_file_action = intent in ("CREATE_FILE", "WRITE_CODE")
        confirmed = True  # Default: proceed

        if require_confirm and is_file_action and "confirmed" not in action_data:
            st.markdown("#### Step 3: Confirm Action")
            st.warning(
                f"⚠️ This will **{get_intent_description(intent)}**.\n\n"
                f"Filename: `{intent_result.get('filename', 'auto-generated')}`\n\n"
                f"All files are saved to: `output/`"
            )
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Confirm & Execute", use_container_width=True):
                    action_data["confirmed"] = True
                    st.rerun()
            with col_no:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.pending_action = None
                    st.info("Action cancelled.")
                    st.stop()
            st.stop()  # Wait for confirmation

        # Step 4: Execute Action
        st.markdown("#### Step 3: Action Executed")
        with st.spinner(f"⚙️ Executing: {get_intent_description(intent)}..."):
            with Timer("Execution") as t_exec:
                result = execute_action(intent, user_text, intent_result)

        st.session_state.last_result = result

        # Save to session memory
        st.session_state.memory.add(
            user_input=user_text,
            intent=intent,
            action=result["action"],
            result=result["result"],
            success=result["success"],
        )

        # Display action taken
        action_color = "#68d391" if result["success"] else "#fc8181"
        st.markdown(
            f'<div class="pipeline-card">'
            f'<h4>⚙️ Action Taken</h4>'
            f'<div class="value" style="color:{action_color}">{result["action"]}</div>'
            f'<div style="color:#718096;font-size:0.8rem;margin-top:0.25rem">'
            f'Time: {t_exec.elapsed:.2f}s'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        if result.get("filepath"):
            st.success(f"📁 Saved to: `{result['filepath']}`")

        # Step 5: Final Result
        st.markdown("#### Step 4: Final Output")
        st.markdown(result["result"])

        # ✅ FIX: STORE results in session state BEFORE clearing pending_action
        st.session_state.pipeline_text = user_text
        st.session_state.pipeline_intent = intent
        st.session_state.pipeline_result = result
        st.session_state.pipeline_action = result["action"]
        st.session_state.pipeline_method = intent_result["method"]

        # Clear pending action (but results stay in session state!)
        st.session_state.pending_action = None

        # Refresh output file list
        st.rerun()

    # ✅ FIX: Display stored results (even after rerun - PERSISTS!)
    elif st.session_state.pipeline_text is not None:
        st.markdown("#### Step 1: Transcribed Input")
        st.markdown(
            f'<div class="pipeline-card">'
            f'<h4>🎙️ Transcribed Text</h4>'
            f'<div class="value">{st.session_state.pipeline_text}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("#### Step 2: Detected Intent")
        st.markdown(
            f'<div class="pipeline-card">'
            f'<h4>🎯 Intent: {st.session_state.pipeline_intent}</h4>'
            f'<div class="value">Method: {st.session_state.pipeline_method}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("#### Step 3: Action Executed")
        st.markdown(
            f'<div class="pipeline-card">'
            f'<h4>⚙️ {st.session_state.pipeline_action}</h4>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("#### Step 4: Final Output")
        st.markdown(st.session_state.pipeline_result["result"])

        # Add Clear button
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.pipeline_text = None
            st.session_state.pipeline_intent = None
            st.session_state.pipeline_result = None
            st.session_state.pipeline_action = None
            st.session_state.pipeline_method = None
            st.rerun()

    elif st.session_state.last_result is None:
        # Empty state
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#4a5568;border:2px dashed #2d3748;border-radius:16px;margin-top:2rem">
            <div style="font-size:3rem">🎙️</div>
            <h3 style="color:#718096;margin:1rem 0 0.5rem">Ready for your command</h3>
            <p style="font-size:0.9rem">Upload audio, record your voice, or type a command<br>then click <b>Process</b> to see the pipeline in action.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Pipeline Diagram (bottom section)
# ---------------------------------------------------------------------------
st.divider()
st.markdown("### 🔁 How It Works")

pipe_cols = st.columns(5)
steps = [
    ("🎤", "Audio Input", "Microphone or file upload"),
    ("🔊", "Speech → Text", "OpenAI Whisper (local)"),
    ("🧠", "Intent Analysis", "Ollama LLM (llama3)"),
    ("⚙️", "Tool Execution", "File ops, code gen, chat"),
    ("📊", "Results Display", "Clean Streamlit UI"),
]
for col, (icon, title, desc) in zip(pipe_cols, steps):
    with col:
        st.markdown(
            f'<div style="text-align:center;padding:1rem;background:#1a202c;border-radius:12px;border:1px solid #2d3748">'
            f'<div style="font-size:1.75rem">{icon}</div>'
            f'<div style="color:#63b3ed;font-weight:700;font-size:0.85rem;margin:0.4rem 0 0.2rem">{title}</div>'
            f'<div style="color:#718096;font-size:0.75rem">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
