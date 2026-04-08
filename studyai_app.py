import streamlit as st
import streamlit_mermaid as st_mermaid

# --- PAGE CONFIG ---
st.set_page_config(page_title="StudyAI — Learn Smarter", page_icon="🧠", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'output_lang' not in st.session_state:
    st.session_state.output_lang = 'English'

# --- SHARED UI COMPONENTS ---
def language_selector():
    st.session_state.output_lang = st.selectbox(
        "Output Language", 
        ["English", "Spanish", "French", "German", "Hindi", "Bengali"],
        index=["English", "Spanish", "French", "German", "Hindi", "Bengali"].index(st.session_state.output_lang)
    )

def input_section(button_label):
    col1, col2 = st.columns([1, 2])
    with col1:
        source = st.radio("Input Source", ["📋 Paste Text", "🎥 YouTube Link"])
        language_selector()
    with col2:
        text_input = st.text_area("Paste content here...", height=200)
    
    return st.button(button_label), text_input

# --- MAIN APP LOGIC ---
st.title("🧠 StudyAI — Learn Smarter")
st.caption("Built by Anushka Nath | AI-powered study tools")

# Navigation Tabs
tabs = st.tabs(["📝 Quiz Generator", "📄 Notes Generator", "🗂️ Flashcards", "📊 Visual Aids"])

# --- 1. QUIZ GENERATOR ---
with tabs[0]:
    st.header("Generate Quiz")
    clicked, data = input_section("Create Quiz ✍️")
    if clicked:
        st.info(f"Generating quiz in {st.session_state.output_lang}...")
        # Add your AI logic here

# --- 2. NOTES GENERATOR ---
with tabs[1]:
    st.header("Generate Clean Notes")
    clicked, data = input_section("Generate Notes 📄")
    if clicked:
        st.success(f"Notes generated in {st.session_state.output_lang}!")
        # Add your AI logic here

# --- 3. FLASHCARDS ---
with tabs[2]:
    st.header("Active Recall Flashcards")
    clicked, data = input_section("Create Flashcards 🗂️")
    if clicked:
        st.warning(f"Flashcards ready in {st.session_state.output_lang}!")
        # Add your AI logic here

# --- 4. VISUAL AIDS (NEW SECTION) ---
with tabs[3]:
    st.header("Visual Learning Aids")
    v_col1, v_col2 = st.columns([1, 2])
    
    with v_col1:
        viz_type = st.radio("Select Type", ["Flowchart", "Mind Map"])
        language_selector()
    
    with v_col2:
        viz_input = st.text_area("Paste process or topics to visualize...", height=150)
        generate_viz = st.button("Visualize 🎨")

    if generate_viz:
        st.subheader(f"Your {viz_type}")
        
        # This is a placeholder Mermaid string. 
        # You would use your AI to generate this syntax based on user input.
        if viz_type == "Flowchart":
            mermaid_code = """
            graph TD
                A[Start] --> B{Is it working?}
                B -- Yes --> C[Great!]
                B -- No --> D[Debug Code]
            """
        else:
            mermaid_code = """
            mindmap
              root((Study Subject))
                Topic 1
                  Subtopic A
                Topic 2
                  Subtopic B
            """
        
        st_mermaid.st_mermaid(mermaid_code)
