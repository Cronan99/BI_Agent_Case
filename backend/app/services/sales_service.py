from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from .access_service import get_user_brand_ids


def get_sales_summary(
        db: Session,
        user_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        region: str | None = None,
        city: str | None = None,
        ):

    brand_ids = get_user_brand_ids(db, user_id)

    if not brand_ids:
        return {
            "revenue": 0,
            "orders": 0,
            "products": 0,
        }

    query = (
        db.query(
            func.sum(models.Order.line_total_sek).label("revenue_sek"),
            func.sum(models.Order.quantity).label("units_sold"),
            func.count(func.distinct(models.Order.order_id)).label("orders"),
        )
        .join(
            models.Product,
            models.Order.product_id == models.Product.product_id,
        )
        .join(
            models.Store,
            models.Order.store_id == models.Store.store_id,
        )
        .filter(models.Product.brand_id.in_(brand_ids))
    )

    if start_date:
        query = query.filter(models.Order.order_date >= start_date)

    if end_date:
        query = query.filter(models.Order.order_date <= end_date)

    if region:
        query = query.filter(models.Store.region == region)

    if city:
        query = query.filter(models.Store.city == city)

    result = query.first()

    return {
        "revenue_sek": result.revenue_sek or 0,
        "units_sold": result.units_sold or 0,
        "orders": result.orders or 0,
    }


def get_top_products(
    db: Session,
    user_id: str,
    limit: int = 5,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    city: str | None = None,
):
    brand_ids = get_user_brand_ids(db, user_id)

    if not brand_ids:
        return []

    query = (
        db.query(
            models.Product.product_id,
            models.Product.product_name,
            func.sum(models.Order.line_total_sek).label("revenue_sek"),
            func.sum(models.Order.quantity).label("units_sold"),
        )
        .join(models.Product, models.Order.product_id == models.Product.product_id)
        .join(models.Store, models.Order.store_id == models.Store.store_id)
        .filter(models.Product.brand_id.in_(brand_ids))
    )

    if start_date:
        query = query.filter(models.Order.order_date >= start_date)

    if end_date:
        query = query.filter(models.Order.order_date <= end_date)

    if region:
        query = query.filter(models.Store.region == region)

    if city:
        query = query.filter(models.Store.city == city)

    results = (
        query
        .group_by(
            models.Product.product_id,
            models.Product.product_name,
        )
        .order_by(
            func.sum(models.Order.line_total_sek).desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "revenue_sek": row.revenue_sek,
            "units_sold": row.units_sold,
        }
        for row in results
    ]