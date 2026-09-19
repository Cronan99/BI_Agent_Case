import time

from backend.app.database import SessionLocal
from backend.app.models import User
from backend.app.agent.agent import ask_agent


def main():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.user_id == "U02")
            .first()
        )

        print(f"Testing as: {user.full_name}")

        start = time.perf_counter()

        answer = ask_agent(
            "Hur mycket sålde vi i Stockholm under januari 2025?",
            db,
            user,
        )

        print(
            f"Agent completed in "
            f"{time.perf_counter() - start:.2f}s"
        )

        print("\nAnswer:")
        print(answer)

    finally:
        db.close()


if __name__ == "__main__":
    main()