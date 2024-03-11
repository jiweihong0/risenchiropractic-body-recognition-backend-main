import cv2
import mediapipe as mp
import os

def side_pose(user_name, side_path):
    # 初始化MediaPipe姿勢估計模型
    mp_pose = mp.solutions.pose

    # 要排除的臉部和手掌的關鍵點
    EXCLUDED_LANDMARKS = set([
        mp_pose.PoseLandmark.NOSE,
        mp_pose.PoseLandmark.LEFT_EYE_INNER,
        mp_pose.PoseLandmark.LEFT_EYE,
        mp_pose.PoseLandmark.LEFT_EYE_OUTER,
        mp_pose.PoseLandmark.RIGHT_EYE_INNER,
        mp_pose.PoseLandmark.RIGHT_EYE,
        mp_pose.PoseLandmark.RIGHT_EYE_OUTER,
        mp_pose.PoseLandmark.LEFT_EAR,
        mp_pose.PoseLandmark.RIGHT_EAR,
        mp_pose.PoseLandmark.MOUTH_LEFT,
        mp_pose.PoseLandmark.MOUTH_RIGHT,
        mp_pose.PoseLandmark.LEFT_WRIST,
        mp_pose.PoseLandmark.RIGHT_WRIST,
        mp_pose.PoseLandmark.LEFT_ANKLE,
        mp_pose.PoseLandmark.RIGHT_ANKLE,
        mp_pose.PoseLandmark.LEFT_ELBOW,
        mp_pose.PoseLandmark.RIGHT_ELBOW,
        mp_pose.PoseLandmark.LEFT_THUMB,
        mp_pose.PoseLandmark.RIGHT_THUMB,
        mp_pose.PoseLandmark.LEFT_PINKY,
        mp_pose.PoseLandmark.RIGHT_PINKY,
        mp_pose.PoseLandmark.LEFT_INDEX,
        mp_pose.PoseLandmark.RIGHT_INDEX,
    ])

    def apply_landmark_exclusions(excluded_landmarks, image_file):
        if "left" in image_file:
            excluded_landmarks.add(mp_pose.PoseLandmark.RIGHT_HIP)
            excluded_landmarks.add(mp_pose.PoseLandmark.RIGHT_SHOULDER)
            excluded_landmarks.add(mp_pose.PoseLandmark.RIGHT_FOOT_INDEX)
            excluded_landmarks.add(mp_pose.PoseLandmark.RIGHT_ANKLE)
            excluded_landmarks.add(mp_pose.PoseLandmark.RIGHT_HEEL)
        elif "right" in image_file:
            excluded_landmarks.add(mp_pose.PoseLandmark.LEFT_HIP)
            excluded_landmarks.add(mp_pose.PoseLandmark.LEFT_SHOULDER)
            excluded_landmarks.add(mp_pose.PoseLandmark.LEFT_FOOT_INDEX)
            excluded_landmarks.add(mp_pose.PoseLandmark.LEFT_ANKLE)
            excluded_landmarks.add(mp_pose.PoseLandmark.LEFT_HEEL)

    # 圖片或攝影機視訊處理函數
    def process_image(image, output_path, filename):
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            # 將圖片轉換為RGB格式
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 執行姿勢估計
            results = pose.process(image_rgb)

            # 繪製姿勢估計結果，排除臉部、手掌和手臂的關鍵點
            annotated_image = image.copy()
            image_height, image_width, _ = annotated_image.shape
            keypoints = []
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                if landmark.HasField('visibility') and landmark.visibility < 0.6:
                    continue
                if landmark.HasField('presence') and landmark.presence < 0.5:
                    continue
                if idx not in EXCLUDED_LANDMARKS:
                    cx, cy = int(landmark.x * image_width), int(landmark.y * image_height)
                    keypoints.append((cx, cy))
                    # 定義圓點的大小
                    circle_radius = 15
                    # 繪製大圓點
                    cv2.circle(annotated_image, (cx, cy), circle_radius, (0, 0, 255), -1)

            # 繪製連接線
            if len(keypoints) >= 2:
                for i in range(len(keypoints) - 1):
                    cv2.line(annotated_image, keypoints[i], keypoints[i + 1], (0, 0, 255), 2)

            # 繪製最後一個紅色圓點
            if keypoints:
                last_keypoint = keypoints[-1]
                cv2.circle(annotated_image, last_keypoint, circle_radius, (0, 0, 255), -1)
                cv2.circle(annotated_image, last_keypoint, circle_radius - 5, (255, 255, 255), -1)

            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                if landmark.HasField('visibility') and landmark.visibility < 0.6:
                    continue
                if landmark.HasField('presence') and landmark.presence < 0.5:
                    continue
                if idx not in EXCLUDED_LANDMARKS:
                    cx, cy = int(landmark.x * image_width), int(landmark.y * image_height)
                    keypoints.append((cx, cy))
                    # 定義圓點的大小
                    circle_radius = 15
                    # 繪製白色圓形
                    cv2.circle(annotated_image, (cx, cy), circle_radius - 5, (255, 255, 255), -1)



            # 儲存處理後的圖片
            cv2.imwrite(output_path, annotated_image)

    # 讀取圖片
    image_folder = side_path
    image_files = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(('.jpg', '.jpeg', '.png'))]

    # 處理並儲存圖片
    output_folder = os.path.join('../user_images', user_name, 'result')  # 根據您的路徑結構設定目標路徑
    os.makedirs(output_folder, exist_ok=True)
    for image_id, image_file in enumerate(image_files):
        image = cv2.imread(image_file)
        output_file = os.path.join(output_folder, os.path.basename(image_file))
        # 暫存原始的 EXCLUDED_LANDMARKS
        original_excluded_landmarks = EXCLUDED_LANDMARKS.copy()
        apply_landmark_exclusions(EXCLUDED_LANDMARKS, os.path.basename(image_file))
        process_image(image, output_file, os.path.basename(image_file))
        # # 刪除原始的資料來源圖片
        # os.remove(image_file)
        # 還原 EXCLUDED_LANDMARKS 到原始狀態
        EXCLUDED_LANDMARKS = original_excluded_landmarks