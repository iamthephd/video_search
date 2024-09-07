import streamlit as st

from video_search import get_timestamp_list

# Streamlit UI
st.title("YouTube Timestamp Finder")

video_url = st.text_input("Enter YouTube Video URL")
prompt = st.text_input("Enter your prompt")

if st.button("Submit"):
    if video_url and prompt:
        timestamps = get_timestamp_list(video_url, prompt)
        st.write("Timestamps:", timestamps)
    else:
        st.write("Please enter both a video URL and a prompt.")
