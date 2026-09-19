from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Brand(Base):
    __tablename__ = "brands"

    brand_id = Column(String(10), primary_key=True)
    brand_name = Column(String(255), nullable=False)
    supplier = Column(String(255), nullable=False)

    products = relationship("Product", back_populates="brand")
    user_access = relationship("UserBrandAccess", back_populates="brand")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(10), primary_key=True)
    product_name = Column(String(255), nullable=False)
    brand_id = Column(String(10), ForeignKey("brands.brand_id"), nullable=False)
    category = Column(String(100), nullable=False)
    unit_price_sek = Column(Integer, nullable=False)

    brand = relationship("Brand", back_populates="products")
    orders = relationship("Order", back_populates="product")


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String(10), primary_key=True)
    store_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)

    orders = relationship("Order", back_populates="store")

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(10), primary_key=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    company = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=True) #TODO: Make this non-nullable later

    brand_access = relationship("UserBrandAccess", back_populates="user")


class UserBrandAccess(Base):
    __tablename__ = "user_brand_access"

    user_id = Column(
        String(10),
        ForeignKey("users.user_id"),
        primary_key=True,
    )

    brand_id = Column(
        String(10),
        ForeignKey("brands.brand_id"),
        primary_key=True,
    )

    user = relationship("User", back_populates="brand_access")
    brand = relationship("Brand", back_populates="user_access")


class Order(Base):
    __tablename__ = "orders"

    order_line_id = Column(String(20), primary_key=True)
    order_id = Column(String(20), nullable=False)
    order_date = Column(Date, nullable=False)

    store_id = Column(
        String(10),
        ForeignKey("stores.store_id"),
        nullable=False,
    )

    product_id = Column(
        String(10),
        ForeignKey("products.product_id"),
        nullable=False,
    )

    quantity = Column(Integer, nullable=False)
    unit_price_sek = Column(Integer, nullable=False)
    line_total_sek = Column(Integer, nullable=False)

    store = relationship("Store", back_populates="orders")
    product = relationship("Product", back_populates="orders")