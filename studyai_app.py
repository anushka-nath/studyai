import streamlit as st

# Attempt to import Mermaid, but don't crash if it's missing
try:
    import streamlit_mermaid as st_mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

# --- 1. PAGE CONFIG & SESSION STATE ---
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

# Ensure language selection is remembered across all tabs
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# --- 2. SHARED HELPERS ---
def language_selection_ui():
    """Renders the language selector and updates the session state."""
    languages = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    try:
        current_index = languages.index(st.session_state.output_lang)
    except ValueError:
        current_index = 0
        
    selected_lang = st.selectbox(
        "Select Output Language", 
        languages, 
        index=current_index,
        key=f"lang_{st.session_state.get('active_tab', 'default')}" # Dynamic key
    )
    st.session_state.output_lang = selected_lang

# --- 3. APP HEADER ---
st.title("🧠 StudyAI — Your Personal Learning Assistant")
st.markdown(f"**Current Language:** {st.session_state.output_lang}")

# --- 4. NAVIGATION TABS ---
tab_quiz, tab_flash, tab_visual, tab_notes = st.tabs([
    "📝 Quiz Generator", 
    "🗂️ Flashcards", 
    "📊 Visual Aids", 
    "📄 Notes Generator"
])

# --- TAB 1: QUIZ GENERATOR ---
with tab_quiz:
    st.session_state.active_tab = "quiz"
    st.header("Quiz Generator")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_selection_ui()
    with col2:
        quiz_input = st.text_area("Paste text to generate a quiz:", height=200, key="quiz_input")
        if st.button("Create Quiz ✍️"):
            st.success(f"Generating quiz in {st.session_state.output_lang}...")

# --- TAB 2: FLASHCARDS ---
with tab_flash:
    st.session_state.active_tab = "flash"
    st.header("Active Recall Flashcards")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_selection_ui()
    with col2:
        flash_input = st.text_area("Paste content for flashcards:", height=200, key="flash_input")
        if st.button("Create Flashcards 🗂️"):
            st.warning(f"Generating flashcards in {st.session_state.output_lang}...")

# --- TAB 3: VISUAL AIDS (FLOWCHART & MIND MAP) ---
with tab_visual:
    st.session_state.active_tab = "visual"
    st.header("Visual Learning Aids")
    
    if not MERMAID_AVAILABLE:
        st.error("⚠️ Visualization library not found. Please add 'streamlit-mermaid' to your requirements.txt file on GitHub.")
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            language_selection_ui()
            viz_choice = st.radio("Select Type", ["Flowchart", "Mind Map"])
        with col2:
            viz_input = st.text_area("Paste steps or topics:", height=200, key="viz_input")
            if st.button("Generate Visual 🎨"):
                if viz_choice == "Flowchart":
                    chart_code = "graph TD; A[Start] --> B[Process]; B --> C[End];"
                else:
                    chart_code = "mindmap\n  root((Topic))\n    Sub 1\n    Sub 2"
                st_mermaid.st_mermaid(chart_code)

# --- TAB 4: NOTES GENERATOR ---
with tab_notes:
    st.session_state.active_tab = "notes"
    st.header("Notes Generator")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_selection_ui()
    with col2:
        notes_input = st.text_area("Input content:", height=200, key="notes_input")
        if st.button("Generate Notes 📄"):
            st.info(f"Summarizing in {st.session_state.output_lang}...")
