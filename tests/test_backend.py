# import pytest
# from unittest.mock import patch, MagicMock

# # Assuming your functions are in a module named 'app'
# from s3_audio_transcribe import authenticate_user, register_user

# @patch('s3_audio_transcribe.get_db_connection')
# @patch('s3_audio_transcribe.bcrypt')
# def test_authenticate_user_success(mock_bcrypt, mock_get_db_connection):
#     # Mock DB and bcrypt
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_cursor.fetchone.return_value = ['hashed_pw']
#     mock_conn.cursor.return_value = mock_cursor
#     mock_get_db_connection.return_value = mock_conn
#     mock_bcrypt.checkpw.return_value = True

#     assert authenticate_user('test@example.com', 'password') is True

# @patch('s3_audio_transcribe.get_db_connection')
# @patch('s3_audio_transcribe.bcrypt')
# def test_authenticate_user_failure(mock_bcrypt, mock_get_db_connection):
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_cursor.fetchone.return_value = None
#     mock_conn.cursor.return_value = mock_cursor
#     mock_get_db_connection.return_value = mock_conn

#     assert authenticate_user('test@example.com', 'password') is False

# @patch('s3_audio_transcibe.get_db_connection')
# @patch('s3_audio_transcibe.bcrypt')
# def test_register_user_success(mock_bcrypt, mock_get_db_connection):
#     mock_bcrypt.hashpw.return_value = b'somehash'
#     mock_bcrypt.gensalt.return_value = b'salt'
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_conn.cursor.return_value = mock_cursor
#     mock_get_db_connection.return_value = mock_conn

#     success, msg = register_user('test@example.com', 'password')
#     assert success is True
#     assert "Registration successful" in msg
