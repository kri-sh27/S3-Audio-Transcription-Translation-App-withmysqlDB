import streamlit as st
import os
import tempfile
import speech_recognition as sr
import openai
import boto3
from datetime import datetime
from backend.auth import authenticate_user, register_user
from backend.s3_utils import list_s3_audio_files, download_s3_file, upload_to_s3
from backend.openai_utils import transcribe_audio, translate_text

# ------------------------- CONFIGURATION -------------------------

if not os.path.exists("temp_files"):
    os.makedirs("temp_files")
# Initialize S3 client (make sure your AWS credentials are configured)
s3_client = boto3.client('s3')
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")  # Replace with your bucket name

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Replace with your actual key

# ------------------------- AUTHENTICATION -------------------------
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
                st.session_state.email = email  # Store user email
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

# ------------------------- MAIN APPLICATION -------------------------
st.title("🎙️ Audio Transcription & Translation App")

# Cleanup function to remove temp files
def cleanup_temp_files():
    for filename in os.listdir("temp_files"):
        file_path = os.path.join("temp_files", filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.error(f"Error deleting {file_path}: {e}")

# Sidebar navigation
app_mode = st.sidebar.radio("Navigation", ["View Files", "Create New Recording","Upload Custom File"])

if app_mode == "View Files":
    # ------------------------- FILE VIEWING AND PROCESSING -------------------------
    st.header("📁 Your Audio Files")
    
    # List files from S3
    audio_files = list_s3_audio_files(S3_BUCKET_NAME)
    selected_file = st.selectbox("Choose an audio file", audio_files)
    
    languages = {
        "Original (No Translation)": None,
        "Hindi": "Hindi",
        "Marathi": "Marathi",
        "Japanese": "Japanese",
        "Spanish": "Spanish",
        "French": "French",
        "German": "German"
    }
    target_language = st.selectbox("Select Translation Language", list(languages.keys()))
    
    if selected_file:
        st.write(f"Selected file: **{selected_file}**")
        if st.button("Transcribe & Translate Audio"):
            with st.spinner("Processing audio..."):
                try:
                    # Download and process file
                    # temp_path = os.path.join(tempfile.gettempdir(), f"temp_audio_{os.getpid()}{os.path.splitext(selected_file)[1]}")
                    # Create temp file in current directory
                    # temp_path = os.path.join("temp_files", f"temp_audio_{os.path.splitext(selected_file)[0]}{os.path.splitext(selected_file)[1]}")
                    # download_s3_file(S3_BUCKET_NAME, selected_file, temp_path)
                    safe_filename = os.path.basename(selected_file).replace("/", "_")
                    temp_path = os.path.join("temp_files", f"temp_{safe_filename}")
                    
                    # Ensure temp_files directory exists
                    os.makedirs("temp_files", exist_ok=True)
                    
                    # Download and process file
                    download_s3_file(S3_BUCKET_NAME, selected_file, temp_path)
                    
                    # Verify file was downloaded
                    if not os.path.exists(temp_path):
                        st.error("Failed to download file from S3")
                        raise FileNotFoundError(f"Could not find downloaded file at {temp_path}")


                    # Transcribe audio
                    transcript = transcribe_audio(temp_path)
                    st.success("✅ Transcription Complete!")
                    st.markdown("### 📝 Original Transcript")
                    st.write(transcript)
                    
                    # Translate if requested
                    if languages[target_language]:
                        translated = translate_text(transcript, languages[target_language])
                        st.markdown(f"### 🌐 {target_language} Translation")
                        st.write(translated)
                        
                        # Download buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button("Download Original", transcript, f"{selected_file}_original.txt")
                        with col2:
                            st.download_button(f"Download {target_language}", translated, f"{selected_file}_{target_language}.txt")
                    else:
                        st.download_button("Download Transcript", transcript, f"{selected_file}_transcript.txt")
                    
                    # Clean up
                    # os.unlink(temp_path)
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        os.unlink(temp_path)

elif app_mode == "Create New Recording":
    # ------------------------- AUDIO RECORDING AND UPLOAD -------------------------
    st.header("🎤 Create New Recording")
    
    # Button to start recording
    if st.button("🎙️ Start Recording"):
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            st.info("Listening... Please speak into your mic.")
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=30)
            st.success("Recording complete!")
            
            try:
                # Save recording to temporary file
                # print("inside try block")
                # with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                #     print("iinside with")
                #     tmpfile.write(audio_data.get_wav_data())
                #     tmpfile_path = tmpfile.name
                #     print("printing tmpeil path", tmpfile_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_filename = os.path.join("temp_files", f"recording_{timestamp}.wav")
                
                with open(temp_filename, "wb") as f:
                    f.write(audio_data.get_wav_data())
                # Display audio player
                st.audio(temp_filename, format="audio/wav")
                st.session_state.latest_recording = temp_filename
            except Exception as e:
                st.error(f"⚠️ Error during recording: {e}")
                if 'temp_filename' in locals() and os.path.exists(temp_filename):
                    os.unlink(temp_filename) 
    if 'latest_recording' in st.session_state and os.path.exists(st.session_state.latest_recording): 
                # Option to upload to S3
                # if st.button("📤 Upload to S3"):
                #     # Generate unique filename
                #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                #     username = st.session_state.email.split("@")[0]  # Use part of email as identifier
                #     s3_filename = f"recordings/{username}/{timestamp}.wav"
                #     print("filename is ",s3_filename)
                    
                #     # Upload to S3
                #     with st.spinner("Uploading to S3..."):
                #         upload_to_s3(S3_BUCKET_NAME, tmpfile_path, s3_filename)
                #         st.success(f"✅ File uploaded successfully as {s3_filename}")
                # In your recording code:
                # 
                

                 # Upload to S3
        print("before upload click")
        if st.button("📤 Upload to S3"):
            try:
                with st.spinner("Uploading to S3..."):
                    # Get the latest recording path
                    temp_filename = st.session_state.latest_recording
                    
                    # Verify file exists and has content
                    if not os.path.exists(temp_filename):
                        st.error("File not found. Please record again.")
                        # return
                    
                    elif os.path.getsize(temp_filename) == 0:
                        st.error("Recording file is empty. Please record again.")
                        # return
                    else:
                    # Upload to S3
                        success, s3_key = upload_to_s3(
                            bucket_name=S3_BUCKET_NAME,
                            local_path=temp_filename,
                            user_email=st.session_state.email
                        )
                        if success:
                            st.success(f"✅ File uploaded successfully to {s3_key}")
                        # Clean up
                            os.unlink(temp_filename)
                            del st.session_state.latest_recording
                        else:
                            st.error(f"❌ Upload failed: {s3_key}")
                        
            except Exception as e:
                st.error(f"⚠️ Error during upload: {e}")
                if 'temp_filename' in locals() and os.path.exists(temp_filename):
                    os.unlink(temp_filename)



                # if st.button("📤 Upload to S3"):
                #     print("s3 upload button clicked")
                #     username = st.session_state.email.split("@")[0]
                #     print("Username name is")
                #     # s3_filename = f"recordings/{username}/recording_{timestamp}.wav"
                #     s3_filename = f"recordings/{username}/recording_{timestamp}.wav"
                    
                #     with st.spinner("Uploading to S3..."):
                #         success, result = upload_to_s3(
                #             bucket_name=S3_BUCKET_NAME,
                #             local_path=temp_filename,
                #             s3_key=s3_filename
                #         )
                        
                #         if success:
                #             st.success(f"✅ File uploaded successfully as {s3_filename}")
                #             os.unlink(temp_filename)
                #         else:
                #             st.error(f"❌ Upload failed: {result}")
                # In your recording code:
            #     if st.button("📤 Upload to S3"):
            #         print("inside if")
            #         with st.spinner("Uploading to S3..."):
            #             print("inside with")
            #             success, s3_key = upload_to_s3(
            #                 bucket_name=S3_BUCKET_NAME,
            #                 local_path=temp_filename,
            #                 user_email=st.session_state.email
            #             )
            #             print("before success")
            #             if success:
            #                 st.success(f"✅ File uploaded successfully to {s3_key}")
            #                 # Optionally delete the local file after upload
            #                 os.unlink(temp_filename)
            #             else:
            #                 st.error(f"❌ Upload failed: {s3_key}")  # s3_key contains error message here
            #     # except Exception as e:
            #         # st.error(f"⚠️ Error: {e}")
            #         # Clean up
            #     # os.unlink(tmpfile_path)
                    
            # except Exception as e:
            #     st.error(f"⚠️ Error: {e}")
            #     if 'temp_filename' in locals() and os.path.exists(temp_filename):
            #         os.unlink(temp_filename)

elif app_mode == "Upload Custom File":
    st.header("📤 Upload Custom File")
    
    uploaded_file = st.file_uploader("Choose an audio file to upload", 
                                   type=['wav', 'mp3', 'ogg', 'm4a'])  # Restrict to audio formats
    
    if uploaded_file is not None:
        # Create temp file with proper extension
        file_ext = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_path = tmp_file.name
        
        try:
            # Use your existing upload_to_s3 function
            success, s3_key = upload_to_s3(
                bucket_name=S3_BUCKET_NAME,
                local_path=temp_path,
                user_email=st.session_state.email if 'email' in st.session_state else None
            )
            
            if success:
                st.success(f"✅ File uploaded successfully to: {s3_key}")
                st.audio(temp_path)  # Preview the uploaded audio
            else:
                st.error(f"❌ Upload failed: {s3_key}")
                
        except Exception as e:
            st.error(f"⚠️ Error during upload: {str(e)}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

# ------------------------- SIDEBAR FOOTER -------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ by [Your Name]")