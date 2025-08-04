from src.config.config_manager import get_id_file_path
import cv2
import numpy as np
from pathlib import Path

# 定义常量
CROP_COORDS = (5, 105, 1915, 885)
COLOR_RANGES = {
    'green': (np.array([35, 100, 100]), np.array([85, 255, 255])),
    'red': (np.array([0, 100, 100]), np.array([10, 255, 255]))
}


def create_color_masks(hsv_image, gray_image):
    """创建颜色掩码，整合掩码创建逻辑"""
    masks = {}
    # 使用字典批量处理颜色掩码
    for color, (lower, upper) in COLOR_RANGES.items():
        masks[color] = cv2.inRange(hsv_image, lower, upper)

    # 创建黑色掩码
    _, masks['black'] = cv2.threshold(gray_image, 50, 255, cv2.THRESH_BINARY_INV)

    return masks


def find_and_connect_endpoints(image, green_mask, red_mask):
    """优化后的端点连接函数"""
    # 使用CHAIN_APPROX_SIMPLE减少内存使用
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not (red_contours and green_contours):
        return

    # 直接计算矩形中心点，避免重复计算
    green_rect = cv2.boundingRect(green_contours[0])
    red_rect = cv2.boundingRect(red_contours[0])

    start_point = (green_rect[0] + green_rect[2], green_rect[1] + green_rect[3] // 2)
    end_point = (red_rect[0], red_rect[1] + red_rect[3] // 2)

    cv2.line(image, start_point, end_point, (0, 0, 0), 2)


def process_deviation_area(image, output_path):
    """整合的图像处理函数"""
    # 裁剪图像
    x, y, w, h = CROP_COORDS
    cropped = image[y:y + h, x:x + w]

    # 同时转换灰度和HSV，避免重复读取图像
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

    # 创建所有掩码
    masks = create_color_masks(hsv, gray)

    # 连接端点
    find_and_connect_endpoints(cropped, masks['green'], masks['red'])

    # 合并掩码，使用reduce操作
    combined_mask = np.zeros_like(gray)
    for mask in masks.values():
        combined_mask = cv2.bitwise_or(combined_mask, mask)

    # 查找轮廓
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return

    # 创建单一掩码处理所有轮廓
    mask = np.zeros_like(combined_mask)
    cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

    # 计算非零像素
    non_zero_pixels = cv2.countNonZero(mask)

    # 使用 pathlib 处理路径，提高跨平台兼容性
    write_result(non_zero_pixels, output_path)


def write_result(pixel_count, output_path):
    """独立的结果写入函数"""
    try:
        # 读取ID
        with open(get_id_file_path(), "r") as file:
            id = file.read().strip()

        # 构建完整路径
        result_path = f"./Behavioral_data/{id}/{output_path}/data/数据.txt"

        # 确保目录存在
        Path(result_path).parent.mkdir(parents=True, exist_ok=True)

        # 写入结果
        with open(result_path, "a", encoding="utf-8") as f:
            f.write(f"偏差像素个数 : {pixel_count}\n")
    except Exception as e:
        print(f"写入结果时出错: {e}")
        raise  # 重新抛出异常以便调试


def deviation_area1(image):
    """子任务A的处理函数"""
    process_deviation_area(image, "subA")


def deviation_area2(image):
    """子任务A+B的处理函数"""
    process_deviation_area(image, "subB")

def deviation_area3(image):
    """子任务A+B的处理函数"""
    process_deviation_area(image, "subA+B")