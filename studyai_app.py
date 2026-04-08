import streamlit as st
import requests
import re

# 1. Library Imports
try:
    import streamlit_mermaid as st_mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

# 2. Page Configuration
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# 3. Groq AI Logic
def call_groq(prompt_type, user_text):
    # Retrieve the key (ensure it's named GROQ_API_KEY in your Secrets)
    api_key = st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        return "⚠️ Secret Missing: Please add 'GROQ_API_KEY' to your Streamlit Secrets."

    # Language-aware prompts
    prompts = {
        "viz": f"Output ONLY raw Mermaid.js code for a flowchart or mindmap. No backticks. Language: {st.session_state.output_lang}. Text: {user_text[:1500]}",
        "notes": f"Summarize into professional bullet points in {st.session_state.output_lang}: {user_text[:3000]}",
        "quiz": f"Create 3 multiple choice questions in {st.session_state.output_lang} based on: {user_text[:2000]}"
    }

    try:
        # Calling Groq's high-speed endpoint
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=15,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a fast AI tutor. Output only the raw content requested without explanations."},
                    {"role": "user", "content": prompts[prompt_type]}
                ],
                "temperature": 0.2
            }
        )
        data = response.json()
        if 'choices' in data:
            result = data['choices'][0]['message']['content'].strip()
            # Clean out any markdown backticks that break the visualizer
            return re.sub(r'```mermaid|```|`', '', result).strip()
        else:
            return f"Groq Error: {data.get('error', {}).get('message', 'Unknown response format')}"
    except Exception as e:
        return f"Connection Failed: {str(e)}"

# 4. Helper for Language Sync
def lang_ui(key):
    langs = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    idx = langs.index(st.session_state.output_lang)
    st.session_state.output_lang = st.selectbox("Output Language", langs, index=idx, key=f"lang_{key}")

# --- MAIN APP ---
st.title("🧠 StudyAI")

t_quiz, t_flash, t_viz, t_notes = st.tabs(["📝 Quiz Generator", "🗂️ Flashcards", "🎨 Concept Visualizer", "📄 Notes Generator"])

# --- TAB: QUIZ ---
with t_quiz:
    st.header("Quiz Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        lang_ui("quiz")
        q_src = st.radio("Source", ["Text", "YouTube"], key="q_src")
    with c2:
        q_in = st.text_area("YouTube URL" if q_src == "YouTube" else "Paste Text", key="q_in", height=200)
        if st.button("Create Quiz ✍️"):
            with st.spinner("Groq is generating your quiz..."):
                st.markdown(call_groq("quiz", q_in))

# --- TAB: FLASHCARDS ---
with t_flash:
    st.header("Flashcards")
    c1, c2 = st.columns([1, 2])
    with c1: lang_ui("fc")
    with c2:
        f_in = st.text_area("Enter text for cards:", height=200, key="f_in")
        if st.button("Create Flashcards 🗂️"):
            st.info("Flashcard logic active.")

# --- TAB: CONCEPT VISUALIZER ---
with t_viz:
    st.header("Concept Visualizer")
    if not MERMAID_AVAILABLE:
        st.error("Missing library. Add `streamlit-mermaid` to requirements.txt.")
    else:
        c1, c2 = st.columns([1, 2])
        with c1:
            lang_ui("viz")
            v_style = st.radio("Style", ["Flowchart", "Mind Map"], key="v_style")
        with c2:
            v_txt = st.text_area("Paste text to visualize:", height=200, key="v_txt")
            if st.button("Generate Visual 🎨"):
                if v_txt:
                    with st.spinner("AI is drawing..."):
                        code = call_groq("viz", v_txt)
                        # Ensure the code starts with a valid Mermaid keyword
                        if any(x in code.lower() for x in ["graph", "mindmap", "sequence"]):
                            st_mermaid.st_mermaid(code, height=600)
                        else:
                            st.error(f"AI returned invalid format: {code[:100]}...")
                else:
                    st.warning("Please paste text first.")

# --- TAB: NOTES ---
with t_notes:
    st.header("Notes Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        lang_ui("notes")
        n_src = st.radio("Source", ["Text", "YouTube"], key="n_src")
    with c2:
        n_in = st.text_area("Input Content", key="n_in", height=200)
        if st.button("Generate Notes 📄"):
            with st.spinner("Groq is summarizing..."):
                st.markdown(call_groq("notes", n_in))
