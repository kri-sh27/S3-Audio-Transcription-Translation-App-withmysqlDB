# this file only generate audio and download audio

import streamlit as st
import openai
import speech_recognition as sr
import tempfile
import os

# Set your OpenAI API key
openai.api_key = ""  # Replace with your actual key

st.set_page_config(page_title="Voice to AI Audio", page_icon="🎤")
st.title("🎙️ Speak and Generate AI Voice (TTS)")

# Button to start recording
if st.button("🎧 Record from Mic"):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("Listening... Please speak into your mic.")
        audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        st.success("Recording complete!")

        try:
            st.info("Transcribing...")
            text = recognizer.recognize_google(audio_data)
            st.write("📝 Transcribed Text:")
            st.success(text)

            # Call OpenAI TTS
            st.info("Generating AI voice...")
            response = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",  # or shimmer, echo, etc.
                input=text
            )

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                tmpfile.write(response.content)
                tmpfile_path = tmpfile.name

            st.audio(tmpfile_path, format="audio/mp3")
            st.success("🔊 Audio playback ready")

            # Optionally allow download
            with open(tmpfile_path, "rb") as f:
                st.download_button("📥 Download Audio", f, file_name="output_audio.mp3", mime="audio/mp3")

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
