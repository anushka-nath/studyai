import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Page config
st.set_page_config(page_title="StudyAI", page_icon="🧠", layout="centered")

# Title
st.title("🧠 StudyAI — Learn Smarter")
st.markdown("Built by **Anushka Nath** | AI-powered study tools")
st.divider()

# API Key input
api_key = st.text_input("Enter your Groq API Key", type="password", placeholder="gsk_...")

# Helper function to extract video ID
def get_video_id(url):
    patterns = [
        r'v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# Helper function to generate with Groq
def generate(api_key, prompt):
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Tabs
tab1, tab2 = st.tabs(["📝 Quiz Generator", "📄 Notes Generator"])

# ── TAB 1: QUIZ GENERATOR ──
with tab1:
    st.subheader("Generate Quiz from Your Notes")
    notes_input = st.text_area("Paste your notes here", height=200, placeholder="Paste any topic or notes...")
    num_questions = st.slider("Number of questions", 3, 10, 5)

    if st.button("Generate Quiz ⚡", key="quiz"):
        if not api_key:
            st.error("Please enter your Groq API key above!")
        elif not notes_input:
            st.error("Please paste some notes first!")
        else:
            with st.spinner("Generating quiz..."):
                try:
                    prompt = f"""Create {num_questions} multiple choice questions from these notes.
Format each question exactly like this:
Q1. Question here?
A) Option 1
B) Option 2
C) Option 3
D) Option 4
Answer: A

Notes:
{notes_input}"""
                    result = generate(api_key, prompt)
                    st.success("Quiz Ready!")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ── TAB 2: NOTES GENERATOR ──
with tab2:
    st.subheader("Generate Clean Notes from Any Text or YouTube Video")

    input_type = st.radio("Choose input type", ["📋 Paste Text", "🎥 YouTube Link"])

    content_to_process = ""

    if input_type == "📋 Paste Text":
        raw_input = st.text_area("Paste raw text or messy notes", height=200, placeholder="Paste anything here...")
        content_to_process = raw_input
        prompt_prefix = "Convert the following text into clean, well-structured study notes."

    else:
        yt_url = st.text_input("Paste YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")

        if yt_url:
            video_id = get_video_id(yt_url)
            if video_id:
                with st.spinner("Fetching transcript from YouTube..."):
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                        transcript_text = " ".join([t['text'] for t in transcript_list])
                        content_to_process = transcript_text
                        st.success(f"✅ Transcript fetched! ({len(transcript_text.split())} words)")
                        with st.expander("Preview transcript"):
                            st.write(transcript_text[:500] + "...")
                    except Exception as e:
                        st.error("❌ Could not fetch transcript. Try another video.")
            else:
                st.error("❌ Invalid YouTube URL. Please check and try again.")

        prompt_prefix = "Convert the following YouTube video transcript into clean, well-structured study notes."

    if st.button("Generate Notes 📄", key="notes"):
        if not api_key:
            st.error("Please enter your Groq API key above!")
        elif not content_to_process.strip():
            st.error("Please provide some content first!")
        else:
            with st.spinner("Generating notes..."):
                try:
                    prompt = f"""{prompt_prefix}
Use headings, bullet points, and highlight key terms.
Make it easy to read and revise from.
Include a summary at the top.

Content:
{content_to_process}"""
                    result = generate(api_key, prompt)
                    st.success("Notes Ready!")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Error: {str(e)}")