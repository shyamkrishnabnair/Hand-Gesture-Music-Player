import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import mediapipe as mp
import numpy as np
from playsound import playsound
import threading
import time
import queue

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

sounds_mapping = {
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

class HandTracker(VideoProcessorBase):
    def __init__(self):
        self.hands = mp_hands.Hands(
            model_complexity=1,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.last_sound = None
        self.last_play_time = 0
        self.sound_queue = queue.Queue()
        self.frame_count = 0

    def play_sound(self, sound_file):
        try:
            playsound(sound_file, block=False)
        except Exception as e:
            print(f"Error playing sound: {e}")

    def recv(self, frame):
        self.frame_count += 1
        if self.frame_count % 2 != 0:
            return frame.to_ndarray(format="bgr24")
        
        start_time = time.time()
        try:
            image = frame.to_ndarray(format="bgr24")
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image_rgb)
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

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

                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

            cv2.putText(image, str(finger_count), (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            current_time = time.time()
            if finger_count in sounds_mapping and (current_time - self.last_play_time > 0.5):
                sound_file = sounds_mapping[finger_count]
                if sound_file != self.last_sound:
                    self.sound_queue.put(sound_file)
                    self.last_sound = sound_file
                    self.last_play_time = current_time
                    threading.Thread(target=self.play_sound, args=(sound_file,), daemon=True).start()
                    if finger_count > 5 and finger_count <= 9:
                        time.sleep(0.1)
                        threading.Thread(target=self.play_sound, args=(sound_file,), daemon=True).start()

            print(f"Frame processing time: {(time.time() - start_time)*1000:.2f} ms")
            return image
        except Exception as e:
            print(f"Error processing frame: {e}")
            return image

def main():
    st.title("Hand Gesture Sound Player")
    st.write("Show your fingers to play different sounds! (1-10 fingers)")
    
    webrtc_streamer(
        key="hand-tracker",
        video_processor_factory=HandTracker,
        media_stream_constraints={"video": {"width": {"ideal": 640}, "height": {"ideal": 480}, "frameRate": {"ideal": 15}}, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

if __name__ == "__main__":
    main()