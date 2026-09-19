from backend.app.database import SessionLocal
from backend.app.models import User
from backend.app.services.auth_service import hash_password


DEMO_PASSWORD = "demo123"


def main():
    db = SessionLocal()

    try:
        users = db.query(User).all()

        for user in users:
            user.password_hash = hash_password(DEMO_PASSWORD)

        db.commit()

        print(f"Set demo password for {len(users)} users.")

    finally:
        db.close()


if __name__ == "__main__":
    main()