import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Page config
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4A90E2; color: white; }
    .stTextArea>div>div>textarea { font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# Title & Credits
st.title("🧠 StudyAI — Learn Smarter")
st.markdown("Built by **Anushka Nath** | AI-powered study tools")
st.divider()

# API Key handling
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("GROQ_API_KEY not found in Streamlit Secrets!")
    st.stop()

# Helper: Extract video ID
def get_video_id(url):
    patterns = [
        r'v=([a-zA-Z0-9_-]{11})', 
        r'youtu\.be/([a-zA-Z0-9_-]{11})', 
        r'embed/([a-zA-Z0-9_-]{11})',
        r'youtube.com/shorts/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match: return match.group(1)
    return None

# Helper: Generate with Groq
def generate(prompt):
    client = Groq(api_key=API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert educator. Simplify complex topics into clear, accurate study materials."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Quiz Generator", "📄 Notes Generator", "🗂️ Flashcards"])

# ── TAB 1: QUIZ GENERATOR ──
with tab1:
    st.subheader("Generate Quiz from Your Notes")
    notes_input = st.text_area("Paste your notes here", height=200, placeholder="Paste any topic or notes...", key="quiz_input")
    num_questions = st.slider("Number of questions", 3, 15, 5, key="q_slider")

    if st.button("Generate Quiz ⚡", key="quiz_btn"):
        if not notes_input:
            st.warning("Please paste some notes first!")
        else:
            with st.spinner("Crafting your quiz..."):
                try:
                    prompt = f"Create {num_questions} high-quality MCQs from these notes. Format: Question, 4 Options (A-D), Correct Answer, and a 'Why?' explanation.\n\nNotes:\n{notes_input}"
                    result = generate(prompt)
                    st.success("Quiz Ready!")
                    st.markdown(result)
                    st.download_button("Download Quiz (.txt)", result, file_name="study_quiz.txt")
                except Exception as e:
                    st.error(f"API Error: {str(e)}")

# ── TAB 2: NOTES GENERATOR ──
with tab2:
    st.subheader("Generate Clean Notes")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        input_type = st.radio("Input Source", ["📋 Paste Text", "🎥 YouTube Link"])
        # NEW: Language Selection
        target_lang = st.selectbox("Output Language", 
                                 ["English", "Hindi", "Spanish", "French", "German", "Bengali", "Marathi"], 
                                 index=0)
    
    content_to_process = ""
    
    with col2:
        if input_type == "📋 Paste Text":
            content_to_process = st.text_area("Paste messy notes", height=200, key="manual_notes")
            prompt_prefix = f"Transform this text into structured, hierarchical study notes in {target_lang}."
        else:
            yt_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...", key="yt_url_input")
            if yt_url:
                vid_id = get_video_id(yt_url)
                if vid_id:
                    with st.spinner("Fetching transcript..."):
                        try:
                            # Robust transcript fetching
                            transcript_list = YouTubeTranscriptApi.list_transcripts(vid_id)
                            # Attempt to find English or fallback to any available
                            try:
                                transcript = transcript_list.find_transcript(['en'])
                            except:
                                transcript = next(iter(transcript_list))
                            
                            data = transcript.fetch()
                            content_to_process = " ".join([t['text'] for t in data])
                            st.info(f"✅ Transcript loaded ({len(content_to_process.split())} words)")
                        except Exception as e:
                            st.error(f"❌ YouTube Fetch Failed. YouTube often blocks automated access from cloud servers.")
                            st.info("Tip: If this persists, try copying the transcript manually from YouTube and using 'Paste Text' mode.")
                else:
                    st.error("❌ Invalid URL.")
            prompt_prefix = f"Summarize this transcript into professional study notes in {target_lang}."

    if st.button("Generate Notes 📄", key="notes_btn"):
        if not content_to_process:
            st.warning("Please provide content.")
        else:
            with st.spinner(f"Organizing notes in {target_lang}..."):
                try:
                    prompt = f"{prompt_prefix}\nUse Markdown, include a Summary, Key Takeaways, and a Glossary. All output must be in {target_lang}.\n\nContent:\n{content_to_process}"
                    result = generate(prompt)
                    st.markdown(result)
                    st.download_button(f"Download {target_lang} Notes (.txt)", result, file_name=f"study_notes_{target_lang}.txt")
                except Exception as e:
                    st.error(f"Generation Error: {str(e)}")

# ── TAB 3: FLASHCARDS ──
with tab3:
    st.subheader("Active Recall Flashcards")
    fc_input = st.text_area("Paste text to create flashcards", height=200, placeholder="Paste text here...", key="fc_input")
    
    if st.button("Create Flashcards 🗂️", key="fc_btn"):
        if not fc_input:
            st.warning("Input required.")
        else:
            with st.spinner("Generating cards..."):
                try:
                    prompt = f"Create 5-10 flashcards from this text. Format: Front: [Question] Back: [Answer].\n\nText:\n{fc_input}"
                    result = generate(prompt)
                    st.success("Flashcards Generated!")
                    st.markdown(result)
                    st.download_button("Download Flashcards", result, file_name="flashcards.txt")
                except Exception as e:
                    st.error(f"Generation Error: {str(e)}")
