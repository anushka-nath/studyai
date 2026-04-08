import streamlit as st
import requests

# 1. Safe library import
try:
    import streamlit_mermaid as st_mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

# 2. Page Configuration
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

# Persistent State
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# 3. Helper: Grok AI Call
def call_grok(prompt):
    api_key = st.secrets.get("GROK_API_KEY")
    if not api_key:
        return "Error: Add GROK_API_KEY to Streamlit Secrets."
    try:
        response = requests.post(
            "[https://api.x.ai/v1/chat/completions](https://api.x.ai/v1/chat/completions)",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "grok-beta",
                "messages": [{"role": "system", "content": "You are a helpful assistant that outputs only raw Mermaid.js code. No backticks, no talk."},
                             {"role": "user", "content": prompt}],
                "temperature": 0
            }
        )
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# 4. Helper: Shared Language Selector
def lang_selector(key):
    langs = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    idx = langs.index(st.session_state.output_lang)
    choice = st.selectbox("Output Language", langs, index=idx, key=f"lang_{key}")
    st.session_state.output_lang = choice

# --- MAIN UI ---
st.title("🧠 StudyAI")

tabs = st.tabs(["📝 Quiz Generator", "🗂️ Flashcards", "🎨 Concept Visualizer", "📄 Notes Generator"])

# --- TAB: QUIZ ---
with tabs[0]:
    st.header("Quiz Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        lang_selector("quiz")
        src = st.radio("Source", ["Text", "YouTube"], key="q_src")
    with c2:
        inp = st.text_input("YouTube URL" if src == "YouTube" else "Paste Text", key="q_inp")
        if st.button("Create Quiz ✍️"):
            st.success(f"Generating {st.session_state.output_lang} quiz...")

# --- TAB: FLASHCARDS ---
with tabs[1]:
    st.header("Flashcards")
    c1, c2 = st.columns([1, 2])
    with c1: lang_selector("fc")
    with c2:
        f_inp = st.text_area("Content:", height=200, key="f_inp")
        if st.button("Create Flashcards 🗂️"):
            st.warning("Generating cards...")

# --- TAB: CONCEPT VISUALIZER ---
with tabs[2]:
    st.header("Concept Visualizer")
    if not MERMAID_AVAILABLE:
        st.error("Add `streamlit-mermaid` to requirements.txt on GitHub!")
    else:
        c1, c2 = st.columns([1, 2])
        with c1:
            lang_selector("viz")
            v_style = st.radio("Style", ["Flowchart", "Mind Map"], key="v_style")
        with c2:
            v_text = st.text_area("Paste text to visualize:", height=200, key="v_txt")
            if st.button("Generate Visual 🎨"):
                if v_text:
                    with st.spinner("AI is drawing..."):
                        # Specialized prompt to prevent syntax errors
                        prompt = f"Convert this to a Mermaid {v_style} in {st.session_state.output_lang}. Use 'graph TD' for flowcharts and 'mindmap' for mind maps. Output RAW code only: {v_text[:1500]}"
                        raw_code = call_grok(prompt)
                        
                        # CLEANING THE CODE (Fixes the syntax error bomb)
                        clean_code = raw_code.replace("```mermaid", "").replace("```", "").strip()
                        
                        try:
                            st_mermaid.st_mermaid(clean_code)
                        except:
                            st.error("AI produced invalid syntax. Please try again.")
                else:
                    st.info("Please paste text first.")

# --- TAB: NOTES ---
with tabs[3]:
    st.header("Notes Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        lang_selector("notes")
        n_src = st.radio("Source", ["Text", "YouTube"], key="n_src")
    with c2:
        n_inp = st.text_input("Input Source", key="n_inp")
        if st.button("Generate Notes 📄"):
            st.info("Summarizing...")
            
