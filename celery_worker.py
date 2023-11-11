import sys

# print(sys.path)
# sys.path.append("D:\\anaconda3\\envs\\openmmlab\\Lib\\site-packages")
# print(sys.path)
from celery import Celery
from pipeline.solution import Solution

app = Celery("tasks", broker="redis://localhost:6379")
solution = None


@app.task
def predict_task(video_path, output_path):
    solution.predict_video(video_path, output_path)
    return True


@app.task
def prepared_task():
    global solution
    solution = Solution()
    return True
