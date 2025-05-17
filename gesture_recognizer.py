import cv2
import mediapipe as mp
import pygame
import threading
import numpy as np

class GestureRecognizer:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.running = False
        self.gesture_log = []
        self.last_finger_count = None
        self.lock = threading.Lock()

        pygame.mixer.init()
        self.sounds_mapping = {
            1: "sounds/kick-bass.mp3",
            2: "sounds/crash.mp3",
            3: "sounds/snare.mp3",
            4: "sounds/tom-1.mp3",
            5: "sounds/tom-2.mp3",
            6: "sounds/tom-3.mp3",
            7: "sounds/cr78-Cymbal.mp3",
            8: "sounds/cr78-Guiro 1.mp3",
            9: "sounds/tempest-HiHat Metal.mp3",
            10: "sounds/cr78-Bongo High.mp3"
        }

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def is_running(self):
        with self.lock:
            return self.running

    def get_gestures(self):
        with self.lock:
            return self.gesture_log.copy()

    def generate_frames(self):
        while self.is_running():
            success, image = self.cap.read()
            if not success:
                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            finger_count = 0
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    hand_index = results.multi_hand_landmarks.index(hand_landmarks)
                    hand_label = results.multi_handedness[hand_index].classification[0].label
                    hand_landmarks_list = []

                    for landmarks in hand_landmarks.landmark:
                        hand_landmarks_list.append([landmarks.x, landmarks.y])

                    if hand_label == "Left" and hand_landmarks_list[4][0] > hand_landmarks_list[3][0]:
                        finger_count += 1
                    elif hand_label == "Right" and hand_landmarks_list[4][0] < hand_landmarks_list[3][0]:
                        finger_count += 1

                    if hand_landmarks_list[8][1] < hand_landmarks_list[6][1]:
                        finger_count += 1
                    if hand_landmarks_list[12][1] < hand_landmarks_list[10][1]:
                        finger_count += 1
                    if hand_landmarks_list[16][1] < hand_landmarks_list[14][1]:
                        finger_count += 1
                    if hand_landmarks_list[20][1] < hand_landmarks_list[18][1]:
                        finger_count += 1

                    self.mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())

            with self.lock:
                if finger_count in self.sounds_mapping and finger_count != self.last_finger_count:
                    self.gesture_log.append(finger_count)
                    self.last_finger_count = finger_count

            if finger_count in self.sounds_mapping:
                sound_file = self.sounds_mapping[finger_count]
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                if finger_count <= 5:
                    pygame.time.delay(100)
                elif 5 < finger_count <= 9:
                    pygame.time.delay(100)
                    pygame.mixer.music.play()
                pygame.mixer.music.stop()

            cv2.putText(image, str(finger_count), (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 10)

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def run(self):
        with self.lock:
            self.running = True
        while self.is_running():
            self.generate_frames()

    def start(self):
        if not self.is_running():
            self.thread = threading.Thread(target=self.run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        with self.lock:
            self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        self.cap.release()