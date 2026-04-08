import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Page config
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="wide")

# Title
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
        messages=[{"role": "system", "content": "You are a helpful educational assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Tabs
tab1, tab2 = st.tabs(["📝 Quiz Generator", "📄 Notes Generator"])

# ── TAB 1: QUIZ GENERATOR ──
with tab1:
    st.subheader("Generate Quiz from Your Notes")
    notes_input = st.text_area("Paste your notes here", height=250, placeholder="Paste any topic or notes...")
    num_questions = st.slider("Number of questions", 3, 15, 5)

    if st.button("Generate Quiz ⚡", key="quiz"):
        if not notes_input:
            st.error("Please paste some notes first!")
        else:
            with st.spinner("Analyzing content and creating questions..."):
                try:
                    prompt = f"Create {num_questions} multiple choice questions based on these notes. Provide the correct answer and a brief explanation for each.\n\nNotes:\n{notes_input}"
                    result = generate(prompt)
                    st.success("Quiz Ready!")
                    st.markdown(result)
                    st.download_button("Download Quiz", result, file_name="quiz.txt")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ── TAB 2: NOTES GENERATOR ──
with tab2:
    st.subheader("Generate Clean Notes")
    input_type = st.radio("Choose input type", ["📋 Paste Text", "🎥 YouTube Link"], horizontal=True)
    content_to_process = ""

    if input_type == "📋 Paste Text":
        content_to_process = st.text_area("Paste raw text", height=250, placeholder="Paste messy notes here...")
        prompt_prefix = "Transform this text into structured, hierarchical study notes."
    else:
        yt_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        if yt_url:
            vid_id = get_video_id(yt_url)
            if vid_id:
                try:
                    # Improved transcript fetching (tries English first, then others)
                    transcript_list = YouTubeTranscriptApi.list_transcripts(vid_id)
                    transcript = transcript_list.find_transcript(['en', 'es', 'fr', 'de']).fetch()
                    content_to_process = " ".join([t['text'] for t in transcript])
                    st.success(f"✅ Transcript fetched! ({len(content_to_process.split())} words)")
                except Exception:
                    st.error("❌ Could not fetch transcript. Check if captions are enabled for this video.")
            else:
                st.error("❌ Invalid URL.")
        prompt_prefix = "Summarize this video transcript into detailed study notes with key takeaways."

    if st.button("Generate Notes 📄", key="notes"):
        if not content_to_process:
            st.error("Please provide content first!")
        else:
            with st.spinner("Structuring your notes..."):
                try:
                    prompt = f"{prompt_prefix}\nUse Markdown (headings, bold text, bullets). Include a 'Summary' and a 'Key Terms' section.\n\nContent:\n{content_to_process}"
                    result = generate(prompt)
                    st.success("Notes Ready!")
                    st.markdown(result)
                    st.download_button("Download Notes", result, file_name="notes.txt")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
