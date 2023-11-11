import asyncio
import os
from typing import Annotated
import uuid
import aiofiles
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database.schemas import Order
from pipeline.solution import predict_video


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict")
async def predict_order(order: Order):
    loop = asyncio.get_event_loop()
    os.mkdir(f"./frames/{order.id}/")
    result = await loop.create_task(predict_video(order.video_path, f"./frames/{order.id}/"))
    return result
