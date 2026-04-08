import streamlit as st
import requests
import re

# 1. Library Imports
try:
    import streamlit_mermaid as st_mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

# 2. Page Config
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

# Sync language across tabs
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# 3. Optimized AI Function (Grok)
def call_grok(prompt_type, user_text):
    api_key = st.secrets.get("GROK_API_KEY")
    if not api_key:
        return "Error: Configure GROK_API_KEY in Secrets."
    
    # Specific instructions based on what we are generating
    prompts = {
        "viz": f"Convert to raw Mermaid.js code. Use 'graph TD' for flowchart or 'mindmap'. No backticks. No talk. Language: {st.session_state.output_lang}. Text: {user_text[:1000]}",
        "notes": f"Summarize these notes into clean bullet points in {st.session_state.output_lang}: {user_text[:2000]}",
        "quiz": f"Create 3 multiple choice questions in {st.session_state.output_lang} based on: {user_text[:1500]}"
    }

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=15, # Prevents the "infinite loading" feel
            json={
                "model": "grok-beta",
                "messages": [{"role": "system", "content": "You are an AI study assistant. Output ONLY the requested content."},
                             {"role": "user", "content": prompts[prompt_type]}],
                "temperature": 0.2
            }
        )
        result = response.json()['choices'][0]['message']['content'].strip()
        # Remove any markdown code blocks that break the visualizer
        return re.sub(r'```mermaid|```', '', result).strip()
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# 4. Global Language UI
def show_lang_selector(key):
    langs = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    idx = langs.index(st.session_state.output_lang)
    st.session_state.output_lang = st.selectbox("Output Language", langs, index=idx, key=f"lang_{key}")

# --- APP LAYOUT ---
st.title("🧠 StudyAI")

tabs = st.tabs(["📝 Quiz Generator", "🗂️ Flashcards", "🎨 Concept Visualizer", "📄 Notes Generator"])

# --- TAB: QUIZ ---
with tabs[0]:
    st.header("Quiz Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        show_lang_selector("quiz")
        q_src = st.radio("Source", ["Text", "YouTube"], key="q_src")
    with c2:
        q_in = st.text_input("YouTube URL" if q_src == "YouTube" else "Paste Text", key="q_in")
        if st.button("Create Quiz ✍️"):
            with st.spinner("Generating..."):
                st.write(call_grok("quiz", q_in))

# --- TAB: FLASHCARDS ---
with tabs[1]:
    st.header("Flashcards")
    c1, c2 = st.columns([1, 2])
    with c1: show_lang_selector("fc")
    with c2:
        f_in = st.text_area("Paste content:", height=200, key="f_in")
        if st.button("Create Flashcards 🗂️"):
            st.info("Flashcard logic pending API connection...")

# --- TAB: CONCEPT VISUALIZER ---
with tabs[2]:
    st.header("Concept Visualizer")
    if not MERMAID_AVAILABLE:
        st.error("Add `streamlit-mermaid` to requirements.txt")
    else:
        c1, c2 = st.columns([1, 2])
        with c1:
            show_lang_selector("viz")
            v_style = st.radio("Style", ["Flowchart", "Mind Map"], key="v_style")
        with c2:
            v_txt = st.text_area("Paste text to visualize:", height=200, key="v_txt")
            if st.button("Generate Visual 🎨"):
                if v_txt:
                    with st.spinner("AI is drawing..."):
                        code = call_grok("viz", v_txt)
                        # Fix: check if code is actually Mermaid
                        if "graph" in code or "mindmap" in code:
                            st_mermaid.st_mermaid(code, height=500)
                        else:
                            st.error("AI returned text instead of code. Try again.")
                else:
                    st.warning("Please enter text.")

# --- TAB: NOTES ---
with tabs[3]:
    st.header("Notes Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        show_lang_selector("notes")
        n_src = st.radio("Source", ["Text", "YouTube"], key="n_src")
    with c2:
        n_in = st.text_area("Input Source", key="n_in", height=200)
        if st.button("Generate Notes 📄"):
            with st.spinner("Summarizing..."):
                st.markdown(call_grok("notes", n_in))
