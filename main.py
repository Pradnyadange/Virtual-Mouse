import cv2
import mediapipe as mp
import pyautogui
import os
import math
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Hand detector
hands = mp_hands.Hands(
    model_complexity=0,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0)

last_middle = 0
last_left = 0
last_scrollUp = 0
last_scrollDown = 0

cooldown = 0.5


while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Mirror effect
    frame = cv2.flip(frame, 1)

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process hand
    results = hands.process(rgb_frame)

    current_time = time.time()

    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0].landmark
        index_tip = landmarks[8]
        index_joint = landmarks[6]
        if index_tip.y > index_joint.y:
            pyautogui.middleClick()
            last_middle = current_time

        thumb = landmarks[4]
        index = landmarks[8]
        h,w,_=frame.shape
        thumb_x , thumb_y = int(thumb.x*w), int(thumb.y*h)
        index_x , index_y = int(index.x*w), int(index.y*h)

        distance = math.hypot(index_x - thumb_x , index_y - thumb_y)
        if distance < 40:
            pyautogui.leftClick()
            last_left = current_time

    thumb_up = landmarks[4].y < landmarks[3].y
    index_up = landmarks[8].y < landmarks[6].y
    middle_up = landmarks[12].y < landmarks[10].y
    ring_up = landmarks[16].y < landmarks[14].y
    pinky_up = landmarks[20].y < landmarks[18].y
    if thumb_up and index_up and middle_up and ring_up and pinky_up:
          if current_time - last_scrollUp > cooldown:
           pyautogui.scroll(100)
           last_scrollUp = current_time

    thumb_down = landmarks[4].y > landmarks[3].y
    index_down = landmarks[8].y > landmarks[6].y
    middle_down = landmarks[12].y > landmarks[10].y
    ring_down = landmarks[16].y > landmarks[14].y
    pinky_down = landmarks[20].y > landmarks[18].y
    if thumb_up and index_down and middle_down and ring_down and pinky_down:
          if current_time - last_scrollDown > cooldown:
           pyautogui.scroll(100)
           last_scrollDown = current_time

          index_1 = landmarks[8].y < landmarks[6].y
          middle_2 = landmarks[12].y < landmarks[10].y
          ring_down = landmarks[16].y > landmarks[14].y
    if index_1 and middle_2 and ring_down:
        pyautogui.dragTo(500, 300, duration=1)

