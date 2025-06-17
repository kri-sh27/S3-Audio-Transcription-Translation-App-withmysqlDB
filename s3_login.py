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

# MySQL config
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

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

if "view" not in st.session_state:
    st.session_state.view = "register"  # default view

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
                st.session_state.view = "home"  # Redirect to hello world page
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

# ------------------------- HELLO WORLD PAGE -------------------------
if st.session_state.view == "home":
    st.title("👋 Hello World")
    st.write("Welcome! You are now logged in.")
    st.stop()