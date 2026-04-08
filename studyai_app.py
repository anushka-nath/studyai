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

# Sync language state
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# 3. Corrected Groq AI Logic
def call_groq(prompt_type, user_text, v_style="flowchart"):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Error: GROQ_API_KEY not found in Secrets."

    prompts = {
        "viz": f"Output ONLY raw Mermaid.js code for a {v_style}. No markdown backticks. Language: {st.session_state.output_lang}. Text: {user_text[:1500]}",
        "notes": f"Summarize into clean bullet points in {st.session_state.output_lang}: {user_text[:3000]}",
        "quiz": f"Create 5 multiple choice questions with answers in {st.session_state.output_lang} based on: {user_text[:2000]}",
        "flash": f"Create Q&A flashcards. Format: Front: [Q] | Back: [A]. Language: {st.session_state.output_lang}. Text: {user_text[:1500]}"
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=15,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": "You are a fast AI tutor. Output only the raw content requested."},
                             {"role": "user", "content": prompts[prompt_type]}],
                "temperature": 0.2
            }
        )
        data = response.json()
        if 'choices' in data:
            result = data['choices'][0]['message']['content'].strip()
            # Clean out any backticks or "mermaid" tags that break the visualizer
            return re.sub(r'```mermaid|```|`', '', result).strip()
        return "API Error: Invalid response."
    except Exception as e:
        return f"Connection Error: {str(e)}"

# 4. Helper for UI consistency
def lang_ui(key):
    langs = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    idx = langs.index(st.session_state.output_lang)
    new_lang = st.selectbox("Output Language", langs, index=idx, key=f"lang_{key}")
    st.session_state.output_lang = new_lang

# --- MAIN INTERFACE ---
st.title("🧠 StudyAI")

tabs = st.tabs(["📝 Quiz Generator", "🗂️ Flashcards", "🎨 Concept Visualizer", "📄 Notes Generator"])

# --- TAB 1: QUIZ ---
with tabs[0]:
    st.header("Quiz Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        lang_ui("quiz")
        q_src = st.radio("Source Type", ["Text", "YouTube Link"], key="q_src")
    with c2:
        # Restore YT Link input
        q_in = st.text_input("Paste YouTube URL here" if q_src == "YouTube Link" else "Paste Text Content", key="q_in")
        if st.button("Create Quiz ✍️"):
            with st.spinner("Analyzing..."):
                res = call_groq("quiz", q_in)
                st.markdown(res)
                st.download_button("Download Quiz 📥", res, file_name="quiz.txt")

# --- TAB 2: FLASHCARDS ---
with tabs[1]:
    st.header("Flashcards")
    c1, c2 = st.columns([1, 2])
    with c1: lang_ui("fc")
    with c2:
        f_in = st.text_area("Paste text for cards:", height=200, key="f_in")
        if st.button("Create Flashcards 🗂️"):
            with st.spinner("Generating cards..."):
                f_res = call_groq("flash", f_in)
                st.markdown(f_res)
                st.download_button("Download Flashcards 📥", f_res, file_name="flashcards.txt")

# --- TAB 3: CONCEPT VISUALIZER ---
with tabs[2]:
    st.header("Concept Visualizer")
    if not MERMAID_AVAILABLE:
        st.error("Add `streamlit-mermaid` to requirements.txt.")
    else:
        c1, c2 = st.columns([1, 2])
        with c1:
            lang_ui("viz")
            v_style_choice = st.radio("Style", ["Flowchart", "Mind Map"], key="v_style_widget")
        with c2:
            v_txt = st.text_area("Paste text to visualize:", height=200, key="v_txt")
            if st.button("Generate Visual 🎨"):
                if v_txt:
                    with st.spinner("AI is drawing..."):
                        style_clean = v_style_choice.lower().replace(" ", "")
                        code = call_groq("viz", v_txt, style_clean)
                        # The fix: This actually triggers the rendering component
                        if "graph" in code or "mindmap" in code:
                            st.success("Visual Generated Below:")
                            st_mermaid.st_mermaid(code, height=500)
                        else:
                            st.error(f"Syntax Error: AI produced text instead of a diagram. Try shorter text.")
                else:
                    st.warning("Please paste text first.")

# --- TAB 4: NOTES ---
with tabs[3]:
    st.header("Notes Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        lang_ui("notes")
        n_src = st.radio("Source Type", ["Text", "YouTube Link"], key="n_src")
    with c2:
        # Restore YT Link input
        n_in = st.text_input("Paste YouTube URL here" if n_src == "YouTube Link" else "Paste Text Content", key="n_in")
        if st.button("Generate Notes 📄"):
            with st.spinner("Summarizing..."):
                notes_res = call_groq("notes", n_in)
                st.markdown(notes_res)
                st.download_button("Download Notes 📥", notes_res, file_name="notes.txt")
