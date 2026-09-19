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
            func.count(models.Order.order_line_id).label("order_lines"),
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
        "revenue": result.revenue_sek or 0,
        "products": result.units_sold or 0,
        "orders": result.order_lines or 0,
    }