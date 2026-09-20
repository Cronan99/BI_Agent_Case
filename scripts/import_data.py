from pathlib import Path

import pandas as pd
from sqlalchemy import text

from backend.app.database import engine


DATA_DIR = Path(__file__).parent.parent / "data"


def table_has_data(table_name: str) -> bool:
    with engine.connect() as connection:
        result = connection.execute(
            text(f"SELECT EXISTS (SELECT 1 FROM {table_name} LIMIT 1)")
        )
        return result.scalar()


def import_csv(filename: str, table_name: str):
    if table_has_data(table_name):
        print(f"Skipping {table_name}: data already exists")
        return

    filepath = DATA_DIR / filename

    print(f"Importing {filename}...")

    df = pd.read_csv(filepath)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
    )

    print(f"Imported {len(df)} rows into {table_name}")


def main():
    import_csv("brands.csv", "brands")
    import_csv("stores.csv", "stores")
    import_csv("users.csv", "users")
    import_csv("products.csv", "products")
    import_csv("user_brand_access.csv", "user_brand_access")
    import_csv("orders.csv", "orders")


if __name__ == "__main__":
    main()