import cv2


def get_preview(video_destention, frame_name):
    cap = cv2.VideoCapture(video_destention)
    ret, frame = cap.read()
    cv2.imwrite(frame_name, frame)
    cap.release()
    return frame_name
