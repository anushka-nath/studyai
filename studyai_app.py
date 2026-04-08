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

# Persistent state
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# --- 3. THE ENGINE: GROQ API ---
def call_groq(prompt_type, user_text, count=5, v_style="flowchart"):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Error: GROQ_API_KEY not found in Secrets."

    prompts = {
        "viz": f"Output ONLY raw Mermaid.js code for a {v_style}. Use node['text'] format. No special chars. Language: {st.session_state.output_lang}. Text: {user_text[:1200]}",
        "notes": f"Summarize into professional bullet points in {st.session_state.output_lang}: {user_text[:3000]}",
        "quiz": f"Create EXACTLY {count} multiple choice questions with answers in {st.session_state.output_lang} based on: {user_text[:2000]}",
        "flash": f"Create EXACTLY {count} Flashcards. Format:\n**Card X**\nFront: [Q]\nBack: [A]\n\nLanguage: {st.session_state.output_lang}. Text: {user_text[:1500]}"
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=20,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": "You are a specialized AI tutor. Provide clear, formatted output."},
                             {"role": "user", "content": prompts[prompt_type]}],
                "temperature": 0.2
            }
        )
        data = response.json()
        if 'choices' in data:
            res = data['choices'][0]['message']['content'].strip()
            if prompt_type == "viz":
                return re.sub(r'```mermaid|```|`|mermaid', '', res, flags=re.IGNORECASE).strip()
            return res
        return "Error: API returned empty response."
    except Exception as e:
        return f"Error: {str(e)}"

# --- MAIN INTERFACE ---
st.title("🧠 StudyAI")

tabs = st.tabs(["📝 Quiz Generator", "🗂️ Flashcards", "🎨 Concept Visualizer", "📄 Notes Generator"])

langs = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]

# --- TAB 1: QUIZ ---
with tabs[0]:
    st.header("Quiz Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.session_state.output_lang = st.selectbox("Output Language", langs, key="l_q")
        q_src = st.radio("Source Type", ["Text", "YouTube Link"], key="q_src")
        q_count = st.slider("Number of Questions", 3, 15, 5, key="q_cnt")
    with c2:
        if q_src == "YouTube Link":
            q_in = st.text_input("Paste YouTube URL", key="q_yt_in")
        else:
            q_in = st.text_area("Paste Text", key="q_tx_in", height=200)
            
        if st.button("Create Quiz ✍️"):
            if q_in:
                with st.spinner("Generating..."):
                    res = call_groq("quiz", q_in, count=q_count)
                    st.markdown(res)
                    st.download_button("Download Quiz 📥", res, file_name="quiz.txt")
            else:
                st.warning("Please enter content first.")

# --- TAB 2: FLASHCARDS ---
with tabs[1]:
    st.header("Flashcards")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.session_state.output_lang = st.selectbox("Output Language", langs, key="l_f")
        f_count = st.slider("Number of Cards", 3, 15, 5, key="f_cnt")
    with c2:
        f_in = st.text_area("Paste text for cards:", height=200, key="f_tx_in")
        if st.button("Create Flashcards 🗂️"):
            if f_in:
                with st.spinner("Generating..."):
                    f_res = call_groq("flash", f_in, count=f_count)
                    st.markdown(f_res)
                    st.download_button("Download Flashcards 📥", f_res, file_name="cards.txt")
            else:
                st.warning("Please paste text.")

# --- TAB 3: CONCEPT VISUALIZER ---
with tabs[2]:
    st.header("Concept Visualizer")
    if not MERMAID_AVAILABLE:
        st.error("Missing streamlit-mermaid library.")
    else:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.session_state.output_lang = st.selectbox("Output Language", langs, key="l_v")
            v_style = st.radio("Style", ["Flowchart", "Mind Map"], key="v_st")
        with c2:
            v_in = st.text_area("Paste text to visualize:", height=200, key="v_tx_in")
            if st.button("Generate Visual 🎨"):
                if v_in:
                    with st.spinner("Drawing..."):
                        code = call_groq("viz", v_in, v_style=v_style.lower().replace(" ", ""))
                        if "graph" in code or "mindmap" in code:
                            st.success("Visual Ready!")
                            st_mermaid.st_mermaid(code, height=500)
                        else:
                            st.error("Failed to render diagram code.")
                else:
                    st.warning("Please paste text.")

# --- TAB 4: NOTES ---
with tabs[3]:
    st.header("Notes Generator")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.session_state.output_lang = st.selectbox("Output Language", langs, key="l_n")
        n_src = st.radio("Source Type", ["Text", "YouTube Link"], key="n_src")
    with c2:
        if n_src == "YouTube Link":
            n_in = st.text_input("Paste YouTube URL", key="n_yt_in")
        else:
            n_in = st.text_area("Input Content", key="n_tx_in", height=200)
            
        if st.button("Generate Notes 📄"):
            if n_in:
                with st.spinner("Summarizing..."):
                    n_res = call_groq("notes", n_in)
                    st.markdown(n_res)
                    st.download_button("Download Notes 📥", n_res, file_name="notes.txt")
            else:
                st.warning("Please enter content.")
