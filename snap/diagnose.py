import cv2
import mediapipe as mp
import time

# 初始化 MediaPipe Pose 和 Face Detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5)
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# 初始化摄像头
cap = cv2.VideoCapture(0)
alarm_triggered = False
last_face_detected_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 转换为RGB格式并检测
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_results = pose.process(rgb_frame)
    face_results = face_detection.process(rgb_frame)
    
    # 绘制人体关键点
    if pose_results.pose_landmarks:
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    # 检测人脸
    if face_results.detections:
        last_face_detected_time = time.time()
        alarm_triggered = False
    else:
        # 如果超过2秒没有检测到人脸，则触发报警
        if time.time() - last_face_detected_time > 2:
            if not alarm_triggered:
                print("报警：屏幕内没有检测到人脸！")
                alarm_triggered = True
    
    cv2.imshow('MediaPipe Human Detection', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
