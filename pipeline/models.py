import torch
from torchvision import transforms
import numpy as np

from typing import List

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results
import mmcv
from mmcv.runner import load_checkpoint
from mmdet.apis import inference_detector
from mmdet.models import build_detector
import cv2


class People_detector:
    def __init__(self, model_weights: str, device="cuda:0", classes="person") -> None:
        self.classes = classes
        self.device = device
        self.model = YOLO(model_weights).to(self.device)

    def select(self, result: List[Results], threshold: float) -> List[List[float]]:
        selected_out = []
        for detects in result:
            names = detects.names
            for instance in detects.boxes.data.tolist():
                confidence, class_id = instance[4], instance[5]
                # print(names[class_id], class_id)
                # x1, y1, x2, y2, confidence, class_id = instance
                if names[class_id] != self.classes or confidence < threshold:
                    continue
                selected_out.append(instance)
        return selected_out

    def predict(self, img: np.ndarray, threshold: float = 0.0):
        result = self.model.predict(img, verbose=False)
        selected = self.select(result, threshold)
        return selected


class ResNet:
    def __init__(self, model_weights, classes, device="cuda:0") -> None:
        self.classes = classes
        self.device = device
        self.transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Resize(224),
                transforms.CenterCrop(224),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
            # [0.485, 0.456, 0.406] - [0.406, 0.456, 0.485]
            # [0.229, 0.224, 0.225] - [0.225, 0.224, 0.229]
            # rgb - bgr
        )
        self.model = torch.load(model_weights, map_location=device).eval()

    def predict(self, img: np.ndarray):
        with torch.no_grad():
            input = (self.transform(img).unsqueeze(0)).to(self.device)
            out = self.model(input)
            label = self.classes[out[0].argmax(0).item()]
            # normalize confidence
            # print(torch.softmax(out[0], 0))
            confidence = torch.softmax(out[0], 0)
            # print(confidence)
            # print(out[0], out[0].max(), confidence)

        return label, confidence


class Mask_Rcnn:
    def __init__(self, config, model_weights, device="cuda:0") -> None:
        self.config = config
        self.model_weights = model_weights
        self.device = device
        self.model = self.load_model(self.config, self.model_weights, self.device)

    def mask_to_polygons(self, mask):
        # cv2.RETR_CCOMP flag retrieves all the contours and arranges them to a 2-level
        # hierarchy. External contours (boundary) of the object are placed in hierarchy-1.
        # Internal contours (holes) are placed in hierarchy-2.
        # cv2.CHAIN_APPROX_NONE flag gets vertices of polygons from contours.
        mask = np.ascontiguousarray(
            mask
        )  # some versions of cv2 does not support incontiguous arr
        res = cv2.findContours(
            mask.astype("uint8"), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE
        )
        hierarchy = res[-1]
        if hierarchy is None:  # empty mask
            return [], False
        has_holes = (hierarchy.reshape(-1, 4)[:, 3] >= 0).sum() > 0
        res = res[-2]
        res = [x.flatten() for x in res]
        # These coordinates from OpenCV are integers in range [0, W-1 or H-1].
        # We add 0.5 to turn them into real-value coordinate space. A better solution
        # would be to first +0.5 and then dilate the returned polygon by 0.5.
        res = [x + 0.5 for x in res if len(x) >= 6]
        return res, has_holes

    def load_model(self, config, model_weights, device="cuda:0"):
        config = mmcv.Config.fromfile(config)
        config.model.pretrained = None
        model = build_detector(config.model)
        model_weights = load_checkpoint(model, model_weights, map_location=device)
        model.CLASSES = model_weights["meta"]["CLASSES"]
        model.cfg = config
        model.to(device)
        model.eval()
        return model

    def predict(
        self,
        img: np.ndarray,
        show=False,
        score_thr=0.5,
        palette=[125, 178, 90],
    ):
        result = inference_detector(self.model, img)
        # print(result)
        if show:
            result_img = self.model.show_result(
                img,
                result,
                score_thr=score_thr,
                show=True,
                bbox_color=[palette],
                mask_color=[palette],
            )
        selected_out = []
        # print(result)
        bboxs, masks = result
        for bbox, mask in zip(bboxs[0], masks[0]):
            # print(bbox)
            # print(mask)
            x1, y1, x2, y2, confidence = bbox
            if confidence < score_thr:
                break
            # mask_uint = mask.astype(np.uint8)
            weapon_contoure, holes = self.mask_to_polygons(mask)
            # print(len(weapon_contoure))
            dict_result = {
                "bbox": [x1, y1, x2, y2],
                "contoure": weapon_contoure,
                "confidence": confidence,
            }
            selected_out.append(dict_result)
            # print(x1, y1, x2, y2, confidence, mask_uint)

        return selected_out
