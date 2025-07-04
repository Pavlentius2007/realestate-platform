from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.user import User
from sqlalchemy import func
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users")
def user_stats(db: Session = Depends(get_db)):
    days_back = 7
    date_from = datetime.utcnow() - timedelta(days=days_back)

    by_date = (
        db.query(func.date(User.created_at), func.count())
        .filter(User.created_at >= date_from)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )

    by_source = (
        db.query(User.source, func.count())
        .group_by(User.source)
        .all()
    )

    return {
        "by_date": {str(date): count for date, count in by_date},
        "by_source": {source or "Не указано": count for source, count in by_source}
    }
