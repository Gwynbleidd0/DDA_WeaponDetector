from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
import datetime
from database.engine import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(Text, index=True)
    video_path = Column(Text, index=True)
    preview_img = Column(Text, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    finished_at = Column(DateTime, index=True)
    processed_frames = Column(Integer, default=0, index=True)


class Frame(Base):
    __tablename__ = "frames"
    id = Column(String, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    has_detection = Column(Boolean, default=False, index=True)
    path_to_frame = Column(Text, index=True)
