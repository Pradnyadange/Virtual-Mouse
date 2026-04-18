import cv2
import mediapipe as mp
import pyautogui
import math
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    model_complexity=0,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()
cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

pyautogui.FAILSAFE = False

cooldown = 0.5
last_action = {
    "middle": 0,
    "left": 0,
    "right": 0,
    "scroll_up": 0,
    "scroll_down": 0,
    "drag": 0,
    "double": 0
}

prev_x, prev_y = 0, 0
smooth = 5

def dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    now = time.time()

    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0].landmark
        mp_draw.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

        ix = int(landmarks[8].x * cam_w)
        iy = int(landmarks[8].y * cam_h)

        mouse_x = int(landmarks[8].x * screen_w)
        mouse_y = int(landmarks[8].y * screen_h)

        curr_x = prev_x + (mouse_x - prev_x) / smooth
        curr_y = prev_y + (mouse_y - prev_y) / smooth
        pyautogui.moveTo(curr_x, curr_y)
        prev_x, prev_y = curr_x, curr_y

        cv2.circle(frame, (ix, iy), 8, (0, 255, 0), -1)

        pinch = dist(landmarks[4], landmarks[8])

        if pinch < 0.02:
            if now - last_action["double"] > cooldown:
                pyautogui.doubleClick()
                last_action["double"] = now
                last_action["left"] = now
        elif pinch < 0.04:
            if now - last_action["left"] > cooldown:
                pyautogui.click()
                last_action["left"] = now

        if dist(landmarks[8], landmarks[12]) < 0.04:
            if now - last_action["right"] > cooldown:
                pyautogui.rightClick()
                last_action["right"] = now

        if landmarks[8].y < landmarks[6].y and landmarks[12].y > landmarks[10].y:
            if now - last_action["middle"] > cooldown:
                pyautogui.middleClick()
                last_action["middle"] = now

        fingers_up = (
            landmarks[4].y < landmarks[3].y and
            landmarks[8].y < landmarks[6].y and
            landmarks[12].y < landmarks[10].y and
            landmarks[16].y < landmarks[14].y and
            landmarks[20].y < landmarks[18].y
        )

        if fingers_up and now - last_action["scroll_up"] > cooldown:
            pyautogui.scroll(120)
            last_action["scroll_up"] = now

        fingers_down = (
            landmarks[4].y > landmarks[3].y and
            landmarks[8].y > landmarks[6].y and
            landmarks[12].y > landmarks[10].y and
            landmarks[16].y > landmarks[14].y and
            landmarks[20].y > landmarks[18].y
        )

        if fingers_down and now - last_action["scroll_down"] > cooldown:
            pyautogui.scroll(-120)
            last_action["scroll_down"] = now

        if (
            landmarks[8].y < landmarks[6].y and
            landmarks[12].y < landmarks[10].y and
            landmarks[16].y > landmarks[14].y
        ):
            if now - last_action["drag"] > cooldown:
                pyautogui.dragTo(mouse_x + 150, mouse_y, duration=0.2)
                last_action["drag"] = now

    cv2.imshow("Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
