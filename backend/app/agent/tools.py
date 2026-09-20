from datetime import date

from sqlalchemy.orm import Session

from .. import models
from ..services.sales_service import (get_sales_summary,
                                       get_top_products,
                                       get_sales_breakdown)


def sales_summary_tool(
    db: Session,
    current_user: models.User,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    city: str | None = None,
):
    """
    Get aggregated sales statistics for the authenticated user's
    accessible brands.

    Can optionally filter by date range, region, or city.
    """

    return get_sales_summary(
        db=db,
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date,
        region=region,
        city=city,
    )

def top_products_tool(
    db: Session,
    current_user: models.User,
    limit: int = 5,
    start_date: date | None = None,
    end_date: date | None = None,
    region: str | None = None,
    city: str | None = None,
):
    """
    Return the top-selling products within the authenticated user's accessible brands.
    """
    return get_top_products(
        db=db,
        user_id=current_user.user_id,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        region=region,
        city=city,
    )

def sales_breakdown_tool(
    db: Session,
    current_user: models.User,
    group_by: str,
    start_date: date | None = None,
    end_date: date | None = None,
):
    """Return sales grouped by an allowed dimension for the authenticated user's accessible brands."""

    return get_sales_breakdown(
        db=db,
        user_id=current_user.user_id,
        group_by=group_by,
        start_date=start_date,
        end_date=end_date,
    )