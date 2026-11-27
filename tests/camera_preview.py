import cv2
import mediapipe as mp

from gesture_controller import GestureController


def draw_hand(preview, detector):
    #OpenCV的颜色顺序是BGR，MediaPipe接收RGB。
    rgb_frame = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
    result = detector.process(rgb_frame)

    if not result.multi_hand_landmarks:
        cv2.putText(preview, "No hand", (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 180, 255), 2)
        return

    hand = result.multi_hand_landmarks[0]
    mp.solutions.drawing_utils.draw_landmarks(
        preview, hand, mp.solutions.hands.HAND_CONNECTIONS
    )

    #用手腕和四个指根的平均位置估计掌心。
    palm_ids = (0, 5, 9, 13, 17)
    palm_x = sum(hand.landmark[i].x for i in palm_ids) / len(palm_ids)
    palm_y = sum(hand.landmark[i].y for i in palm_ids) / len(palm_ids)

    #关键点坐标是归一化坐标，画圆时换算成像素。
    height, width = preview.shape[:2]
    center = (int(palm_x * width), int(palm_y * height))
    cv2.circle(preview, center, 8, (0, 255, 255), -1)
    cv2.putText(preview, "Hand detected", (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 0), 2)
    
    return palm_x, palm_y


def main(detector):
    controller = GestureController()
    camera = cv2.VideoCapture(0) #0表示默认摄像头
    try:
        if not camera.isOpened():
            print("无法打开摄像头，请检查摄像头权限以及是否被其他软件占用。")
            return

        print("摄像头已打开。点击预览窗口，按Q或Esc退出。")
        while True:
            ok, frame = camera.read()
            if not ok:
                print("摄像头已打开，但读取画面失败。")
                break

            preview = cv2.flip(frame, 1) #水平镜像
            palm = draw_hand(preview, detector)
            controller.update(palm)
            direction = controller.get_direction()
            if direction is not None:
                print('方向:', direction, flush=True)
            cv2.imshow("Camera Preview", preview)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    with mp.solutions.hands.Hands(max_num_hands=1) as detector:
        main(detector)