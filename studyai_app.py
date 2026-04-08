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

# --- 3. THE FIX: CLEANING THE MERMAID CODE ---
def clean_mermaid_syntax(code):
    """Removes characters that cause Mermaid to fail rendering."""
    # Remove markdown backticks and 'mermaid' labels
    code = re.sub(r'```mermaid|```|`|mermaid', '', code, flags=re.IGNORECASE).strip()
    # Remove common illegal characters inside the diagram logic
    code = code.replace(":", " ").replace("(", " ").replace(")", " ").replace("#", " ")
    return code

def call_groq(prompt_type, user_text, v_style="flowchart"):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Error: GROQ_API_KEY not found in Secrets."

    prompts = {
        "viz": f"""Convert this to Mermaid.js {v_style}.
        IMPORTANT RULES:
        1. Use 'graph TD' for flowchart.
        2. Use format: node1["Text"] --> node2["Text"].
        3. Do NOT use any special characters like () or : inside the quotes.
        4. Output ONLY the raw code.
        Language: {st.session_state.output_lang}.
        Text: {user_text[:1000]}""",
        "notes": f"Bullet point summary in {st.session_state.output_lang}: {user_text[:3000]}",
        "quiz": f"5 MCQs with answers in {st.session_state.output_lang}: {user_text[:2000]}",
        "flash": f"Q&A flashcards [Q] | [A] in {st.session_state.output_lang}: {user_text[:1500]}"
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=15,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": "You are a specialized Mermaid generator. No talking."},
                             {"role": "user", "content": prompts[prompt_type]}],
                "temperature": 0.1
            }
        )
        res = response.json()['choices'][0]['message']['content'].strip()
        return clean_mermaid_syntax(res)
    except Exception as e:
        return f"Error: {str(e)}"

# 4. Shared Language UI
def lang_ui(key):
    langs = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    idx = langs.index(st.session_state.output_lang)
    st.session_state.output_lang = st.selectbox("Output Language", langs, index=idx, key=f"lang_{key}")

# --- MAIN INTERFACE ---
st.title("🧠 StudyAI")

tabs = st.tabs(["📝 Quiz Generator", "🗂️ Flashcards", "🎨 Concept Visualizer", "📄 Notes Generator"])

# --- TAB: QUIZ ---
with tabs[0]:
    st.header("Quiz Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        lang_ui("quiz")
        q_src = st.radio("Source Type", ["Text", "YouTube Link"], key="q_src")
    with c2:
        q_in = st.text_input("Paste YouTube URL", key="q_yt") if q_src == "YouTube Link" else st.text_area("Paste Text", key="q_txt", height=200)
        if st.button("Create Quiz ✍️"):
            with st.spinner("Generating..."):
                res = call_groq("quiz", q_in)
                st.markdown(res)
                st.download_button("Download Quiz 📥", res, file_name="quiz.txt")

# --- TAB: FLASHCARDS ---
with tabs[1]:
    st.header("Flashcards")
    c1, c2 = st.columns([1, 2])
    with c1: lang_ui("fc")
    with c2:
        f_in = st.text_area("Paste text for cards:", height=200, key="f_in")
        if st.button("Create Flashcards 🗂️"):
            with st.spinner("Generating..."):
                f_res = call_groq("flash", f_in)
                st.markdown(f_res)
                st.download_button("Download Flashcards 📥", f_res, file_name="flashcards.txt")

# --- TAB: CONCEPT VISUALIZER ---
with tabs[2]:
    st.header("Concept Visualizer")
    if not MERMAID_AVAILABLE:
        st.error("Add `streamlit-mermaid` to requirements.txt.")
    else:
        c1, c2 = st.columns([1, 2])
        with c1:
            lang_ui("viz")
            v_style = st.radio("Style", ["Flowchart", "Mind Map"], key="v_style_widget")
        with c2:
            v_txt = st.text_area("Paste text to visualize:", height=200, key="v_txt")
            if st.button("Generate Visual 🎨"):
                if v_txt:
                    with st.spinner("AI is drawing..."):
                        code = call_groq("viz", v_txt, v_style.lower().replace(" ", ""))
                        if "graph" in code or "mindmap" in code:
                            st.success("Diagram Ready:")
                            # --- ACTUAL RENDERING ---
                            st_mermaid.st_mermaid(code, height=500)
                            # Show the code below for debugging if it still fails
                            with st.expander("Show Technical Code"):
                                st.code(code)
                        else:
                            st.error("AI failed to generate a diagram. Try a smaller text snippet.")

# --- TAB: NOTES ---
with tabs[3]:
    st.header("Notes Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        lang_ui("notes")
        n_src = st.radio("Source Type", ["Text", "YouTube Link"], key="n_src")
    with c2:
        n_in = st.text_input("Paste YouTube URL", key="n_yt_notes") if n_src == "YouTube Link" else st.text_area("Input Content", key="n_txt", height=200)
        if st.button("Generate Notes 📄"):
            with st.spinner("Summarizing..."):
                notes_res = call_groq("notes", n_in)
                st.markdown(notes_res)
                st.download_button("Download Notes 📥", notes_res, file_name="notes.txt")
