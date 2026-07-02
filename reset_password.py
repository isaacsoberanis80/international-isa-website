"""
Reset the password for an existing dashboard user.
Run with: python reset_password.py
"""

import getpass

from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_user_by_username
from app.models import db


def main():
    app = create_app()
    with app.app_context():
        username = input("Username to reset: ").strip()
        user = get_user_by_username(username)
        if not user:
            print(f"No user named '{username}' exists. Run create_admin.py instead to create one.")
            return

        password = getpass.getpass("New password (hidden while typing): ")
        confirm = getpass.getpass("Confirm new password: ")
        if password != confirm:
            print("Passwords didn't match, try again.")
            return

        user.password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        db.session.commit()
        print(f"Password for '{username}' updated.")


if __name__ == "__main__":
    main()
