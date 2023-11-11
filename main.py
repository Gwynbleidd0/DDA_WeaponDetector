import os
from typing import Annotated
import uuid
import aiofiles
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import utils, models, schemas
from database.engine import SessionLocal, engine
from utils import get_preview

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/order", response_model=schemas.Order)
async def create_order(title: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    print(title, file)
    uuid_id = uuid.uuid4()
    async with aiofiles.open(f"orders/{uuid_id}.{file.filename.split('.')[-1]}", "wb") as out_file:
        content = await file.read()  # async read
        await out_file.write(content)
    try:
        preview_img = get_preview(f"orders/{uuid_id}.{file.filename.split('.')[-1]}", f"orders/{uuid_id}-preview.png")
    except Exception as er:
        print(er)
    order = schemas.OrderCreate(
        title=title, video_path=f"orders/{uuid_id}.{file.filename.split('.')[-1]}", preview_img=preview_img
    )
    order = utils.create_order(db=db, order=order)
    order_json = schemas.Order.from_orm(order)
    return order


@app.get("/order/{id:int}", response_model=schemas.Order)
def read_orders(id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return utils.get_order(db, order_id=id)


@app.get("/preview/{id:int}")
async def get_item_by_id(id: int, db: Session = Depends(get_db)):
    item = utils.get_order(db, order_id=id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return FileResponse(
        path=item.preview_img,
        filename="preview.png",
        media_type="multipart/form-data",
    )


@app.get("/frames/{id:int}")
async def get_item_by_id(id: int, db: Session = Depends(get_db)):
    return [each for each in os.listdir(f"./frames/{id}") if each.endswith(".png")]


@app.get("/rstp/{name:str}")
async def get_item_by_id(name: str, db: Session = Depends(get_db)):
    return [each for each in os.listdir(f"./rstp/{name}") if each.endswith(".png") and each.index("preview") == -1]


@app.get("/rstp/{name:str}/{img_name:str}")
async def get_item_by_id(name: int, img_name: str, db: Session = Depends(get_db)):
    return FileResponse(
        path=f"./rstp/{name}/{img_name}",
        filename="result.png",
        media_type="multipart/form-data",
    )


@app.get("/frames/{id:int}/{name:str}")
async def get_item_by_id(id: int, name: str, db: Session = Depends(get_db)):
    return FileResponse(
        path=f"./frames/{id}/{name}",
        filename="result.png",
        media_type="multipart/form-data",
    )


@app.get("/result/{id:int}")
async def get_item_by_id(id: int, db: Session = Depends(get_db)):
    results = [each for each in os.listdir(f"./frames/{id}") if each.endswith(".mp4")]
    return FileResponse(
        path=f"./frames/{id}/{results[0]}",
        filename="result.mp4",
        media_type="multipart/form-data",
    )


@app.get("/orders", response_model=list[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = utils.get_orders(db, skip=skip, limit=limit)
    return orders


# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
