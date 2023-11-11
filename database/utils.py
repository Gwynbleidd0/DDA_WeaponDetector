import datetime
from sqlalchemy.orm import Session

from . import models, schemas


def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()


def get_open_orders(db: Session):
    return db.query(models.Order).filter(models.Order.finished_at == None).all()


def make_order_complete(db: Session, order_id: int, datetime: datetime.datetime):
    db.query(models.Order).filter(models.Order.id == order_id).update({"finished_at": datetime})
    db.commit()
    return True


def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(title=order.title, video_path=order.video_path, preview_img=order.preview_img)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
