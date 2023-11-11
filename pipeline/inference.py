import asyncio
from asyncio import Queue
from solution import predict_video
import random


class Inference:
    def __init__(self, queue_size: int = 1) -> None:
        self.queue = Queue(queue_size)

    async def predict_img(self):
        if self.queue.empty() is not True:
            next_order = self.queue.get_nowait()
            predict_video(next_order.video_path, f"frames//{next_order.id}/")
            return next_order.id
