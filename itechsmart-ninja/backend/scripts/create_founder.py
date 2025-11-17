#!/usr/bin/env python3
"""
Create Founder Account Script
This script creates the founder account for iTechSmart Ninja
"""

import sys
import os
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_founder_account():
    """Create the founder account"""

    print("🎯 iTechSmart Ninja - Founder Account Creation")
    print("=" * 50)
    print()

    # Get founder details
    email = input("Enter your email (default: founder@itechsmart.dev): ").strip()
    if not email:
        email = "founder@itechsmart.dev"

    username = input("Enter your username (default: founder): ").strip()
    if not username:
        username = "founder"

    full_name = input("Enter your full name (default: iTechSmart Founder): ").strip()
    if not full_name:
        full_name = "iTechSmart Founder"

    # Get password securely
    while True:
        password = getpass("Enter your password: ")
        password_confirm = getpass("Confirm your password: ")

        if password != password_confirm:
            print("❌ Passwords don't match. Try again.")
            continue

        if len(password) < 8:
            print("❌ Password must be at least 8 characters. Try again.")
            continue

        break

    print()
    print("Creating founder account...")

    # Create database session
    db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = (
            db.query(User)
            .filter((User.email == email) | (User.username == username))
            .first()
        )

        if existing_user:
            print(
                f"❌ User with email '{email}' or username '{username}' already exists!"
            )
            print(
                "   Use a different email/username or delete the existing user first."
            )
            return False

        # Create founder user
        founder = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
            role="founder",
        )

        db.add(founder)
        db.commit()
        db.refresh(founder)

        print()
        print("✅ Founder account created successfully!")
        print()
        print("Account Details:")
        print(f"   Email:    {email}")
        print(f"   Username: {username}")
        print(f"   Name:     {full_name}")
        print(f"   Role:     Founder (Superuser)")
        print()
        print("🎉 You can now login at http://localhost:3000")
        print()

        return True

    except Exception as e:
        print(f"❌ Error creating founder account: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def reset_founder_password():
    """Reset founder password"""

    print("🔐 iTechSmart Ninja - Reset Founder Password")
    print("=" * 50)
    print()

    email = input("Enter founder email: ").strip()

    # Get new password securely
    while True:
        password = getpass("Enter new password: ")
        password_confirm = getpass("Confirm new password: ")

        if password != password_confirm:
            print("❌ Passwords don't match. Try again.")
            continue

        if len(password) < 8:
            print("❌ Password must be at least 8 characters. Try again.")
            continue

        break

    print()
    print("Resetting password...")

    # Create database session
    db = SessionLocal()

    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print(f"❌ User with email '{email}' not found!")
            return False

        # Update password
        user.hashed_password = get_password_hash(password)
        db.commit()

        print()
        print("✅ Password reset successfully!")
        print(f"   Email: {email}")
        print()
        print("🎉 You can now login with your new password")
        print()

        return True

    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def main():
    """Main function"""

    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_founder_password()
    else:
        create_founder_account()


if __name__ == "__main__":
    main()
