import streamlit as st
import streamlit_mermaid as st_mermaid

# --- 1. PAGE CONFIG & SESSION STATE ---
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

# This ensures that if you change language in one tab, it stays changed in others
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# --- 2. SHARED HELPERS ---
def language_selection_ui():
    """Renders the language selector and updates the session state."""
    languages = ["English", "Spanish", "French", "German", "Hindi", "Bengali"]
    # Find index of current language to keep it selected
    try:
        current_index = languages.index(st.session_state.output_lang)
    except ValueError:
        current_index = 0
        
    selected_lang = st.selectbox(
        "Select Output Language", 
        languages, 
        index=current_index,
        key="global_lang_selector"
    )
    st.session_state.output_lang = selected_lang

# --- 3. APP HEADER ---
st.title("🧠 StudyAI — Your Personal Learning Assistant")
st.info(f"Current Output Language: **{st.session_state.output_lang}**")

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
        language_selection_ui()
        quiz_type = st.selectbox("Quiz Type", ["Multiple Choice", "True/False", "Short Answer"])
    with col2:
        quiz_input = st.text_area("Paste text or notes to generate a quiz:", height=200, key="quiz_input")
        if st.button("Create Quiz ✍️"):
            st.success(f"Generating {quiz_type} quiz in {st.session_state.output_lang}...")
            # Insert your AI logic here

# --- TAB 2: FLASHCARDS ---
with tab_flash:
    st.header("Active Recall Flashcards")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_selection_ui()
        st.write("Convert concepts into Q&A cards.")
    with col2:
        flash_input = st.text_area("Paste content for flashcards:", height=200, key="flash_input")
        if st.button("Create Flashcards 🗂️"):
            st.warning(f"Generating flashcards in {st.session_state.output_lang}...")
            # Insert your AI logic here

# --- TAB 3: VISUAL AIDS (NEW) ---
with tab_visual:
    st.header("Flowcharts & Mind Maps")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_selection_ui()
        viz_choice = st.radio("Select Visualization Type", ["Flowchart", "Mind Map"])
        st.caption("Flowcharts are great for processes; Mind Maps are best for hierarchies.")
    
    with col2:
        viz_input = st.text_area("Paste process steps or topic hierarchy:", height=200, key="viz_input")
        if st.button("Generate Visual 🎨"):
            st.subheader(f"Your {viz_choice}")
            
            # Note: In a real scenario, your AI would generate the Mermaid string.
            # Below are static examples to show it works.
            if viz_choice == "Flowchart":
                chart_code = "graph TD; A[Start] --> B[Step 1]; B --> C[Step 2]; C --> D[End];"
            else:
                chart_code = "mindmap\n  root((Main Topic))\n    Subtopic 1\n    Subtopic 2\n    Subtopic 3"
            
            st_mermaid.st_mermaid(chart_code)

# --- TAB 4: NOTES GENERATOR ---
with tab_notes:
    st.header("Notes Generator")
    col1, col2 = st.columns([1, 2])
    with col1:
        language_selection_ui()
        source_type = st.radio("Source", ["Paste Text", "YouTube Link"])
    with col2:
        notes_input = st.text_area("Input source content:", height=200, key="notes_input")
        if st.button("Generate Notes 📄"):
            st.info(f"Summarizing notes in {st.session_state.output_lang}...")
            # Insert your AI logic here
