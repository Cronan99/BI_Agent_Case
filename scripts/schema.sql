CREATE TABLE IF NOT EXISTS brands (
    brand_id VARCHAR(10) PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    supplier VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS stores (
    store_id VARCHAR(10) PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(10) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    company VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    brand_id VARCHAR(10) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price_sek INTEGER NOT NULL,

    FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id)
);

CREATE TABLE IF NOT EXISTS user_brand_access (
    user_id VARCHAR(10) NOT NULL,
    brand_id VARCHAR(10) NOT NULL,

    PRIMARY KEY (user_id, brand_id),

    FOREIGN KEY (user_id)
        REFERENCES users(user_id),

    FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_line_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    order_date DATE NOT NULL,
    store_id VARCHAR(10) NOT NULL,
    product_id VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_sek INTEGER NOT NULL,
    line_total_sek INTEGER NOT NULL,

    FOREIGN KEY (store_id)
        REFERENCES stores(store_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);