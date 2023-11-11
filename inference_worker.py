import datetime
import os
import time
from database.utils import get_open_orders, make_order_complete
from pipeline.solution import Solution
from database.engine import SessionLocal, engine

inference = Solution()

while True:
    db_session = SessionLocal()
    all_orders = get_open_orders(db_session)
    db_session.close()
    print(all_orders)
    for i in all_orders:
        try:
            os.mkdir(f"./frames/{i.id}/")
        except Exception as er:
            print(er)
        inference.predict_video(i.video_path, f"./frames/{i.id}/", step_frame=4, save_video=True)
        db_session = SessionLocal()
        make_order_complete(db_session, i.id, datetime.datetime.utcnow())
        db_session.close()
    time.sleep(10)
