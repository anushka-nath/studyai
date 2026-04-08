import streamlit as st
import os
import requests
import json

# Safe import for the visualization library
try:
    import streamlit_mermaid as st_mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

# --- 1. PAGE CONFIG & SESSION STATE ---
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# --- 2. AI LOGIC (GROK API) ---
def call_grok_for_mermaid(user_text, viz_type, lang):
    """Calls Grok API to convert text into Mermaid syntax."""
    api_key = st.secrets.get("GROK_API_KEY")
    if not api_key:
        return "error: API Key not found in Secrets."
    
    # Prompt to force the AI to return ONLY the Mermaid code
    prompt = f"""
    Convert the following text into a {viz_type} using Mermaid.js syntax.
    Language: {lang}.
    Rules:
    1. If Flowchart, use 'graph TD'.
    2. If Mind Map, use 'mindmap'.
    3. Return ONLY the code. No explanation, no markdown backticks.
    
    Text: {user_text[:2000]}
    """
    
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "grok-beta", # or your specific grok model
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0
            }
        )
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"graph TD; Error[Error calling AI: {str(e)}]"

# --- 3. SHARED UI HELPERS ---
def language_ui(key_suffix):
    languages = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    index = languages.index(st.session_state.output_lang)
    new_lang = st.selectbox("Output Language", languages, index=index, key=f"lang_{key_suffix}")
    st.session_state.output_lang = new_lang

# --- 4. APP HEADER ---
st.title("🧠 StudyAI — Your Personal Learning Assistant")

# --- 5. NAVIGATION TABS ---
tab_quiz, tab_flash, tab_visual, tab_notes = st.tabs([
    "📝 Quiz Generator", "🗂️ Flashcards", "🎨 Concept Visualizer", "📄 Notes Generator"
])

# --- TAB 1: QUIZ GENERATOR ---
with tab_quiz:
    st.header("Quiz Generator")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_ui("quiz")
        source = st.radio("Quiz Source", ["Text Content", "YouTube Link"], key="quiz_src")
    with col2:
        u_input = st.text_input("YouTube URL" if source == "YouTube Link" else "Paste text", key="quiz_in")
        if st.button("Create Quiz ✍️"):
            st.success(f"Processing in {st.session_state.output_lang}...")

# --- TAB 2: FLASHCARDS ---
with tab_flash:
    st.header("Active Recall Flashcards")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_ui("flash")
    with col2:
        flash_input = st.text_area("Paste text:", height=200, key="fc_txt")
        if st.button("Create Flashcards 🗂️"):
            st.warning("Generating cards...")

# --- TAB 3: CONCEPT VISUALIZER ---
with tab_visual:
    st.header("Concept Visualizer")
    if not MERMAID_AVAILABLE:
        st.error("Missing `streamlit-mermaid` in requirements.txt")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            language_ui("visual")
            viz_type = st.radio("Style", ["Flowchart", "Mind Map"], key="v_style")
        with col2:
            v_input = st.text_area("Paste text to visualize:", height=200, key="viz_txt")
            if st.button("Generate Visual 🎨"):
                if v_input:
                    with st.spinner("AI is drawing your diagram..."):
                        mermaid_code = call_grok_for_mermaid(v_input, viz_type, st.session_state.output_lang)
                        # Remove markdown code blocks if AI included them
                        clean_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
                        st_mermaid.st_mermaid(clean_code)
                else:
                    st.error("Please paste some text first!")

# --- TAB 4: NOTES GENERATOR ---
with tab_notes:
    st.header("Notes Generator")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_ui("notes")
        n_source = st.radio("Notes Source", ["Text", "YouTube"], key="n_src")
    with col2:
        n_input = st.text_input("Enter source here:", key="notes_in")
        if st.button("Generate Notes 📄"):
            st.info("Summarizing...")
