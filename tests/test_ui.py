# from streamlit.testing.v1 import AppTest

# def test_register_and_login_flow():
#     at = AppTest.from_file("s3_audio_transcribe.py").run()
#     # Simulate registration
#     at.text_input[0].input("test@example.com").run()
#     at.text_input[1].input("password123").run()
#     at.text_input[2].input("password123").run()
#     at.form_submit_button[0].click().run()
#     assert "Registration successful" in at.success[0].value

#     # Switch to login view and simulate login
#     at.button[0].click().run()  # "Go to Login"
#     at.text_input[0].input("test@example.com").run()
#     at.text_input[1].input("password123").run()
#     at.form_submit_button[0].click().run()
#     assert "Login successful" in at.success[0].value
