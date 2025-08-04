from src.config.config_manager import get_id_file_path, get_base_dir
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os


def save_cropped_image(frame, x, y, width, height, filename):
    # 裁剪指定区域
    roi = frame[y:y + height, x:x + width]
    return roi


def calculate_pixel_difference(origin_image, image1, image2, t1, t2, timestamp, total_pause_time=0):
    # 1. 裁剪图像
    x, y, width, height = 0, 50, 1920, 920
    origin_image = save_cropped_image(origin_image, x, y, width, height, timestamp)
    image1 = save_cropped_image(image1, x, y, width, height, timestamp)
    image2 = save_cropped_image(image2, x, y, width, height, timestamp)

    # 2. 转换为灰度图并二值化
    gray_origin = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    _, binary_origin = cv2.threshold(gray_origin, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. 创建黑色轨迹掩码（从image1中提取）
    black_mask = (gray_origin < 50)  # 黑色轨迹掩码

    # 4. 从image2中提取绿色轨迹
    hsv_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv_image2, lower_green, upper_green)
    green_mask = (green_mask > 0)

    # 5. 计算重合部分（交集）
    overlap_mask = black_mask & green_mask

    # 6. 统计像素
    total_pixels = np.sum(black_mask)  # 黑色轨迹的总像素
    overlap_pixels = np.sum(overlap_mask)  # 重合部分的像素

    # 计算百分比 (重合像素/总像素)
    overlap_percentage = (overlap_pixels / total_pixels * 100) if total_pixels > 0 else 0

    # 计算纯绘图时间（减去平均分配的暂停时间）
    raw_time = t2 - t1
    time_diff = raw_time

    # 7. 保存结果
    with open(get_id_file_path(), "r") as file:
        id = file.read()
    behavioral_data_path = os.path.join(get_base_dir(), "Behavioral_data", id, "subA", "data", "数据.txt")
    with open(behavioral_data_path, "a", encoding="utf-8") as f:
        f.write(
            f"有效像素: {overlap_pixels}   总像素: {total_pixels}   "
            f"百分比：{overlap_percentage:.2f}%   绘图时长：{time_diff} \n")

    # 8. 返回计算结果（用于调试）
    return {
        'overlap_pixels': overlap_pixels,
        'total_pixels': total_pixels,
        'percentage': overlap_percentage,
        'time': time_diff
    }




def calculate_pixel_difference2(origin_image, image1, image2, t1, t2, timestamp, total_pause_time=0):
    # 1. 裁剪图像
    x, y, width, height = 0, 50, 1920, 920
    origin_image = save_cropped_image(origin_image, x, y, width, height, timestamp)
    image1 = save_cropped_image(image1, x, y, width, height, timestamp)
    image2 = save_cropped_image(image2, x, y, width, height, timestamp)

    # 2. 转换为灰度图并二值化
    gray_origin = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    _, binary_origin = cv2.threshold(gray_origin, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. 创建黑色轨迹掩码（从image1中提取）
    black_mask = (gray_origin < 50)  # 黑色轨迹掩码

    # 4. 从image2中提取绿色轨迹
    hsv_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv_image2, lower_green, upper_green)
    green_mask = (green_mask > 0)

    # 5. 计算重合部分（交集）
    overlap_mask = black_mask & green_mask

    # 6. 统计像素
    total_pixels = np.sum(black_mask)  # 黑色轨迹的总像素
    overlap_pixels = np.sum(overlap_mask)  # 重合部分的像素

    # 计算百分比 (重合像素/总像素)
    overlap_percentage = (overlap_pixels / total_pixels * 100) if total_pixels > 0 else 0

    # 计算纯绘图时间（减去平均分配的暂停时间）
    raw_time = t2 - t1
    time_diff = raw_time

    # 7. 保存结果
    with open(get_id_file_path(), "r") as file:
        id = file.read()
    behavioral_data_path = os.path.join(get_base_dir(), "Behavioral_data", id, "subAB", "data", "数据.txt")
    with open(behavioral_data_path, "a", encoding="utf-8") as f:
        f.write(
            f"有效像素: {overlap_pixels}   总像素: {total_pixels}   "
            f"百分比：{overlap_percentage:.2f}%   绘图时长：{time_diff} \n")

    # 8. 返回计算结果（用于调试）
    return {
        'overlap_pixels': overlap_pixels,
        'total_pixels': total_pixels,
        'percentage': overlap_percentage,
        'time': time_diff
    }

def calculate_pixel_difference3(origin_image, image1, image2, t1, t2, timestamp, total_pause_time=0):
    # 1. 裁剪图像
    x, y, width, height = 0, 50, 1920, 920
    origin_image = save_cropped_image(origin_image, x, y, width, height, timestamp)
    image1 = save_cropped_image(image1, x, y, width, height, timestamp)
    image2 = save_cropped_image(image2, x, y, width, height, timestamp)

    # 2. 转换为灰度图并二值化
    gray_origin = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    _, binary_origin = cv2.threshold(gray_origin, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. 创建黑色轨迹掩码（从image1中提取）
    black_mask = (gray_origin < 50)  # 黑色轨迹掩码

    # 4. 从image2中提取绿色轨迹
    hsv_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv_image2, lower_green, upper_green)
    green_mask = (green_mask > 0)

    # 5. 计算重合部分（交集）
    overlap_mask = black_mask & green_mask

    # 6. 统计像素
    total_pixels = np.sum(black_mask)  # 黑色轨迹的总像素
    overlap_pixels = np.sum(overlap_mask)  # 重合部分的像素

    # 计算百分比 (重合像素/总像素)
    overlap_percentage = (overlap_pixels / total_pixels * 100) if total_pixels > 0 else 0

    # 计算纯绘图时间（减去平均分配的暂停时间）
    raw_time = t2 - t1
    time_diff = raw_time

    # 7. 保存结果
    with open(get_id_file_path(), "r") as file:
        id = file.read()
    behavioral_data_path = os.path.join(get_base_dir(), "Behavioral_data", id, "subAC", "data", "数据.txt")
    with open(behavioral_data_path, "a", encoding="utf-8") as f:
        f.write(
            f"有效像素: {overlap_pixels}   总像素: {total_pixels}   "
            f"百分比：{overlap_percentage:.2f}%   绘图时长：{time_diff} \n")

    # 8. 返回计算结果（用于调试）
    return {
        'overlap_pixels': overlap_pixels,
        'total_pixels': total_pixels,
        'percentage': overlap_percentage,
        'time': time_diff
    }