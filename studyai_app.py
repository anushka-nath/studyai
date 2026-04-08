import streamlit as st

# Safe import for Mermaid
try:
    import streamlit_mermaid as st_mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

# --- 1. PAGE CONFIG & SESSION STATE ---
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

# Global state for language
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# --- 2. SHARED UI COMPONENTS ---
def language_ui(key_suffix):
    languages = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    index = languages.index(st.session_state.output_lang)
    # Update global state when this specific dropdown changes
    new_lang = st.selectbox("Select Output Language", languages, index=index, key=f"lang_{key_suffix}")
    st.session_state.output_lang = new_lang

# --- 3. APP HEADER ---
st.title("🧠 StudyAI — Your Personal Learning Assistant")
st.markdown(f"**Current Language Global Setting:** {st.session_state.output_lang}")

# --- 4. NAVIGATION TABS ---
tab_quiz, tab_flash, tab_visual, tab_notes = st.tabs([
    "📝 Quiz Generator", 
    "🗂️ Flashcards", 
    "📊 Visual Aids", 
    "📄 Notes Generator"
])

# --- TAB 1: QUIZ GENERATOR ---
with tab_quiz:
    st.header("Quiz Generator")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_ui("quiz")
        source = st.radio("Quiz Source", ["Text Content", "YouTube Link"], key="quiz_src")
    with col2:
        if source == "YouTube Link":
            u_input = st.text_input("Enter YouTube URL:", key="quiz_yt_url")
        else:
            u_input = st.text_area("Paste text:", height=200, key="quiz_txt")
        
        if st.button("Create Quiz ✍️"):
            st.success(f"Processing {source} in {st.session_state.output_lang}...")

# --- TAB 2: FLASHCARDS ---
with tab_flash:
    st.header("Active Recall Flashcards")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_ui("flash")
    with col2:
        flash_input = st.text_area("Paste content for cards:", height=200, key="fc_txt")
        if st.button("Create Flashcards 🗂️"):
            st.warning(f"Creating cards in {st.session_state.output_lang}...")

# --- TAB 3: VISUAL AIDS ---
with tab_visual:
    st.header("Visual Learning Aids")
    if not MERMAID_AVAILABLE:
        st.error("⚠️ Library 'streamlit-mermaid' missing. Add it to requirements.txt on GitHub!")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            language_ui("visual")
            viz_type = st.radio("Format", ["Flowchart", "Mind Map"])
        with col2:
            viz_input = st.text_area("Paste steps or hierarchy:", height=200, key="viz_txt")
            if st.button("Generate Visual 🎨"):
                # Placeholder for AI-generated Mermaid code
                code = "graph TD; A[Start] --> B[Step]; B --> C[End];" if viz_type == "Flowchart" else "mindmap\n  root((Topic))\n    Sub"
                st_mermaid.st_mermaid(code)

# --- TAB 4: NOTES GENERATOR ---
with tab_notes:
    st.header("Notes Generator")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_ui("notes")
        n_source = st.radio("Notes Source", ["Paste Text", "YouTube Link"], key="notes_src")
    with col2:
        if n_source == "YouTube Link":
            n_input = st.text_input("Enter YouTube URL:", key="notes_yt_url")
        else:
            n_input = st.text_area("Input content:", height=200, key="notes_txt")
            
        if st.button("Generate Notes 📄"):
            st.info(f"Summarizing {n_source} in {st.session_state.output_lang}...")
