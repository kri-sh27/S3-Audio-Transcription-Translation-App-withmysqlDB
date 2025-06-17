import streamlit as st
import boto3
import openai
import os
from dotenv import load_dotenv
import tempfile
import mysql.connector
import bcrypt

# Load environment variables
load_dotenv()

# Configure OpenAI and AWS
openai.api_key = os.getenv('OPENAI_API_KEY')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
bucket_name = os.getenv('S3_BUCKET_NAME')

# MySQL config
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# ------------------------- DB FUNCTIONS -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

def authenticate_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return bcrypt.checkpw(password.encode('utf-8'), row[0].encode('utf-8'))
    return False

def register_user(email, password):
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, password_hash))
        conn.commit()
        conn.close()
        return True, "✅ Registration successful! You can now log in."
    except mysql.connector.Error as err:
        return False, f"❌ Error: {err}"

# ------------------------- LOGIN / REGISTER -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Set default view to registration instead of login
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
def list_s3_audio_files():
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    return [obj['Key'] for obj in response.get('Contents', [])
            if obj['Key'].lower().endswith(('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'))]

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            file=audio_file,
            model="whisper-1",
            response_format="text"
        )
    return transcript

def translate_text(text, target_language):
    prompt = f"Translate the following English text to {target_language}:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ------------------------- MAIN UI -------------------------
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
                s3_client.download_file(bucket_name, selected_file, temp_path)

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

# Sidebar usage
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
