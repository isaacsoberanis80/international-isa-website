"""
Reset the password for an existing dashboard user.
Run with: python reset_password.py
"""

import getpass

from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_user_by_username, get_connection


def set_password(username, password_hash):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (password_hash, username),
    )
    conn.commit()
    conn.close()


def main():
    create_app()

    username = input("Username to reset: ").strip()
    if not get_user_by_username(username):
        print(f"No user named '{username}' exists. Run create_admin.py instead to create one.")
        return

    password = getpass.getpass("New password (hidden while typing): ")
    confirm = getpass.getpass("Confirm new password: ")
    if password != confirm:
        print("Passwords didn't match, try again.")
        return

    set_password(username, generate_password_hash(password, method="pbkdf2:sha256"))
    print(f"Password for '{username}' updated.")


if __name__ == "__main__":
    main()
