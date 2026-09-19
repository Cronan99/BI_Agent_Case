import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")

files = [
    "orders.csv",
    "products.csv",
    "brands.csv",
    "stores.csv",
    "users.csv",
    "user_brand_access.csv",
]

for filename in files:
    df = pd.read_csv(DATA_DIR / filename)

    print(f"\n--- {filename} ---")
    print(df.dtypes)
    print(df.head())