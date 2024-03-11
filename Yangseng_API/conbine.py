from PIL import Image
import os
import datetime

def merge_images_and_move(user_name, employee_name):
    result_folder = f'../user_images/{user_name}/result'
    final_folder = f'../user_images/{user_name}'
    
    # 檢查結果資料夾是否存在
    if not os.path.exists(result_folder):
        print(f"Result folder for {user_name} does not exist.")
        return

    # 取得 result 資料夾中的所有圖片檔案，按照包含 "front"、"back"、"left"、"right" 的順序排序
    image_files = [f for f in os.listdir(result_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]

    # 根據檔名中包含的關鍵字 "front"、"back"、"left"、"right" 來排序圖片檔案

    image_files.sort(key=lambda x: ("right" in x, "left" in x, "back" in x, "front" in x))
    # 確認是否有正確數量的圖片
    if len(image_files) != 4:
        print("There should be exactly 4 images in the result folder.")
        return

    # 打開圖片並儲存到一個列表中
    images = [Image.open(os.path.join(result_folder, f)) for f in image_files]

    # 取得每個圖片的寬度和高度
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)

    # 建立一個新的大圖片
    merged_image = Image.new('RGB', (total_width, max_height))

    # 將每張圖片貼到大圖片上
    x_offset = 0
    for image in images:
        merged_image.paste(image, (x_offset, 0))
        x_offset += image.width

    # 取得當前時間，並將其加入到檔名中
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_image_filename = f'{user_name}_merged_{current_time}_by_{employee_name}.png'

    # 儲存合併後的圖片到 user_name 資料夾
    merged_image_path = os.path.join(final_folder, merged_image_filename)
    merged_image.save(merged_image_path)

    # 清空 result 資料夾內的圖片
    for image_file in image_files:
        os.remove(os.path.join(result_folder, image_file))
