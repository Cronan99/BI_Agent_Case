from sqlaclhemy import func
from sqlalchemy.orm import Session

from .. import models
from .access_service import get_user_brand_ids


def get_sales_summary(db: Session, user_id: str):

    brand_ids = get_user_brand_ids(db, user_id)

    if not brand_ids:
        return {
            "revenue": 0,
            "orders": 0,
            "products": 0,
        }

    result = (
        db.query(
            func.sum(models.Order.line_total_sek)
            func.sum(models.Order.quantity),
            func.count(models.Order.order_line_id),
        )
        .join(
            models.Product,
            models.Order.product_id == models.Product.product_id,
        )
        .filter(models.Product.brand_id.in(brand_ids))
        .first()
    )

    return {
        "revenue": result[0] or 0,
        "products": result[1] or 0,
        "orders": result[2] or 0,
    }