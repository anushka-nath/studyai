import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Page config
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

# Custom CSS for better aesthetics
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
    patterns = [r'v=([a-zA-Z0-9_-]{11})', r'youtu\.be/([a-zA-Z0-9_-]{11})', r'embed/([a-zA-Z0-9_-]{11})']
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
    
    content_to_process = ""
    
    with col2:
        if input_type == "📋 Paste Text":
            content_to_process = st.text_area("Paste messy notes", height=200)
            prompt_prefix = "Transform this text into structured, hierarchical study notes."
        else:
            yt_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
            if yt_url:
                vid_id = get_video_id(yt_url)
                if vid_id:
                    with st.spinner("Fetching transcript..."):
                        try:
                            # Use the class method correctly
                            transcript_list = YouTubeTranscriptApi.list_transcripts(vid_id)
                            
                            try:
                                # Try manual English first
                                transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                            except:
                                try:
                                    # Fallback to auto-generated English
                                    transcript = transcript_list.find_generated_transcript(['en'])
                                except:
                                    # Final fallback: Take the first available and translate to English
                                    transcript = next(iter(transcript_list)).translate('en')
                            
                            data = transcript.fetch()
                            content_to_process = " ".join([t['text'] for t in data])
                            st.info(f"✅ Transcript loaded ({len(content_to_process.split())} words)")
                        except Exception as e:
                            # Final bulletproof fallback for older versions
                            try:
                                data = YouTubeTranscriptApi.get_transcript(vid_id)
                                content_to_process = " ".join([t['text'] for t in data])
                                st.info(f"✅ Transcript loaded via fallback ({len(content_to_process.split())} words)")
                            except:
                                st.error(f"❌ Transcript Error: {str(e)}")
                                st.info("This video might not have captions enabled.")
                else:
                    st.error("❌ Invalid URL.")
            prompt_prefix = "Summarize this transcript into professional study notes."

    if st.button("Generate Notes 📄", key="notes_btn"):
        if not content_to_process:
            st.warning("Please provide content.")
        else:
            with st.spinner("Organizing notes..."):
                prompt = f"{prompt_prefix}\nUse Markdown, include a Summary, Key Takeaways, and a Glossary.\n\nContent:\n{content_to_process}"
                result = generate(prompt)
                st.markdown(result)
                st.download_button("Download Notes (.txt)", result, file_name="study_notes.txt")

# ── TAB 3: FLASHCARDS ──
with tab3:
    st.subheader("Active Recall Flashcards")
    fc_input = st.text_area("Paste text to create flashcards", height=200, placeholder="Paste a paragraph or chapter summary...")
    
    if st.button("Create Flashcards 🗂️"):
        if not fc_input:
            st.warning("Input required.")
        else:
            with st.spinner("Generating cards..."):
                prompt = f"Create 5-10 flashcards from this text. Format each card as:\nFront: [Question]\nBack: [Answer]\n\nText:\n{fc_input}"
                result = generate(prompt)
                st.success("Flashcards Generated!")
                st.markdown(result)
                st.download_button("Download Flashcards", result, file_name="flashcards.txt")
