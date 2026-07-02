"""
Create the first team login for the dashboard.
Run with: python create_admin.py
"""

import getpass

from werkzeug.security import generate_password_hash

from app import create_app
from app.db import create_user, get_user_by_username


def main():
    create_app()  # ensures the database tables exist

    username = input("Username: ").strip()
    if get_user_by_username(username):
        print(f"'{username}' already exists.")
        return

    password = getpass.getpass("Password (hidden while typing): ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords didn't match, try again.")
        return

    create_user(username, generate_password_hash(password, method="pbkdf2:sha256"))
    print(f"User '{username}' created. Log in at /dashboard/login")


if __name__ == "__main__":
    main()
