# import openai 
# import os
# from dotenv import load_dotenv
# from flask import Flask, request, jsonify, render_template

# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# openai.api_key = OPENAI_API_KEY

# app = Flask(__name__)
# app.config["UPLOAD_FOLDER"] = "static"


# @app.route('/', methods=['GET', 'POST'])
# def main():
#     if request.method == "POST":
#         language = request.form["language"]
#         file = request.files["file"]
#         if file:
#             filename = file.filename
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
#             audio_file = open("static/Recording.mp3", "rb")
#             transcript = openai.Audio.translate("whisper-1", audio_file)

#             response = openai.ChatCompletion.create(
#                     model="gpt-4",
#                     messages = [{ "role": "system", "content": f"You will be provided with a sentence in English, and your task is to translate it into {language}" }, 
#                                 { "role": "user", "content": transcript.text }],
#                     temperature=0,
#                     max_tokens=256
#                   )
            
#             return jsonify(response)
        
    
#     return render_template("index.html")



# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=True, port=8080)




import streamlit as st
import os
import tempfile

from backend.auth import authenticate_user, register_user
from backend.s3_utils import list_s3_audio_files, download_s3_file
from backend.openai_utils import transcribe_audio, translate_text

# ------------------------- LOGIN / REGISTER -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "view" not in st.session_state:
    st.session_state.view = "register"  # default is now register

def switch_view(view_name):
    st.session_state.view = view_name
    st.rerun()

if not st.session_state.authenticated:
    if st.session_state.view == "login":
        st.title("🔐 Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
        if submitted:
            if authenticate_user(email, password):
                st.session_state.authenticated = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
        st.info("New here?")
        if st.button("Register here"):
            switch_view("register")
    elif st.session_state.view == "register":
        st.title("📝 Create a New Account")
        with st.form("register_form"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
        if submitted:
            if new_password != confirm_password:
                st.warning("⚠️ Passwords do not match.")
            elif len(new_password) < 6:
                st.warning("⚠️ Password must be at least 6 characters long.")
            else:
                success, msg = register_user(new_email, new_password)
                if success:
                    st.success(msg)
                    if st.button("Go to Login"):
                        switch_view("login")
                else:
                    st.error(msg)
        st.info("Already registered?")
        if st.button("Login here"):
            switch_view("login")
    st.stop()

# ------------------------- AUDIO TRANSCRIPTION APP -------------------------
st.title("🎙️ S3 Audio Transcription & Translation App")

st.sidebar.header("Select Audio File")
audio_files = list_s3_audio_files()
selected_file = st.sidebar.selectbox("Choose an audio file", audio_files)

languages = {
    "Original (No Translation)": None,
    "Hindi": "Hindi",
    "Marathi": "Marathi",
    "Japanese": "Japanese",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German"
}
target_language = st.sidebar.selectbox("Select Translation Language", list(languages.keys()))

if selected_file:
    st.write(f"Selected file: **{selected_file}**")
    if st.button("Transcribe & Translate Audio"):
        with st.spinner("Transcribing and translating audio..."):
            try:
                temp_path = os.path.join(tempfile.gettempdir(), f"temp_audio_{os.getpid()}{os.path.splitext(selected_file)[1]}")
                download_s3_file(selected_file, temp_path)
                transcript = transcribe_audio(temp_path)
                st.success("✅ Transcription Complete!")
                st.markdown("### 📝 Original Transcript")
                st.write(transcript)
                if languages[target_language]:
                    translated = translate_text(transcript, languages[target_language])
                    st.markdown(f"### 🌐 {target_language} Translation")
                    st.write(translated)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button("Download Original", transcript, f"{selected_file}_original.txt")
                    with col2:
                        st.download_button(f"Download {target_language}", translated, f"{selected_file}_{target_language}.txt")
                else:
                    st.download_button("Download Transcript", transcript, f"{selected_file}_transcript.txt")
            except Exception as e:
                st.error(f"❌ Error: {e}")

with st.sidebar.expander("ℹ️ How to use"):
    st.write("""
    1. Register or log in.
    2. Select an audio file from S3.
    3. Choose a translation language (optional).
    4. Click 'Transcribe & Translate Audio'.
    5. Download the results.
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ by Krishnat")
