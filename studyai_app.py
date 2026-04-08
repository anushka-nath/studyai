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

# 4. Helper for UI consistency
def lang_ui(key):
    langs = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    idx = langs.index(st.session_state.output_lang)
    choice = st.selectbox("Output Language", langs, index=idx, key=f"lang_{key}")
    st.session_state.output_lang = choice

# --- MAIN INTERFACE ---
st.title("🧠
