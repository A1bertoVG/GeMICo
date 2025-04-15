import cv2
import mediapipe as mp
import rtmidi
import math

# MediaPipe y MIDI setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
midiout = rtmidi.MidiOut()
midiout.open_port(1)

# Estado manos
right_hand_detected = False
left_hand_detected = False

def distancia(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def map_range(value, in_min, in_max, out_min, out_max):
    value = max(min(value, in_max), in_min)
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)

    current_right = False
    current_left = False

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, hand_type in zip(result.multi_hand_landmarks, result.multi_handedness):
            hand_label = hand_type.classification[0].label
            landmarks = hand_landmarks.landmark
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Puntos: Pulgar (4), Índice (8)
            pulgar = landmarks[4]
            indice = landmarks[8]
            dist = distancia(pulgar, indice)

            # Escalar distancia a valor MIDI
            midi_val = map_range(dist, 0.05, 0.25, 0, 127)

            if hand_label == 'Right':
                current_right = True
                midiout.send_message([0xB0, 10, midi_val])  # CC FX1 Dry/Wet
                midiout.send_message([0xB0, 12, map_range(landmarks[0].y, 0.0, 1.0, 127, 0)])  # CC FX1 Feedback
                print(f"🎚️ Right Dry/Wet: {midi_val}")

            elif hand_label == 'Left':
                current_left = True
                midiout.send_message([0xB0, 11, midi_val])  # CC FX2 Dry/Wet
                midiout.send_message([0xB0, 13, map_range(landmarks[0].y, 0.0, 1.0, 127, 0)])  # CC FX2 Feedback
                print(f"🎚️ Left Dry/Wet: {midi_val}")

    # Cambios de estado ON/OFF FX
    if current_right and not right_hand_detected:
        midiout.send_message([0x90, 60, 127])  # Note ON FX1
        print("🖐️ Mano derecha detectada: FX1 ON")
    elif not current_right and right_hand_detected:
        midiout.send_message([0x80, 60, 0])    # Note OFF FX1
        print("🖐️ Mano derecha perdida: FX1 OFF")
    right_hand_detected = current_right

    if current_left and not left_hand_detected:
        midiout.send_message([0x90, 62, 127])  # Note ON FX2
        print("🤚 Mano izquierda detectada: FX2 ON")
    elif not current_left and left_hand_detected:
        midiout.send_message([0x80, 62, 0])    # Note OFF FX2
        print("🤚 Mano izquierda perdida: FX2 OFF")
    left_hand_detected = current_left

    # Convertir a blanco y negro para mostrar
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gray_bgr = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR)  # necesario para dibujar landmarks a color
    cv2.imshow("Gesture MIDI Control", frame_gray_bgr)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
midiout.close_port()
