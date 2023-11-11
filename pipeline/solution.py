from pipeline.models import People_detector, ResNet, Mask_Rcnn
import torch
import cv2
import numpy as np
import os
import time
import uuid


class Solution:
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.people_detect = People_detector("./pipeline/yolo/yolov5m.pt", device=self.device)
        self.weapon_segmentor = Mask_Rcnn(
            "./pipeline/mask_rcnn/Weapon.py", "./pipeline/mask_rcnn/weapon_segm_v3.pth", device=self.device
        )
        self.garment_classifier = ResNet(
            "./pipeline/classifier/garment_V2.pt",
            ["armored", "normal"],
            device=self.device,
        )
        self.pose_classifier = ResNet("./pipeline/classifier/pose_V2.pt", ["normal", "shooting"], device=self.device)
        self.weapon_classifier = ResNet(
            "./pipeline/classifier/weapon_V3.pt", ["no weapon", "weapon"], device=self.device
        )

        self.DETECT_PEOPLE_THR = 0.5
        self.DETECT_WEAPON_THR = 0.8

        # Веса во взвешеном голосовании
        self.WEIGHTS_GARMENT = 0.20
        self.WEIGHTS_POSE = 0.15
        self.WEIGHTS_WEAPON_CLS = 0.3
        self.WEIGHTS_SEG = 0.35

        # Порог, выше которого оружие есть
        self.WEAPON_THR = 0.62

    def inference_img(
        self,
        frame: np.ndarray,
        id_frame=None,
        total_people=None,
        total_shooters=None,
        total_time=None,
    ):
        num_shooters = 0
        summarize_conf = 0
        list_confidence_shooters = []
        use_segmentator = False
        # Inference people detector
        time_start = time.perf_counter()
        results = self.people_detect.predict(frame, threshold=self.DETECT_PEOPLE_THR)
        num_people = len(results)
        if num_people <= 2:
            use_segmentator = True
        # print(results)
        for instance in results:
            x1, y1, x2, y2, _, _ = instance
            crop = frame[int(y1) : int(y2), int(x1) : int(x2)]
            class_crop = "No weapon"

            # inference all model
            start_classifier = time.perf_counter()
            # crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            garment_label, garment_confidence = self.garment_classifier.predict(crop)
            pose_label, pose_confidence = self.pose_classifier.predict(crop)
            weapon_label, weapon_confidence = self.weapon_classifier.predict(crop)
            # crop = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
            # print(garment_label, garment_confidence)
            garment_confidence = garment_confidence[0].cpu().numpy()
            pose_confidence = pose_confidence[1].cpu().numpy()
            weapon_confidence = weapon_confidence[1].cpu().numpy()
            # print(f"classifier in: {(time.perf_counter()-start_classifier) *1000:.2f} ms")
            # запуск сегментации только если есть 2 косвенных признака, или обнаружено оружие
            if garment_label == "armored" and pose_label == "shooting" or weapon_label == "weapon" or use_segmentator:
                use_segmentator = True
                detected_weapon_list = self.weapon_segmentor.predict(crop, score_thr=self.DETECT_WEAPON_THR, show=False)
                # get confidence of weapon segmentator
                seg_confidence = (
                    np.array([weapon["confidence"] for weapon in detected_weapon_list]).mean()
                    if len(detected_weapon_list) != 0
                    else 0
                )

                # if seg_confidence is np.nan:
                #     seg_confidence = 0

            # calculate smmarized weapon confidence
            # вероятность наличия оружия
            summarize_conf = (
                garment_confidence * self.WEIGHTS_GARMENT
                + pose_confidence * self.WEIGHTS_POSE
                + weapon_confidence * self.WEIGHTS_WEAPON_CLS
            )
            if use_segmentator:
                summarize_conf += seg_confidence * self.WEIGHTS_SEG

            # print(garment_label, pose_label, weapon_label)
            # print(
            #     garment_confidence * WEIGHTS_GARMENT,
            #     pose_confidence * WEIGHTS_POSE,
            #     weapon_confidence * WEIGHTS_WEAPON_CLS,
            #     # seg_confidence * WEIGHTS_SEG,
            # )
            # print(summarize_conf)
            if summarize_conf >= self.WEAPON_THR:
                class_crop = "Weapon"
                num_shooters += 1
                list_confidence_shooters.append(summarize_conf)

            if class_crop == "Weapon" or False:
                # draw bbox of human
                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), [0, 255, 255], 2)
                # draw text of confidence
                cv2.putText(
                    frame,
                    f"Weapon: {summarize_conf*100:.0f}%",
                    (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1,
                    [255, 0, 0],
                    4,
                )
                cv2.putText(
                    frame,
                    f"{self.garment_classifier.classes[0]}: {garment_confidence*100:.0f}%",
                    (int(x1), int(y1) + 20),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.5,
                    [0, 0, 255],
                    2,
                )
                cv2.putText(
                    frame,
                    f"{self.pose_classifier.classes[1]}: {pose_confidence*100:.0f}%",
                    (int(x1), int(y1) + 40),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.5,
                    [0, 255, 0],
                    2,
                )
                cv2.putText(
                    frame,
                    f"{self.weapon_classifier.classes[1]}: {weapon_confidence*100:.0f}%",
                    (int(x1), int(y1) + 60),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.5,
                    [255, 127, 0],
                    2,
                )

                # draw weapon contour and bboxes
                if use_segmentator:
                    for instace_weapon in detected_weapon_list:
                        weapon_bbox = instace_weapon["bbox"]
                        confidence_weapon = instace_weapon["confidence"]
                        weapon_x1, weapon_y1, weapon_x2, weapon_y2 = weapon_bbox
                        weapon_x1 += int(x1)
                        weapon_y1 += int(y1)
                        weapon_x2 += int(x1)
                        weapon_y2 += int(y1)
                        cx, xy = int((weapon_x1 + weapon_x2) // 2), int((weapon_y1 + weapon_y2) // 2)

                        weapon_polygons = instace_weapon["contoure"]
                        for polygon in weapon_polygons:
                            # print(polygon)
                            new_weapon_polygons = np.asarray(polygon, dtype=np.int32).reshape(-1, 1, 2)
                            new_weapon_polygons[:, :, 0] += int(x1)
                            new_weapon_polygons[:, :, 1] += int(y1)

                        frame = cv2.drawContours(frame, new_weapon_polygons, -1, (0, 124, 255), 2)
                        frame = cv2.rectangle(
                            frame,
                            (int(weapon_x1), int(weapon_y1)),
                            (int(weapon_x2), int(weapon_y2)),
                            [255, 0, 0],
                            1,
                        )

                        cv2.putText(
                            frame,
                            f"{confidence_weapon*100:.0f}%",
                            (cx, xy),
                            cv2.FONT_HERSHEY_DUPLEX,
                            0.5,
                            [255, 127, 0],
                            1,
                        )
        time_proc = time.perf_counter() - time_start
        total_shooters = total_shooters + num_shooters if not total_shooters is None else None
        total_people = total_people + num_people if not total_people is None else None
        total_time = total_time + time_proc if not total_time is None else None
        list_num = [total_people, total_shooters, total_time, id_frame]
        strings_num = ["people, ", "shooters, ", "time (s), ", "frames"]
        if len(list_confidence_shooters) == 0:
            list_confidence_shooters.append(0)
        output_str = f"{num_people:>3} people, {num_shooters} shooters, {time_proc*1000 :>7.2f} ms, conf: {np.array(list_confidence_shooters).mean():.2f} | "
        output_str += (
            "total: "
            if not list_num[0] is None or not list_num[1] is None or not list_num[2] is None or not list_num[3] is None
            else ""
        )
        for num, string in zip(list_num, strings_num):
            if not num is None:
                output_str += f"{int(num):>7} {string}"
        print(output_str)
        return num_shooters, frame, total_people, total_shooters, total_time

    def save_img(self, path_save_img, frame):
        os.makedirs(path_save_img, exist_ok=True)
        name = f"{uuid.uuid4()}.png"
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(f"{path_save_img}/{name}", frame)

    def save_img_from_video(self, path_save_img, frame, path_video, id_frame):
        os.makedirs(path_save_img, exist_ok=True)
        name = os.path.basename(path_video) + f"_{id_frame}.png"
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(f"{path_save_img}/{name}", frame)

    def is_rtsp(self, path):
        if not os.path.isfile(path) and "rtsp" in path:
            return True
        else:
            return False

    def predict_img(self, frame: np.ndarray or str, path_save_img: str = None, show: bool = False):
        if isinstance(frame, str):
            frame = cv2.imread(frame)
        num_shooters, frame, total_people, total_shooters = self.inference_img(frame)
        if num_shooters >= 1:
            self.save_img(path_save_img, frame)
        if show:
            cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
            cv2.imshow("frame", frame)
            cv2.waitKey(0)
        # show results

    def predict_video(
        self,
        path_video: str,
        path_save_img: str = None,
        show: bool = False,
        save_video: bool = False,
        step_frame: int = 1,
        total_time_start=0,
        total_people_start=0,
        total_shooters_start=0,
        total_frames_start=0,
    ):
        # Цикл обработки кадров видео
        cap = cv2.VideoCapture(path_video)
        num_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        id_frame = total_frames_start
        total_people, total_shooters, total_time = (
            total_people_start,
            total_shooters_start,
            total_time_start,
        )
        start_time = time.perf_counter()
        is_stream = self.is_rtsp(path_video)
        path_video = f"Stream_{uuid.uuid4()}" if is_stream else path_video
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            fps = cap.get(cv2.CAP_PROP_FPS) // step_frame
            width = int(cap.get(3))  # float `width`
            height = int(cap.get(4))  # float `height`
            video_size = (width, height)
            name = "out_" + os.path.basename(path_video) + ".mp4"
            vid = cv2.VideoWriter(f"{path_save_img}/{name}", fourcc, fps, video_size)
        while cap.isOpened():
            id_frame += 1
            # Read a frame from the video
            success, frame = cap.read()
            if not success:
                break
            if id_frame % step_frame != 0:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            num_shooters, frame, total_people, total_shooters, total_time = self.inference_img(
                frame, id_frame / step_frame, total_people, total_shooters, total_time
            )
            if num_shooters >= 1:
                self.save_img_from_video(path_save_img, frame, path_video, id_frame)
            if show or save_video:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                if show or is_stream:
                    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
                    cv2.imshow("frame", frame)
                    key = cv2.waitKey(1)
                    if (key == ord("q")) or key == 27:
                        vid.release() if save_video else None
                        break
                if save_video:
                    vid.write((frame))
        cap.release()
        cv2.destroyAllWindows()
        if save_video:
            vid.release()
        print(
            f"total time process: {(time.perf_counter() - start_time)/60:.2f}m, total time inf: {total_time/60:.2f} m, total people: {total_people}, total shooters: {total_shooters}"
        )
        return total_time, total_people, total_shooters, id_frame


if __name__ == "__main__":
    # path_vid = "D:/Project/Hackaton/LCT_Krasnodar/data/train/no_weapon/74.Шевченко 286 (Двор) 2023-09-27 10-37-00_000+0300 [10m1s].mp4"
    # path_vid = "D:/Project/Hackaton/LCT_Krasnodar/data/yt/В Ярославле камеры наблюдения зафиксировали мужчину, открывшего стрельбу в подъезде.mp4"
    path_vid = (
        "rtsp://admin:A1234567@188.170.176.190:8031/Streaming/Channels/101?transportmode=unicast&profile=Profile_1"
    )
    solution = Solution()
    solution.predict_video(
        path_vid,
        path_save_img="../data/out",
        show=False,
        save_video=True,
        step_frame=7,
    )

# 183 v1

#
