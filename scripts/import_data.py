from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


DATA_DIR = Path(__file__).parent.parent / "data"

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/solvigo"

engine = create_engine(DATABASE_URL)


def import_csv(filename: str, table_name: str):
    filepath = DATA_DIR / filename

    print(f"Importing {filename}...")

    df = pd.read_csv(filepath)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
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