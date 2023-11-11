import json
import os

from pipeline.solution import Solution

solution = Solution()

with open("rstp_config.json", "r", encoding="utf8") as f:
    rstp_config = json.load(f)

for i in rstp_config.items():
    try:
        os.makedirs(f"./rstp/{i[0]}")
    except Exception as er:
        print(er)
    print(i[1]["rstpLink"])
    solution.predict_video(i[1]["rstpLink"], f"./rstp/{i[0]}/", step_frame=5)
    print(i)
