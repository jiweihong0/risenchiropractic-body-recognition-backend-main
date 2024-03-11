import os
import sys

def clear(user_name):
    # 要清除的資料夾列表
    folders_to_clear = ['side_pose', 'up_pose']

    for folder in folders_to_clear:
        folder_path = os.path.join('../user_images', user_name, folder)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

if __name__ == "__main__":
    # 確保有足夠的命令行參數
    if len(sys.argv) != 2:
        print("Usage: python clear.py user_name")
        sys.exit(1)

    # 從命令行參數獲取使用者名稱
    user_name = sys.argv[1]
    clear(user_name)
