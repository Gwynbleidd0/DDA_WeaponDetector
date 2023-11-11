import datetime
from typing import Union, Optional

from pydantic import BaseModel


class FrameCreate(BaseModel):
    id: int
    has_detection: bool
    path_to_frame: str


class Frame(FrameCreate):
    order_id: int

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    title: str


class OrderCreate(OrderBase):
    video_path: str
    preview_img: str


class Order(OrderCreate):
    id: int
    created_at: datetime.datetime
    finished_at: Optional[datetime.datetime]
    processed_frames: int

    class Config:
        orm_mode = True
