from sqlalchemy.orm import Session

from .. import models

def get_user_brand_ids(db: Session, user_id: str) -> list[str]:

    results = (
        db.query(models.UserBrandAccess.brand_id)
        .filter(models.UserBrandAccess.user_id == user_id)
        .all()
    )

    return [brand_id for (brand_id,) in results]
