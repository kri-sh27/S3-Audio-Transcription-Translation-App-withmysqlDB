import pytest
import bcrypt
from unittest.mock import patch, MagicMock
from backend.auth import authenticate_user, register_user

@pytest.fixture
def mock_db(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr('backend.auth.get_db_connection', lambda: mock_conn)
    return mock_conn, mock_cursor

def test_authenticate_user_success(mock_db):
    mock_conn, mock_cursor = mock_db
    password = "testpassword"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    mock_cursor.fetchone.return_value = (password_hash,)
    assert authenticate_user("test@example.com", password) is True

def test_register_user_duplicate_email(mock_db):
    mock_conn, mock_cursor = mock_db
    from mysql.connector import Error
    def raise_duplicate(*args, **kwargs):
        raise Error("Duplicate entry 'test@example.com' for key 'users.email'")
    mock_cursor.execute.side_effect = raise_duplicate
    success, msg = register_user("test@example.com", "password123")
    assert not success
    assert "Duplicate entry" in msg
