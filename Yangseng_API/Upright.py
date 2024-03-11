import cv2
import mediapipe as mp
import os
import math

def up_pose(user_name, up_path):
    mp_pose = mp.solutions.pose

    EXCLUDED_LANDMARKS = set([
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
        mp_pose.PoseLandmark.LEFT_THUMB,
        mp_pose.PoseLandmark.RIGHT_THUMB,
        mp_pose.PoseLandmark.LEFT_PINKY,
        mp_pose.PoseLandmark.RIGHT_PINKY,
        mp_pose.PoseLandmark.LEFT_INDEX,
        mp_pose.PoseLandmark.RIGHT_INDEX,
    ])

    def calculate_distance(point1, point2):
        """计算两点之间的距离。

        Args:
            point1: 第一个点的坐标。
            point2: 第二个点的坐标。

        Returns:
            两点之间的距离。
        """

        x1, y1 = point1.x, point1.y
        x2, y2 = point2.x, point2.y

        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        return distance
    def calculate_angle(point1X,point1Y,point2X,point2Y):
        """计算两点连线与垂直线的夹角。

        Args:
            point1: 第一个点的坐标。
            point2: 第二个点的坐标。

        Returns:
            两点连线与垂直线的夹角。
        """
        
        # 计算两点之间的距离。
        # distance = calculate_distance(point1X,point1Y,point2X,point2Y)

        # 计算两点连线与水平线的夹角。
        angle = math.atan2(point2Y - point1Y, point2X - point1X)

        # 将角度转换为度。
        angle = math.degrees(angle)

        # 将角度转换为 0 到 180 度之间。
        angle = abs(angle % 180)

        return angle

    def process_image(image):
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks is None:
                return image

            annotated_image = image.copy()

            # 绘制连接线
            for connection in mp_pose.POSE_CONNECTIONS:
                start_landmark = connection[0]
                end_landmark = connection[1]

                if (start_landmark not in EXCLUDED_LANDMARKS) and (end_landmark not in EXCLUDED_LANDMARKS):
                    start_point = results.pose_landmarks.landmark[start_landmark]
                    end_point = results.pose_landmarks.landmark[end_landmark]

                    if start_point.visibility >= 0.1 and end_point.visibility >= 0.1:
                        start_point_x, start_point_y = int(start_point.x * image.shape[1]), int(start_point.y * image.shape[0])
                        end_point_x, end_point_y = int(end_point.x * image.shape[1]), int(end_point.y * image.shape[0])

                        # 排除左肩膀到左hip和右肩膀到右hip的连接线
                        if not ((start_landmark == mp_pose.PoseLandmark.LEFT_SHOULDER and end_landmark == mp_pose.PoseLandmark.LEFT_HIP) or
                                (start_landmark == mp_pose.PoseLandmark.RIGHT_SHOULDER and end_landmark == mp_pose.PoseLandmark.RIGHT_HIP)):
                            # 将关键点绘制为大红原点
                            cv2.circle(annotated_image, (start_point_x, start_point_y), 12, (0, 0, 255), -1)  # 修改关键点绘制为大红原点
                            cv2.circle(annotated_image, (end_point_x, end_point_y), 12, (0, 0, 255), -1)      # 修改关键点绘制为大红原点
                            cv2.line(annotated_image, (start_point_x, start_point_y), (end_point_x, end_point_y), (0, 0, 255), 3)
                            # 填充白色圆点
                            cv2.circle(annotated_image, (start_point_x, start_point_y), 8, (255, 255, 255), -1)
                            cv2.circle(annotated_image, (end_point_x, end_point_y), 8, (255, 255, 255), -1)
                            

            # 计算肩膀中点坐标
            left_shoulder_point = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder_point = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            # 計算如果兩個點沒有平行，告訴我傾斜的角度 用print
            
            

            if left_shoulder_point.visibility >= 0.1 and right_shoulder_point.visibility >= 0.1:
                shoulder_midpoint_x = (left_shoulder_point.x + right_shoulder_point.x) / 2
                shoulder_midpoint_y = (left_shoulder_point.y + right_shoulder_point.y) / 2
                # 绘制肩膀中点
                cv2.circle(annotated_image, (int(shoulder_midpoint_x * image.shape[1]), int(shoulder_midpoint_y * image.shape[0])), 12, (0, 0, 255), -1)


            # 计算臀部中点坐标
            left_hip_point = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip_point = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
            # 計算角度
            midpoint_shoulder = (left_hip_point.x + right_hip_point.x) / 2
            midpoint_hip = (left_hip_point.y + right_hip_point.y) / 2
            # 計算如果兩個點沒有平行，告訴我傾斜的角度 用print
            data = calculate_angle(shoulder_midpoint_x,shoulder_midpoint_y,midpoint_shoulder,midpoint_hip)
           
            # save data to file
            os.path.join('../user_images/'+user_name, 'data.txt')
            with open('../user_images/'+user_name+'/data.txt', 'w') as f:
                f.write(str(data))



            if left_hip_point.visibility >= 0.1 and right_hip_point.visibility >= 0.1:
                hip_midpoint_x = (left_hip_point.x + right_hip_point.x) / 2
                hip_midpoint_y = (left_hip_point.y + right_hip_point.y) / 2

                # 绘制臀部中点
                cv2.circle(annotated_image, (int(hip_midpoint_x * image.shape[1]), int(hip_midpoint_y * image.shape[0])), 12, (0, 0, 255), -1)


            # 获取鼻子的点
            nose_point = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            nose_x, nose_y = int(nose_point.x * image.shape[1]), int(nose_point.y * image.shape[0])
                # 绘制臀部中点
            cv2.circle(annotated_image, (nose_x, nose_y), 12, (0, 0, 255), -1)

            # 绘制连接线从肩膀中点到鼻子
            if left_shoulder_point.visibility >= 0.1 and right_shoulder_point.visibility >= 0.1:
                cv2.line(annotated_image, (int(shoulder_midpoint_x * image.shape[1]), int(shoulder_midpoint_y * image.shape[0])), (nose_x, nose_y), (0, 0, 255), 3)

            # 绘制连接线从臀部中点到鼻子
            if left_hip_point.visibility >= 0.1 and right_hip_point.visibility >= 0.1:
                cv2.line(annotated_image, (int(hip_midpoint_x * image.shape[1]), int(hip_midpoint_y * image.shape[0])), (int(shoulder_midpoint_x * image.shape[1]), int(shoulder_midpoint_y * image.shape[0])), (0, 0, 255), 3)

                
            cv2.circle(annotated_image, (int(shoulder_midpoint_x * image.shape[1]), int(shoulder_midpoint_y * image.shape[0])),8, (255, 255, 255), -1)
            cv2.circle(annotated_image, (nose_x, nose_y), 8, (255, 255, 255), -1)
            cv2.circle(annotated_image, (int(hip_midpoint_x * image.shape[1]), int(hip_midpoint_y * image.shape[0])), 8, (255, 255, 255), -1)
            return annotated_image

    image_folder = up_path
    image_files = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(('.jpg', '.jpeg', '.png'))]

    # 处理并储存图片
    output_folder = os.path.join('../user_images', user_name, 'result')  # 根据您的路径结构设置目标路径
    os.makedirs(output_folder, exist_ok=True)

    for image_file in image_files:
        image = cv2.imread(image_file)
        processed_image = process_image(image)
        output_file = os.path.join(output_folder, os.path.basename(image_file))
        cv2.imwrite(output_file, processed_image)
        # # 删除原始的数据来源图片
        # os.remove(image_file)
