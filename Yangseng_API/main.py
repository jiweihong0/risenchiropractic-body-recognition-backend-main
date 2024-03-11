
from sideways import side_pose
from Upright import up_pose
import sys
from conbine import merge_images_and_move
def main():
    if len(sys.argv) != 5:
        print("Usage: python main.py <user_name> <employee_name> <side_path> <up_path> 123")
        sys.exit(1)

    user_name = sys.argv[2]
    employee_name = sys.argv[1]
    side_path = sys.argv[3]
    up_path = sys.argv[4]

    # 呼叫 side_pose() 並傳遞上面的 side_path
    side_pose(user_name,side_path)
    # 呼叫 up_pose() 並傳遞上面的 up_path
    up_pose(user_name,up_path)
    # 呼叫合併圖片的函式
    merge_images_and_move(user_name, employee_name)


if __name__ == "__main__":
    main()
