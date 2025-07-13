#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import cv2
import pygame
import sys
import math
from src.core import game_function as gf
from src.utils import shared_data
from src.ui.Button import Button, Button2
from src.data.Calculate_pixel_difference import calculate_pixel_difference, calculate_pixel_difference2, \
    calculate_pixel_difference3
from src.data.Deviation_area import deviation_area1, deviation_area2, deviation_area3
from src.utils.game_stats import GameStats
from src.core.level import Level
from src.hardware.serial_marker import serial_marker, initialize_serial
from src.config.settings import *
import random
from src.ui.likert_scale import LikertScale
from src.data.handle_slider_event import  handle_button_event
import csv
import os
from datetime import datetime
from src.core.paint import GameDrawing
from src.utils.font_utils import get_font_path
def speed_level_to_value(level):
    """将1-100级别转换为50-150的实际速度值"""
    return 50 + (level - 1) * (150 - 50) / 99

def speed_value_to_level(value):
    """将50-150的实际速度值转换为1-100级别"""
    return int(1 + (value - 50) * 99 / (150 - 50))

def read_speed_value():
    """读取scroll_value.txt中的速度值，如果文件不存在或值无效则返回默认值50"""
    try:
        with open('scroll_value.txt', 'r') as f:
            speed_value = int(f.read().strip())
            # 确保速度值在合理范围内
            return max(50, min(150, speed_value))
    except (FileNotFoundError, ValueError):
        # 如果文件不存在或值无效，创建默认文件并返回默认值
        with open('scroll_value.txt', 'w') as f:
            f.write('50')
        return 50

def handle_image_navigation(game_drawing, numbers, current_index, self, action="next"):
    """统一处理图片导航逻辑，确保图片按固定顺序显示"""
    serial_marker(bytes([0x01]))
    if current_index < len(numbers):
        return game_drawing.random_painting(numbers[current_index], self, current_index)
    return None, None

# 绘图参数
dots_time = []
green = (50, 128, 50)
black = (0, 0, 0)
grey = (230, 230, 230)
RED = (255, 0, 0)

# 存储三组被试数据的全局变量
experiment_data = {
    'subA': None,
    'subAB': None,
    'subAC': None
}


def draw_key_box(screen, text, font, center_pos):
    """
    绘制一个带有边框的按键方框，并返回其占用的矩形区域。
    """
    KEY_BG_COLOR = (255, 255, 255)
    KEY_BORDER_COLOR = (100, 100, 100)
    KEY_TEXT_COLOR = black
    PADDING_X = 8
    PADDING_Y = 4

    text_surf = font.render(text, True, KEY_TEXT_COLOR)
    text_rect = text_surf.get_rect()

    box_rect = pygame.Rect(0, 0, text_rect.width + PADDING_X * 2, text_rect.height + PADDING_Y * 2)
    box_rect.center = center_pos

    pygame.draw.rect(screen, KEY_BG_COLOR, box_rect, border_radius=5)
    pygame.draw.rect(screen, KEY_BORDER_COLOR, box_rect, 2, border_radius=5)

    text_rect.center = box_rect.center
    screen.blit(text_surf, text_rect)

    return box_rect


class Game:

    def __init__(self):
        # 初始化
        pygame.init()
        # 初始化速度为1级别（对应速度值50）
        with open('scroll_value.txt', 'w') as f:
            f.write('50')
        settings = Settings()
        stats = GameStats(settings)

        # 设置屏幕
        self.screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), pygame.FULLSCREEN)
        self.font = pygame.font.Font(get_font_path(), 40)
        pygame.display.set_caption('实验')

        # 设置时钟
        self.clock = pygame.time.Clock()
        self.screen.fill(grey)

        # 创建Level对象
        self.level = Level()



    def run(self):
        global paused, t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3, timestamp4, timestamp5, timestamp6, timestamp7, timestamp8
        settings = Settings()
        stats = GameStats(settings)
        user1_mark = getattr(shared_data, 'user1_mark', '01')
        user2_mark = getattr(shared_data, 'user2_mark', '02')
        user3_mark = getattr(shared_data, 'user3_mark', '03')

        # 从完整标识符中提取数字部分（如从"SZ21-01"提取"01"）
        def extract_number(mark):
            if mark and isinstance(mark, str):
                # 查找最后一个连字符后的数字
                if '-' in mark:
                    return mark.split('-')[-1]
                # 如果没有连字符，查找字符串末尾的数字
                import re
                match = re.search(r'\d+$', mark)
                if match:
                    return match.group()
            return mark

        user1 = extract_number(user1_mark)
        user2 = extract_number(user2_mark)
        user3 = extract_number(user3_mark)
        # 导入绘图模块

        game_drawing = GameDrawing()
        
        try:
            initialize_serial()
            print("串口初始化成功")
        except Exception as e:
            print("未找到串口")

        t1, t2, t3, t4, t5, t6, t7, t8, t9 = [None] * 9
        timestamp1, timestamp2, timestamp3, timestamp4, timestamp5, timestamp6, timestamp7, timestamp8 = [None] * 8
        with open('config.txt', 'w') as f:
            f.truncate(0)
            f.write('1')

        # 速度调整按钮设置
        speed_value = read_speed_value()
        speed_min, speed_max = 50, 150
        speed_step = 25
        
        # 按钮位置设置
        button_y = 30
        button_size = 40
        button_spacing = 40
        
        # 减速按钮
        minus_button_rect = pygame.Rect(settings.screen_width - 250, button_y, button_size, button_size)
        # 加速按钮
        plus_button_rect = pygame.Rect(settings.screen_width - 140, button_y, button_size, button_size)
        # 数值显示区域
        value_display_rect = pygame.Rect(settings.screen_width - 200 , button_y, 55, button_size)

        self.display_flowchart_instructions()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
                        self.screen.fill(grey)
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.clock.tick(60)  # 限制帧率，减少CPU使用
        self.display_meditation_instructions()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
                        self.screen.fill(grey)
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.clock.tick(60)  # 限制帧率，减少CPU使用

        numbers1 = random.sample(range(1, 9), 8)
        self.screen.fill(grey)
        line_length = 20
        pygame.draw.line(self.screen, green, (910, 540), (1010, 540), line_length)
        pygame.draw.line(self.screen, green, (960, 490), (960, 590), line_length)
        pygame.display.update()
        serial_marker(bytes([0x04]))
        start_ticks = pygame.time.get_ticks()
        running = True
        countdown_time = 2
        paused = False
        pause_start_time = 0
        total_pause_time = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            remaining_time = max(0, countdown_time - elapsed_time)
            if remaining_time == 0:
                running = False
                self.screen.fill(grey)
            self.clock.tick(60)  # 限制帧率，减少CPU使用
        # 使用新格式的指导语替换旧的指导语
        self.display_task_instructions_formatted(subject='A')
        waiting_for_space = True
        while waiting_for_space:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        waiting_for_space = False
            self.clock.tick(60)  # 限制帧率，减少CPU使用

        # 静息态后等待开始第一张绘图
        self.screen.fill(grey)
        stats.game_score = 0
        paused = False
        first_image_shown = False
        running = True
        current_image_index = 0  # 当前图片索引
        
        # 读取id变量
        with open(f"Behavioral_data/id.txt", "r") as file:
            id = file.read().strip()
        
        while running:
            dt = self.clock.tick(60) / 1000
            
            # 确保背景正确刷新
            self.screen.fill(grey)
            
            user_button2 = Button2(settings, self.screen, f"航天员:{user1}", 20, 20)
            step_button2 = Button(settings, self.screen, "", 1700, 1000)

            mouse_pos = pygame.mouse.get_pos()
            

            
            # 处理键盘和鼠标事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    self.screen.fill(grey)
                elif event.type == pygame.MOUSEBUTTONUP:  # 处理鼠标释放
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max, speed_value, speed_step)
                elif event.type == pygame.MOUSEMOTION:  # 处理鼠标移动
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max, speed_value, speed_step)
                elif event.type == pygame.MOUSEBUTTONDOWN:  # 处理鼠标点击
                    current_time = pygame.time.get_ticks()
                    # 处理按钮事件
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max, speed_value, speed_step)


                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_p:  # P键暂停
                        if not paused:
                            pause_start_time = pygame.time.get_ticks()
                        else:
                            total_pause_time += pygame.time.get_ticks() - pause_start_time
                        paused = not paused
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # +键增加速度
                        speed_value = min(speed_max, speed_value + speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                    elif event.key == pygame.K_MINUS:  # -键降低速度
                        speed_value = max(speed_min, speed_value - speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))

                    elif event.key == pygame.K_SPACE and not paused:  # 空格键下一张（需要到达终点）
                        if not first_image_shown:
                            # 显示第一张图
                            serial_marker(bytes([0x01]))
                            t1, timestamp1 = game_drawing.random_painting(numbers1[0], self, 0)
                            stats.game_score = 1
                            first_image_shown = True
                        elif stats.game_score < 8 and self.level.is_endpoint_reached():
                            # 在进入下一张图前先截图保存当前用户绘制的内容
                            current_image_index = stats.game_score
                            if current_image_index < 8:
                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()
                                
                                # 保存当前绘制内容为post_screenshot
                                post_screenshot_path = f"./Behavioral_data/{id}/subA/output_image/post_screenshot{current_image_index - 1}.png"
                                pygame.image.save(self.screen, post_screenshot_path)
                                
                                serial_marker(bytes([0x01]))
                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers1[1], self, 1)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers1[2], self, 2)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers1[3], self, 3)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers1[4], self, 4)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers1[5], self, 5)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers1[6], self, 6)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers1[7], self, 7)
                                stats.game_score += 1
                                self.level.reset_endpoint_reached()
                        elif stats.game_score == 8:
                            # 确保绘制内容已经显示到屏幕上
                            self.level.run(dt, stats, [], self.screen)
                            pygame.display.update()
                            
                            # 保存最后一张图的post_screenshot
                            post_screenshot_path = f"./Behavioral_data/{id}/subA/output_image/post_screenshot7.png"
                            pygame.image.save(self.screen, post_screenshot_path)
                            
                            t9 = (pygame.time.get_ticks() - total_pause_time) / 1000
                            stats.game_score = 9
                    elif event.key == pygame.K_n and not paused:  # N键下一张（原功能，不需要到达终点）
                        if not first_image_shown:
                            # 显示第一张图
                            serial_marker(bytes([0x01]))
                            t1, timestamp1 = game_drawing.random_painting(numbers1[0], self, 0)
                            stats.game_score = 1
                            first_image_shown = True
                        elif stats.game_score < 8:
                            # 在进入下一张图前先截图保存当前用户绘制的内容
                            current_image_index = stats.game_score
                            if current_image_index < 8:
                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()
                                
                                # 保存当前绘制内容为post_screenshot
                                post_screenshot_path = f"./Behavioral_data/{id}/subA/output_image/post_screenshot{current_image_index - 1}.png"
                                pygame.image.save(self.screen, post_screenshot_path)
                                
                                serial_marker(bytes([0x01]))
                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers1[1], self, 1)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers1[2], self, 2)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers1[3], self, 3)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers1[4], self, 4)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers1[5], self, 5)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers1[6], self, 6)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers1[7], self, 7)
                                stats.game_score += 1
                        elif stats.game_score == 8:
                            # 确保绘制内容已经显示到屏幕上
                            self.level.run(dt, stats, [], self.screen)
                            pygame.display.update()
                            
                            # 保存最后一张图的post_screenshot
                            post_screenshot_path = f"./Behavioral_data/{id}/subA/output_image/post_screenshot7.png"
                            pygame.image.save(self.screen, post_screenshot_path)
                            
                            t9 = (pygame.time.get_ticks() - total_pause_time) / 1000
                            stats.game_score = 9

            # 绘制速度调整按钮
            speed_font = pygame.font.Font(get_font_path(), 50)
            button_font = pygame.font.Font(get_font_path(), 50)
            value_font = pygame.font.Font(get_font_path(), 30)

            # 绘制速度标签
            speed_text = speed_font.render("速度:", True, (0, 0, 0))
            speed_rect = speed_text.get_rect(right=minus_button_rect.left - 10, centery=minus_button_rect.centery)
            self.screen.blit(speed_text, speed_rect)

            # 绘制减速按钮
            minus_color = (150, 150, 150) if speed_value <= speed_min else (100, 149, 237)
            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, (0, 0, 0))
            minus_text_rect = minus_text.get_rect(center=minus_button_rect.center)
            self.screen.blit(minus_text, minus_text_rect)

            # 绘制数值显示
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            speed_level = speed_value_to_level(speed_value)
            value_text = value_font.render(f"{speed_level}", True, (255, 0, 0))
            value_text_rect = value_text.get_rect(center=value_display_rect.center)
            self.screen.blit(value_text, value_text_rect)

            # 绘制加速按钮
            plus_color = (150, 150, 150) if speed_value >= speed_max else (100, 149, 237)
            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, (0, 0, 0))
            plus_text_rect = plus_text.get_rect(center=plus_button_rect.center)
            self.screen.blit(plus_text, plus_text_rect)

            # 显示按键提示
            key_hint_font = pygame.font.Font(get_font_path(), 40)
            if paused:
                step_button2.text = "已暂停"
                hint_text = "按P键继续  |  按Esc键返回主界面"
                hint_color = (0, 0, 0)
            else:
                if first_image_shown and 1 <= stats.game_score <= 8:
                    step_button2.text = f"{stats.game_score} / 8"
                    hint_text = "按P键暂停  |  按空格键下一张"
                    hint_color = (0, 0, 0)
                elif stats.game_score > 8:
                    step_button2.text = "完成"
                    hint_text = "实验完成"
                    hint_color = (0, 255, 0)
                elif not first_image_shown:
                    step_button2.text = "等待开始"
                    hint_text = "按空格键开始第一张图片"
                    hint_color = (0, 0, 0)
                else:
                    step_button2.text = ""
                    hint_text = "按P键暂停  |  按空格键下一张"
                    hint_color = (0, 0, 0)
            
            # 绘制按键提示文本在屏幕上方，避免被绘图界面覆盖
            hint_surface = key_hint_font.render(hint_text, True, hint_color)
            hint_rect = hint_surface.get_rect(center=(settings.screen_width // 2, 50))
            # 添加背景矩形
            bg_rect = pygame.Rect(hint_rect.x - 10, hint_rect.y - 5, hint_rect.width + 20, hint_rect.height + 10)
            pygame.draw.rect(self.screen, (144, 144, 144), bg_rect)
            self.screen.blit(hint_surface, hint_rect)

            if 0 <= stats.game_score < 9:
                for button in [user_button2, step_button2]:
                    gf.update_screen(button)
            self.level.run(dt, stats, [], self.screen)
            pygame.display.update()
            if stats.game_score == 9:
                self.level.clear()
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)
                dataloading(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3, timestamp4,
                            timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time)
                with open(f"Behavioral_data/id.txt", "r") as file:
                    id = file.read()
                with open(f"./Behavioral_data/{id}/subA/data/数据.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    data = [f"图像 {i + 1}  {lines[i].strip()} {lines[i].strip()}" for i in range(8)]
                
                serial_marker(bytes([0x05]))
                user1 = getattr(shared_data, 'user1_mark', '01')
                # 合并显示数据和量表界面
                likert = LikertScale(screen=self.screen, question=f"请{user1}按下键盘按键1到7评估任务难度:",
                                     position=(260, 400),
                                     size=(1400, 500),
                                     highlight_user=user1)
                likert_running = True
                score = None
                while likert_running:
                    self.screen.fill(grey)
                    
                    # 显示数据
                    draw_data(self, self.screen, data, "A")
                    
                    # 处理事件
                    mouse_clicked = False
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_clicked = True
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE: 
                                pygame.quit()
                                sys.exit()
                            else:
                                key_pressed = event.key
                    
                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(), mouse_clicked=mouse_clicked, key_pressed=key_pressed)
                    
                    pygame.display.flip()
                    self.clock.tick(60)
                    if score is not None: 
                        likert_running = False
                        
                # 保存量表结果
                if score is not None:
                    with open(f"Behavioral_data/id.txt", "r") as file: 
                        id = file.read()
                    with open(f"./Behavioral_data/{id}/subA/likert_scale/量表.txt", "w") as f: 
                        f.write(str(score))
                
                stats.game_score = 10
                break

        rest_instructions(self, rest_duration=2)
        # 被试1+2协作阶段
        with open('config.txt', 'w') as f:
            f.truncate(0)
            f.write('3')
        numbers2 = random.sample(range(1, 9), 8)
        self.display_task_instructions_formatted(subject='AB')
        waiting_for_space = True
        while waiting_for_space:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        waiting_for_space = False
            self.clock.tick(60)  # 限制帧率，减少CPU使用

        # 开始被试B，等待显示第一张图片
        self.screen.fill(grey)
        stats.game_score = 11
        paused = False
        pause_start_time = 0
        total_pause_time = 0
        first_image_shown = False
        running = True
        current_image_index = 0  # 当前图片索引
        
        # 速度调整按钮设置
        speed_value = read_speed_value()
        speed_min, speed_max = 50, 150
        speed_step = 25
        
        # 按钮位置设置
        button_y = 30
        button_size = 40
        button_spacing = 40
        
        # 减速按钮
        minus_button_rect = pygame.Rect(settings.screen_width - 250, button_y, button_size, button_size)
        # 加速按钮
        plus_button_rect = pygame.Rect(settings.screen_width - 140, button_y, button_size, button_size)
        # 数值显示区域
        value_display_rect = pygame.Rect(settings.screen_width - 200 , button_y, 55, button_size)

        with open(f"Behavioral_data/id.txt", "r") as file:
            id = file.read().strip()
        while running:
            dt = self.clock.tick(60) / 1000
            
            # 确保背景正确刷新
            self.screen.fill(grey)
            
            # 设置按钮
            user_button2 = Button2(settings, self.screen, f"航天员:{user1}和{user2}", 10, 10)
            step_button2 = Button(settings, self.screen, "", 1700, 1000)

            mouse_pos = pygame.mouse.get_pos()
            

            
            # 处理键盘和鼠标事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_p:  # P键暂停
                        if not paused:
                            pause_start_time = pygame.time.get_ticks()
                        else:
                            total_pause_time += pygame.time.get_ticks() - pause_start_time
                        paused = not paused
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # +键增加速度
                        speed_value = min(speed_max, speed_value + speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                        print(f"速度增加到: {speed_value}")
                    elif event.key == pygame.K_MINUS:  # -键降低速度
                        speed_value = max(speed_min, speed_value - speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                        print(f"速度降低到: {speed_value}")
                    elif event.key == pygame.K_SPACE and not paused:  # 空格键下一张（需要到达终点）
                        if not first_image_shown:
                            # 显示第一张图
                            serial_marker(bytes([0x01]))
                            t1, timestamp1 = game_drawing.random_painting(numbers2[0], self, 11)
                            stats.game_score = 12
                            first_image_shown = True
                        elif stats.game_score < 19 and self.level.is_endpoint_reached():
                            # 在进入下一张图前先截图保存当前用户绘制的内容
                            current_image_index = stats.game_score - 11
                            if current_image_index < 8:
                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()
                                
                                # 保存当前绘制内容为post_screenshot
                                post_screenshot_path = f"./Behavioral_data/{id}/subAB/output_image/post_screenshot{current_image_index - 1}.png"
                                pygame.image.save(self.screen, post_screenshot_path)
                                
                                serial_marker(bytes([0x01]))
                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers2[1], self, 12)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers2[2], self, 13)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers2[3], self, 14)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers2[4], self, 15)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers2[5], self, 16)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers2[6], self, 17)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers2[7], self, 18)
                                stats.game_score += 1
                                self.level.reset_endpoint_reached()
                        elif stats.game_score == 19:
                            # 确保绘制内容已经显示到屏幕上
                            self.level.run(dt, stats, [], self.screen)
                            pygame.display.update()
                            
                            # 保存最后一张图的post_screenshot
                            post_screenshot_path = f"./Behavioral_data/{id}/subAB/output_image/post_screenshot7.png"
                            pygame.image.save(self.screen, post_screenshot_path)
                            t9 = (pygame.time.get_ticks() - total_pause_time) / 1000
                            stats.game_score = 20
                    elif event.key == pygame.K_n and not paused:  # N键下一张（原功能，不需要到达终点）
                        if not first_image_shown:
                            # 显示第一张图
                            serial_marker(bytes([0x01]))
                            t1, timestamp1 = game_drawing.random_painting(numbers2[0], self, 11)
                            stats.game_score = 12
                            first_image_shown = True
                        elif stats.game_score < 19:
                            # 在进入下一张图前先截图保存当前用户绘制的内容
                            current_image_index = stats.game_score - 11
                            if current_image_index < 8:
                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()
                                
                                # 保存当前绘制内容为post_screenshot
                                post_screenshot_path = f"./Behavioral_data/{id}/subAB/output_image/post_screenshot{current_image_index - 1}.png"
                                pygame.image.save(self.screen, post_screenshot_path)
                                
                                serial_marker(bytes([0x01]))
                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers2[1], self, 12)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers2[2], self, 13)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers2[3], self, 14)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers2[4], self, 15)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers2[5], self, 16)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers2[6], self, 17)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers2[7], self, 18)
                                stats.game_score += 1
                        elif stats.game_score == 19:
                            # 确保绘制内容已经显示到屏幕上
                            self.level.run(dt, stats, [], self.screen)
                            pygame.display.update()
                            
                            # 保存最后一张图的post_screenshot
                            post_screenshot_path = f"./Behavioral_data/{id}/subAB/output_image/post_screenshot7.png"
                            pygame.image.save(self.screen, post_screenshot_path)
                            t9 = (pygame.time.get_ticks() - total_pause_time) / 1000
                            stats.game_score = 20

            # 绘制速度调整按钮
            speed_font = pygame.font.Font(get_font_path(), 50)
            button_font = pygame.font.Font(get_font_path(), 50)
            value_font = pygame.font.Font(get_font_path(), 30)
            

            
            # 绘制速度标签
            speed_text = speed_font.render("速度:", True, (0, 0, 0))
            speed_rect = speed_text.get_rect(right=minus_button_rect.left - 10, centery=minus_button_rect.centery)
            self.screen.blit(speed_text, speed_rect)
            
            # 绘制减速按钮
            minus_color = (150, 150, 150) if speed_value <= speed_min else (255, 100, 100)
            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, (0, 0, 0))
            minus_text_rect = minus_text.get_rect(center=minus_button_rect.center)
            self.screen.blit(minus_text, minus_text_rect)
            
            # 绘制数值显示
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            speed_level = speed_value_to_level(speed_value)
            value_text = value_font.render(f"{speed_level}", True, (255, 0, 0))
            value_text_rect = value_text.get_rect(center=value_display_rect.center)
            self.screen.blit(value_text, value_text_rect)
            
            # 绘制加速按钮
            plus_color = (150, 150, 150) if speed_value >= speed_max else (100, 255, 100)
            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, (0, 0, 0))
            plus_text_rect = plus_text.get_rect(center=plus_button_rect.center)
            self.screen.blit(plus_text, plus_text_rect)

            # 显示按键提示
            key_hint_font = pygame.font.Font(get_font_path(), 40)
            if paused:
                step_button2.text = "已暂停"
                hint_text = "按P键继续  |  按ESC键退出"
                hint_color = (0, 0, 0)
            else:
                if first_image_shown and 12 <= stats.game_score <= 19:
                    step_button2.text = f"{stats.game_score - 11} / 8"
                    hint_text = "按P键暂停  |  按空格键下一张"
                    hint_color = (0, 0, 0)
                elif stats.game_score > 19:
                    step_button2.text = "完成"
                    hint_text = "实验完成"
                    hint_color = (0, 255, 0)
                elif not first_image_shown:
                    step_button2.text = "等待开始"
                    hint_text = "按空格键开始第一张图片"
                    hint_color = (0, 0, 0)
                else:
                    step_button2.text = ""
                    hint_text = "按P键暂停  |  按空格键下一张"
                    hint_color = (0, 0, 0)
            
            # 绘制按键提示文本在屏幕上方，避免被绘图界面覆盖
            hint_surface = key_hint_font.render(hint_text, True, hint_color)
            hint_rect = hint_surface.get_rect(center=(settings.screen_width // 2, 50))
            # 添加背景矩形
            bg_rect = pygame.Rect(hint_rect.x - 10, hint_rect.y - 5, hint_rect.width + 20, hint_rect.height + 10)
            pygame.draw.rect(self.screen, (144, 144, 144), bg_rect)
            self.screen.blit(hint_surface, hint_rect)

            if 10 < stats.game_score < 20:
                for button in [user_button2, step_button2]:
                    gf.update_screen(button)
            # 更新游戏等级
            self.level.run(dt, stats, [], self.screen)
            pygame.display.update()
            # 处理游戏结束逻辑
            if stats.game_score == 20:
                self.level.clear()  # 调用clear方法彻底清除
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)
                dataloading2(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3, timestamp4,
                             timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time)
                with open(f"Behavioral_data/id.txt", "r") as file:
                    id = file.read()
                with open(f"./Behavioral_data/{id}/subAB/data/数据.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    data = [f"图像{i + 1} {lines[i].strip()} {lines[i].strip()}" for i in range(8)]
                
                serial_marker(bytes([0x05]))
                user1 = getattr(shared_data, 'user1_mark', '01')
                # 合并显示数据和量表界面
                likert = LikertScale(screen=self.screen, question=f"请{user1}按下键盘按键1到7评估任务难度:",
                                     position=(260, 400),
                                     size=(1400, 500),
                                     highlight_user=user1)
                likert_running = True
                score = None
                while likert_running:
                    self.screen.fill(grey)
                    
                    # 显示数据
                    draw_data(self, self.screen, data, "B")
                    
                    # 处理事件
                    mouse_clicked = False
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_clicked = True
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
                            else:
                                key_pressed = event.key
                    
                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(), mouse_clicked=mouse_clicked, key_pressed=key_pressed)
                    
                    pygame.display.flip()
                    self.clock.tick(60)
                    if score is not None: 
                        likert_running = False
                        
                # 保存量表结果
                if score is not None:
                    with open(f"Behavioral_data/id.txt", "r") as file: 
                        id = file.read()
                    with open(f"./Behavioral_data/{id}/subAB/likert_scale/量表.txt", "w") as f: 
                        f.write(str(score))
                
                stats.game_score = 21
                break
        serial_marker(bytes([0x07]))
        rest_instructions(self, 2)  # 120秒休息倒计时
        stats.game_score += 1

        # 被试1+3协作阶段
        with open('config.txt', 'w') as f:
            f.truncate(0)
            f.write('3')
        numbers3 = random.sample(range(1, 9), 8)
        self.display_task_instructions_formatted(subject='AC')
        waiting_for_space = True
        while waiting_for_space:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        waiting_for_space = False
            self.clock.tick(60)  # 限制帧率，减少CPU使用

        # 开始A+B协作，直接显示第一张图片
        self.screen.fill(grey)
        stats.game_score = 23
        paused = False
        pause_start_time = 0
        total_pause_time = 0
        first_image_shown = False
        running = True
        current_image_index = 0  # 当前图片索引
        
        # 速度调整按钮设置
        speed_value = read_speed_value()
        speed_min, speed_max = 50, 150
        speed_step = 25
        
        # 按钮位置设置
        button_y = 30
        button_size = 40
        button_spacing = 40
        
        # 减速按钮
        minus_button_rect = pygame.Rect(settings.screen_width - 250, button_y, button_size, button_size)
        # 加速按钮
        plus_button_rect = pygame.Rect(settings.screen_width - 140, button_y, button_size, button_size)
        # 数值显示区域
        value_display_rect = pygame.Rect(settings.screen_width - 200 , button_y, 55, button_size)


        with open(f"Behavioral_data/id.txt", "r") as file:
            id = file.read().strip()
        while running:
            dt = self.clock.tick(60) / 1000

            # 确保背景正确刷新
            self.screen.fill(grey)

            # 设置按钮
            user_button2 = Button2(settings, self.screen, f"航天员:{user1}和{user3}", 10, 10)
            step_button2 = Button(settings, self.screen, "", 1700, 1000)

            mouse_pos = pygame.mouse.get_pos()
            # 检查按钮点击

            # 处理键盘事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    self.screen.fill(grey)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_p:  # P键暂停
                        if not paused:
                            pause_start_time = pygame.time.get_ticks()
                        else:
                            total_pause_time += pygame.time.get_ticks() - pause_start_time
                        paused = not paused
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # +键增加速度
                        speed_value = min(speed_max, speed_value + speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                        print(f"速度增加到: {speed_value}")
                    elif event.key == pygame.K_MINUS:  # -键降低速度
                        speed_value = max(speed_min, speed_value - speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                        print(f"速度降低到: {speed_value}")
                    elif event.key == pygame.K_SPACE and not paused:  # 空格键下一张（需要到达终点）
                        if not first_image_shown:
                            # 显示第一张图
                            serial_marker(bytes([0x01]))
                            t1, timestamp1 = game_drawing.random_painting(numbers3[0], self, 23)
                            stats.game_score = 24
                            first_image_shown = True
                        elif stats.game_score < 31 and self.level.is_endpoint_reached():
                            current_image_index = stats.game_score - 23
                            if current_image_index < 8:
                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()
                                
                                # 保存当前绘制内容为post_screenshot
                                with open(f"Behavioral_data/id.txt", "r") as file:
                                    id = file.read().strip()
                                post_screenshot_path = f"./Behavioral_data/{id}/subAC/output_image/post_screenshot{current_image_index - 1}.png"
                                pygame.image.save(self.screen, post_screenshot_path)
                                
                                serial_marker(bytes([0x01]))
                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers3[1], self, 24)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers3[2], self, 25)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers3[3], self, 26)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers3[4], self, 27)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers3[5], self, 28)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers3[6], self, 29)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers3[7], self, 30)
                                stats.game_score += 1
                                self.level.reset_endpoint_reached()
                        elif stats.game_score == 31:

                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()

                                # 保存最后一张图的post_screenshot
                                post_screenshot_path = f"./Behavioral_data/{id}/subAC/output_image/post_screenshot7.png"
                                pygame.image.save(self.screen, post_screenshot_path)
                                t9 = (pygame.time.get_ticks() - total_pause_time) / 1000
                                stats.game_score = 32
                    elif event.key == pygame.K_n and not paused:  # N键下一张（原功能，不需要到达终点）
                        if not first_image_shown:
                            # 显示第一张图
                            serial_marker(bytes([0x01]))
                            t1, timestamp1 = game_drawing.random_painting(numbers3[0], self, 23)
                            stats.game_score = 24
                            first_image_shown = True
                        elif stats.game_score < 31:
                            current_image_index = stats.game_score - 23
                            if current_image_index < 8:
                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()
                                
                                # 保存当前绘制内容为post_screenshot
                                with open(f"Behavioral_data/id.txt", "r") as file:
                                    id = file.read().strip()
                                post_screenshot_path = f"./Behavioral_data/{id}/subAC/output_image/post_screenshot{current_image_index - 1}.png"
                                pygame.image.save(self.screen, post_screenshot_path)
                                
                                serial_marker(bytes([0x01]))
                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers3[1], self, 24)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers3[2], self, 25)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers3[3], self, 26)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers3[4], self, 27)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers3[5], self, 28)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers3[6], self, 29)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers3[7], self, 30)
                                stats.game_score += 1
                        elif stats.game_score == 31:
                            # 确保绘制内容已经显示到屏幕上
                            self.level.run(dt, stats, [], self.screen)
                            pygame.display.update()

                            # 保存最后一张图的post_screenshot
                            post_screenshot_path = f"./Behavioral_data/{id}/subAC/output_image/post_screenshot7.png"
                            pygame.image.save(self.screen, post_screenshot_path)
                            t9 = (pygame.time.get_ticks() - total_pause_time) / 1000
                            stats.game_score = 32

            # 绘制速度调整按钮
            speed_font = pygame.font.Font(get_font_path(), 50)
            button_font = pygame.font.Font(get_font_path(), 50)
            value_font = pygame.font.Font(get_font_path(), 30)



            # 绘制速度标签
            speed_text = speed_font.render("速度:", True, (0, 0, 0))
            speed_rect = speed_text.get_rect(right=minus_button_rect.left - 10, centery=minus_button_rect.centery)
            self.screen.blit(speed_text, speed_rect)
            
            # 绘制减速按钮
            minus_color = (150, 150, 150) if speed_value <= speed_min else (255, 100, 100)
            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, (0, 0, 0))
            minus_text_rect = minus_text.get_rect(center=minus_button_rect.center)
            self.screen.blit(minus_text, minus_text_rect)
            
            # 绘制数值显示
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            speed_level = speed_value_to_level(speed_value)
            value_text = value_font.render(f"{speed_level}", True, (255, 0, 0))
            value_text_rect = value_text.get_rect(center=value_display_rect.center)
            self.screen.blit(value_text, value_text_rect)
            
            # 绘制加速按钮
            plus_color = (150, 150, 150) if speed_value >= speed_max else (100, 255, 100)
            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, (0, 0, 0))
            plus_text_rect = plus_text.get_rect(center=plus_button_rect.center)
            self.screen.blit(plus_text, plus_text_rect)

            # 显示按键提示
            key_hint_font = pygame.font.Font(get_font_path(), 40)
            if paused:
                step_button2.text = "已暂停"
                hint_text = "按P键继续  |  按ESC键退出"
                hint_color = (0, 0, 0)
            else:
                if first_image_shown and 24 <= stats.game_score <= 31:
                    step_button2.text = f"{stats.game_score - 23} / 8"
                    hint_text = "按P键暂停  |  按空格键下一张"
                    hint_color = (0, 0, 0)
                elif stats.game_score > 31:
                    step_button2.text = "完成"
                    hint_text = "实验完成"
                    hint_color = (0, 255, 0)
                elif not first_image_shown:
                    step_button2.text = "等待开始"
                    hint_text = "按空格键开始第一张图片"
                    hint_color = (0, 0, 0)
                else:
                    step_button2.text = ""
                    hint_text = "按P键暂停  |  按空格键下一张"
                    hint_color = (0, 0, 0)
            
            # 绘制按键提示文本在屏幕上方，避免被绘图界面覆盖
            hint_surface = key_hint_font.render(hint_text, True, hint_color)
            hint_rect = hint_surface.get_rect(center=(settings.screen_width // 2, 50))
            # 添加背景矩形
            bg_rect = pygame.Rect(hint_rect.x - 10, hint_rect.y - 5, hint_rect.width + 20, hint_rect.height + 10)
            pygame.draw.rect(self.screen, (144, 144, 144), bg_rect)
            self.screen.blit(hint_surface, hint_rect)

            if 22 < stats.game_score < 32:
                for button in [user_button2, step_button2]:
                    gf.update_screen(button)
                # 更新滑块显示位置
            # 更新游戏等级
            self.level.run(dt, stats, [], self.screen)
            pygame.display.update()
            # 处理游戏结束逻辑
            if stats.game_score == 32:
                self.level.clear()  # 调用clear方法彻底清除
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)
                dataloading3(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3, timestamp4,
                             timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time)
                with open(f"Behavioral_data/id.txt", "r") as file:
                    id = file.read()
                with open(f"./Behavioral_data/{id}/subAC/data/数据.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    data = [f"图像{i + 1}{lines[i].strip()}{lines[i].strip()}" for i in range(8)]
                
                serial_marker(bytes([0x05]))
                
                # 合并显示数据和量表界面
                likert = LikertScale(screen=self.screen, question=f"请{user1}按下键盘按键1到7评估任务难度:",
                                     position=(260, 400),
                                     size=(1400, 500),
                                     highlight_user=user1)
                likert_running = True
                score = None
                while likert_running:
                    self.screen.fill(grey)
                    
                    # 显示数据
                    draw_data(self, self.screen, data, "AB")
                    
                    # 处理事件
                    mouse_clicked = False
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_clicked = True
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
                            else:
                                key_pressed = event.key
                    
                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(), mouse_clicked=mouse_clicked, key_pressed=key_pressed)
                    
                    pygame.display.flip()
                    self.clock.tick(60)
                    if score is not None: 
                        likert_running = False
                        
                # 保存量表结果
                if score is not None:
                    with open(f"Behavioral_data/id.txt", "r") as file: 
                        id = file.read()
                    with open(f"./Behavioral_data/{id}/subAC/likert_scale/量表.txt", "w") as f: 
                        f.write(str(score))
                
                stats.game_score = 33
                break
        self.display_meditation_instructions()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
                        self.screen.fill(grey)
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.clock.tick(60)  # 限制帧率，减少CPU使用

        self.screen.fill(grey)
        line_length = 20
        pygame.draw.line(self.screen, green, (910, 540), (1010, 540), line_length)
        pygame.draw.line(self.screen, green, (960, 490), (960, 590), line_length)
        pygame.display.update()
        serial_marker(bytes([0x04]))
        start_ticks = pygame.time.get_ticks()
        running = True
        countdown_time = 2
        paused = False
        pause_start_time = 0
        total_pause_time = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            remaining_time = max(0, countdown_time - elapsed_time)
            if remaining_time == 0:
                running = False
                self.screen.fill(grey)
            self.clock.tick(60)  # 限制帧率，减少CPU使用
        # 实验结束
        self.display_end_screen()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            self.clock.tick(60)  # 限制帧率，减少CPU使用

    import pygame

    def display_flowchart_instructions(self):
        """以流程图的形式显示实验指导语"""
        # --- Colors and Fonts Initialization ---
        BG_COLOR = (230, 230, 230)
        BOX_COLOR = (160, 160, 160)
        TEXT_COLOR = (0, 0, 0)
        ARROW_COLOR = (160, 160, 160)
        GREEN_COLOR = green

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        try:
            title_font = pygame.font.Font(get_font_path(), 72)  # 增大标题字体
            header_font = pygame.font.Font(get_font_path(), 42)  # 增大头部字体
            main_font = pygame.font.Font(get_font_path(), 48)    # 增大主字体
            sub_font = pygame.font.Font(get_font_path(), 34)     # 增大子字体
            desc_font = pygame.font.Font(get_font_path(), 48)    # 新增描述字体
            prompt_font = pygame.font.Font(get_font_path(), 68)
            key_info_font = pygame.font.Font(get_font_path(), 60)
        except IOError:
            # Fallback to default system font if 'msyh.ttc' is not found
            title_font = pygame.font.SysFont(None, 75)
            header_font = pygame.font.SysFont(None, 45)
            main_font = pygame.font.SysFont(None, 55)
            sub_font = pygame.font.SysFont(None, 40)
            desc_font = pygame.font.SysFont(None, 40)
            prompt_font = pygame.font.SysFont(None, 50)
            key_info_font = pygame.font.SysFont(None, 30)

        self.screen.fill(BG_COLOR)

        # --- Title ---
        title_surf = title_font.render("实验流程", True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(screen_width / 2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # --- 添加流程图描述 ---
        desc_text = "本实验包含5个阶段，按顺序依次进行，每个阶段都有明确的时间限制和任务要求"
        desc_surf = desc_font.render(desc_text, True, TEXT_COLOR)
        desc_rect = desc_surf.get_rect(center=(screen_width / 2, 140))
        self.screen.blit(desc_surf, desc_rect)
        
        user1 = getattr(shared_data, 'user1_mark', None)
        user2 = getattr(shared_data, 'user2_mark', None)
        user3 = getattr(shared_data, 'user3_mark', None)
        # --- Updated Flowchart Steps ---
        # The core change is in this data structure to reflect the new experimental flow.
        flow_steps = [
            {"header": "第一部分", "main": f"{user1}静息任务", "sub": "（2分钟）"},
            {"header": "第二部分", "main": f"{user1}单独绘图", "sub": "（7分钟）"},
            {"header": "第三部分", "main": f"{user1}&{user2}合作绘图", "sub": "（7分钟）"},
            {"header": "第四部分", "main": f"{user1}&{user3}合作绘图", "sub": "（7分钟）"},
            {"header": "第五部分", "main": f"{user1}静息任务", "sub": "（2分钟）"}
        ]

        # --- Layout Calculations for Centering the Flowchart ---
        box_width, box_height = 340, 220  # 增大流程图方框尺寸
        box_gap = 60  # 增大间距
        total_width = len(flow_steps) * box_width + (len(flow_steps) - 1) * box_gap
        start_x = (screen_width - total_width) / 2
        y_pos = screen_height / 2 - box_height / 2 + 30  # 向下调整位置

        # --- Drawing Flowchart Boxes and Arrows ---
        box_rects = []
        for i, step in enumerate(flow_steps):
            box_x = start_x + i * (box_width + box_gap)
            rect = pygame.Rect(box_x, y_pos, box_width, box_height)
            box_rects.append(rect)

            # Draw the box
            pygame.draw.rect(self.screen, BOX_COLOR, rect, border_radius=25)

            # Render and position the text inside the box
            header_surf = header_font.render(step["header"], True, TEXT_COLOR)
            header_rect = header_surf.get_rect(center=(rect.centerx, rect.top + 50))
            self.screen.blit(header_surf, header_rect)

            main_surf = main_font.render(step["main"], True, TEXT_COLOR)
            main_rect = main_surf.get_rect(center=(rect.centerx, rect.centery + 10))
            self.screen.blit(main_surf, main_rect)

            sub_surf = sub_font.render(step["sub"], True, TEXT_COLOR)
            sub_rect = sub_surf.get_rect(center=(rect.centerx, rect.bottom - 45))
            self.screen.blit(sub_surf, sub_rect)

        # Draw connecting arrows (修复箭头白色小正方体问题 - 确保线条和箭头头部完美对齐)
        for i in range(len(box_rects) - 1):
            start_point = box_rects[i].midright
            end_point = box_rects[i + 1].midleft
            
            # 计算箭头参数
            arrow_size = 20
            line_start = (start_point[0] + 15, start_point[1])
            # 箭头线条的终点要与箭头头部的后端对齐
            line_end = (end_point[0] - 15 - arrow_size, end_point[1])
            arrow_tip = (end_point[0] - 15, end_point[1])  # 箭头尖端
            
            # 绘制箭头线条 (从起点到箭头后端)
            pygame.draw.line(self.screen, ARROW_COLOR, line_start, line_end, 6)
            
            # 绘制箭头头部三角形 (确保与线条无缝连接)
            arrow_points = [
                arrow_tip,                                             # 箭头尖端
                (line_end[0], line_end[1] - arrow_size//2),           # 左上角 (与线条终点对齐)
                (line_end[0], line_end[1] + arrow_size//2)            # 左下角 (与线条终点对齐)
            ]
            pygame.draw.polygon(self.screen, ARROW_COLOR, arrow_points)

        # --- Bottom Prompt and Key Information ---
        # This part remains the same but is positioned lower.
        prompt_y_center = screen_height - 150
        prompt_parts = [("按 ", TEXT_COLOR), ("空格键", GREEN_COLOR), (" 即可开始", TEXT_COLOR)]
        prompt_surfaces = [prompt_font.render(text, True, color) for text, color in prompt_parts]
        total_prompt_width = sum(s.get_width() for s in prompt_surfaces)
        current_x = (screen_width - total_prompt_width) / 2
        for surf in prompt_surfaces:
            rect = surf.get_rect(left=current_x, centery=prompt_y_center)
            self.screen.blit(surf, rect)
            current_x += surf.get_width()

        key_info_y_bottom = screen_height - 40
        key_info_parts = [("实验中可按 ", TEXT_COLOR), ("P", GREEN_COLOR), (" 键暂停  |  按 ", TEXT_COLOR),
                          ("ESC", GREEN_COLOR), (" 键退出", TEXT_COLOR)]
        key_info_surfaces = [key_info_font.render(text, True, color) for text, color in key_info_parts]
        total_key_info_width = sum(s.get_width() for s in key_info_surfaces)
        current_x = (screen_width - total_key_info_width) / 2
        for surf in key_info_surfaces:
            rect = surf.get_rect(left=current_x, bottom=key_info_y_bottom)
            self.screen.blit(surf, rect)
            current_x += surf.get_width()

        pygame.display.update()

    def display_task_instructions_formatted(self, subject='A'):
        """
        以简化风格动态绘制绘图任务的指导语。
        【已按照用户最终指定的顺序重排布局，代码完整无省略】
        """
        # --- 参数定义 ---
        BG_COLOR = (230, 230, 230)
        TEXT_COLOR = (0, 0, 0)
        GREEN_COLOR = (0, 255, 0)
        RED = (255, 0, 0)
        PROMPT_GREEN_COLOR = (0, 180, 0)

        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(BG_COLOR)

        # --- 字体加载 ---
        try:
            font_name = get_font_path()
            title_font = pygame.font.Font(font_name, 65)
            main_font = pygame.font.Font(font_name, 44)
            main_font_bold = pygame.font.Font(font_name, 48)
            main_font_bold.set_bold(True)
            key_font = pygame.font.Font(font_name, 42)
            prompt_font = pygame.font.Font(font_name, 50)
        except (IOError, TypeError):
            # 如果自定义字体加载失败，则使用系统后备字体
            title_font = pygame.font.SysFont('sans-serif', 70)
            main_font = pygame.font.SysFont('sans-serif', 45)
            main_font_bold = pygame.font.SysFont('sans-serif', 45, bold=True)
            key_font = pygame.font.SysFont('sans-serif', 40)
            prompt_font = pygame.font.SysFont('sans-serif', 55)

        user1 = getattr(shared_data, 'user1_mark', '用户1')
        user2 = getattr(shared_data, 'user2_mark', '用户2')
        user3 = getattr(shared_data, 'user3_mark', '用户3')

        # --- 辅助函数 (完整定义) ---
        def render_composite_line(y, line_def):
            """渲染由普通文本和按键方框组成的复合行"""
            total_width = 0
            surfaces = []
            for item in line_def:
                content, font, part_type = item
                if part_type == "key":
                    text_surf = font.render(content, True, (0, 0, 0))
                    total_width += text_surf.get_width() + 16  # 加上左右内边距
                    surfaces.append({'type': 'key', 'content': content, 'font': font})
                else:
                    text_surf = font.render(content, True, TEXT_COLOR)
                    total_width += text_surf.get_width()
                    surfaces.append({'type': 'text', 'surf': text_surf})

            x_pos = (screen_w - total_width) / 2
            for item in surfaces:
                if item['type'] == "key":
                    temp_surf = item['font'].render(item['content'], True, (0, 0, 0))
                    key_rect_width = temp_surf.get_width() + 16
                    draw_key_box(self.screen, item['content'], item['font'],
                                 (x_pos + key_rect_width / 2, y + item['font'].get_height() / 2 - 4))
                    x_pos += key_rect_width
                else:
                    self.screen.blit(item['surf'], (x_pos, y))
                    x_pos += item['surf'].get_width()

        def render_line(parts, x, y):
            """渲染带有粗体和下划线的文本行"""
            for text, font, color in parts:
                surf = font.render(text, True, color)
                self.screen.blit(surf, (x, y))
                if font == main_font_bold:
                    pygame.draw.line(self.screen, color, (x, y + surf.get_height() - 2),
                                     (x + surf.get_width(), y + surf.get_height() - 2), 2)
                x += surf.get_width()

        # --- 布局绘制开始 ---
        y_pos = 160
        line_height = 65

        # =================================================================
        # 步骤 1: 标题
        # =================================================================
        if subject == 'A':
            title_text = f"{user1}单人绘图任务指导语"
        elif subject == 'B':
            title_text = f"{user2}单人绘图任务指导语"
        elif subject == 'C':
            title_text = f"{user3}单人绘图任务指导语"
        elif subject == 'AB':
            title_text = f"{user1}和{user2}合作绘图任务指导语"
        else:  # AC
            title_text = f"{user1}和{user3}合作绘图任务指导语"

        title_surf = title_font.render(title_text, True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(screen_w / 2, 80))
        self.screen.blit(title_surf, title_rect)

        # =================================================================
        # 步骤 2: 指明操作者
        # =================================================================
        if subject == 'A':
            role_text = f"请{user1}绘图，{user2}和{user3}休息"
        elif subject == 'B':
            role_text = f"请{user2}绘图，{user1}和{user3}休息"
        elif subject == 'C':
            role_text = f"请{user3}绘图，{user1}和{user2}休息"
        elif subject == 'AB':
            role_text = f"请{user1}和{user2}绘图，{user3}休息"
        else:  # AC
            role_text = f"请{user1}和{user3}绘图，{user2}休息"

        role_surf = main_font.render(role_text, True, TEXT_COLOR)
        role_rect = role_surf.get_rect(center=(screen_w / 2, y_pos))
        self.screen.blit(role_surf, role_rect)
        y_pos += line_height

        # =================================================================
        # 步骤 3: 任务描述
        # =================================================================
        if subject == 'A':
            parts1 = [(f"{user1}航天员控制键盘沿", main_font, TEXT_COLOR), ("黑色轨迹", main_font_bold, TEXT_COLOR),
                      ("从", main_font, TEXT_COLOR), ("绿色起点", main_font_bold, TEXT_COLOR),
                      ("移至", main_font, TEXT_COLOR), ("红色终点", main_font_bold, TEXT_COLOR)]
        elif subject == 'B':
            parts1 = [(f"{user2}航天员控制键盘沿", main_font, TEXT_COLOR), ("黑色轨迹", main_font_bold, TEXT_COLOR),
                      ("从", main_font, TEXT_COLOR), ("绿色起点", main_font_bold, TEXT_COLOR),
                      ("移至", main_font, TEXT_COLOR), ("红色终点", main_font_bold, TEXT_COLOR)]
        elif subject == 'C':
            parts1 = [(f"{user3}航天员控制键盘沿", main_font, TEXT_COLOR), ("黑色轨迹", main_font_bold, TEXT_COLOR),
                      ("从", main_font, TEXT_COLOR), ("绿色起点", main_font_bold, TEXT_COLOR),
                      ("移至", main_font, TEXT_COLOR), ("红色终点", main_font_bold, TEXT_COLOR)]
        elif subject == 'AB':
            parts1 = [(f"{user1}和{user2}航天员控制键盘沿", main_font, TEXT_COLOR),
                      ("黑色轨迹", main_font_bold, TEXT_COLOR), ("从", main_font, TEXT_COLOR),
                      ("绿色起点", main_font_bold, TEXT_COLOR), ("移至", main_font, TEXT_COLOR),
                      ("红色终点", main_font_bold, TEXT_COLOR)]
        else:  # AC
            parts1 = [(f"{user1}和{user3}航天员控制键盘沿", main_font, TEXT_COLOR),
                      ("黑色轨迹", main_font_bold, TEXT_COLOR), ("从", main_font, TEXT_COLOR),
                      ("绿色起点", main_font_bold, TEXT_COLOR), ("移至", main_font, TEXT_COLOR),
                      ("红色终点", main_font_bold, TEXT_COLOR)]

        total_width_parts1 = sum(f.render(t, True, c).get_width() for t, f, c in parts1)
        render_line(parts1, (screen_w - total_width_parts1) / 2, y_pos)
        y_pos += line_height + 20

        # =================================================================
        # 步骤 4: 任务流程图
        # =================================================================
        diagram_y = y_pos
        steps = ["任务开始", "沿轨迹绘图", "到达终点"]
        box_w, box_h = 220, 100
        gap = 80
        total_width_diagram = len(steps) * box_w + (len(steps) - 1) * gap
        start_x = (screen_w - total_width_diagram) / 2
        for i, step_text in enumerate(steps):
            box_x = start_x + i * (box_w + gap)
            box_rect = pygame.Rect(box_x, diagram_y, box_w, box_h)
            pygame.draw.rect(self.screen, (200, 200, 200), box_rect, border_radius=10)
            pygame.draw.rect(self.screen, TEXT_COLOR, box_rect, 2, border_radius=10)
            if i == 0:
                pygame.draw.rect(self.screen, GREEN_COLOR, (box_rect.centerx - 15, box_rect.centery - 15, 30, 30))
            elif i == 1:
                path_points = [(box_rect.left + 30, box_rect.centery + 15), (box_rect.centerx, box_rect.centery - 15),
                               (box_rect.right - 30, box_rect.centery + 15)]
                pygame.draw.lines(self.screen, TEXT_COLOR, False, path_points, 4)
            else:
                pygame.draw.rect(self.screen, RED, (box_rect.centerx - 15, box_rect.centery - 15, 30, 30))
            label_surf = main_font.render(step_text, True, TEXT_COLOR)
            label_rect = label_surf.get_rect(center=(box_rect.centerx, box_rect.bottom + 30))
            self.screen.blit(label_surf, label_rect)
            if i < len(steps) - 1:
                arrow_start = (box_rect.right + 10, box_rect.centery)
                arrow_end = (box_rect.right + gap - 10, box_rect.centery)
                pygame.draw.line(self.screen, TEXT_COLOR, arrow_start, arrow_end, 4)
                pygame.draw.polygon(self.screen, TEXT_COLOR,
                                    [(arrow_end[0], arrow_end[1]), (arrow_end[0] - 15, arrow_end[1] - 8),
                                     (arrow_end[0] - 15, arrow_end[1] + 8)])
        y_pos += box_h + 80

        # =================================================================
        # 步骤 5: 每个人的分工
        # =================================================================
        if subject in ['AB', 'AC']:
            line3_surf = main_font.render("本轮为合作任务：", True, TEXT_COLOR)
            line3_rect = line3_surf.get_rect(center=(screen_w / 2, y_pos))
            self.screen.blit(line3_surf, line3_rect)
            y_pos += line_height

        if subject == 'A':
            line_def = [(f"请{user1}:使用 ", main_font, "text"), ("W", key_font, "key"),
                        (" 控制上, ", main_font, "text"), ("A", key_font, "key"), (" 控制左, ", main_font, "text"),
                        ("S", key_font, "key"), (" 控制下, ", main_font, "text"), ("D", key_font, "key"),
                        (" 控制右。", main_font, "text")]
        elif subject == 'B':
            line_def = [(f"请{user2}:使用 ", main_font, "text"), ("↑", key_font, "key"),
                        (" 控制上, ", main_font, "text"), ("←", key_font, "key"), (" 控制左, ", main_font, "text"),
                        ("↓", key_font, "key"), (" 控制下, ", main_font, "text"), ("→", key_font, "key"),
                        (" 控制右。", main_font, "text")]
        elif subject == 'C':
            line_def = [(f"请{user3}:使用 ", main_font, "text"), ("↑", key_font, "key"),
                        (" 控制上, ", main_font, "text"), ("←", key_font, "key"), (" 控制左, ", main_font, "text"),
                        ("↓", key_font, "key"), (" 控制下, ", main_font, "text"), ("→", key_font, "key"),
                        (" 控制右。", main_font, "text")]
        elif subject == 'AB':
            line_def = [(f"请{user1}: 使用", main_font, "text"), ("A", key_font, "key"), ("控制左 ", main_font, "text"),
                        ("D", key_font, "key"), ("控制右", main_font, "text"), (f"，请{user2}:使用 ", main_font, "text"),
                        ("↑", key_font, "key"), ("控制上 ", main_font, "text"), ("↓", key_font, "key"),
                        ("控制下。", main_font, "text")]
        else:  # AC
            line_def = [(f"请{user1}: 使用", main_font, "text"), ("A", key_font, "key"), ("控制左 ", main_font, "text"),
                        ("D", key_font, "key"), ("控制右", main_font, "text"), (f"，请{user3}:使用 ", main_font, "text"),
                        ("↑", key_font, "key"), ("控制上 ", main_font, "text"), ("↓", key_font, "key"),
                        ("控制下。", main_font, "text")]

        render_composite_line(y_pos, line_def)
        y_pos += line_height + 20

        # =================================================================
        # 步骤 6: 速度调整
        # =================================================================
        button_text = [("您还可以通过键盘上的: ", main_font, "text"), (" -", key_font, "key"), ("+", key_font, "key"),
                       ("按钮来调整绘图速度", main_font, "text")]
        render_composite_line(y_pos, button_text)
        y_pos += line_height + 50
        # 速度调整示意图
        diagram_bg_rect = pygame.Rect(0, 0, 500, 100)
        diagram_bg_rect.center = (screen_w / 2, y_pos)
        speed_label_surf = main_font.render("速度:", True, TEXT_COLOR)
        label_rect = speed_label_surf.get_rect(center=(diagram_bg_rect.centerx - 160, diagram_bg_rect.centery))
        self.screen.blit(speed_label_surf, label_rect)

        minus_demo_rect = pygame.Rect(0, 0, 50, 50)
        minus_demo_rect.center = (diagram_bg_rect.centerx - 55, diagram_bg_rect.centery)
        pygame.draw.rect(self.screen, (100, 149, 237), minus_demo_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), minus_demo_rect, 2, border_radius=5)
        minus_text = main_font.render("-", True, TEXT_COLOR)
        minus_text_rect = minus_text.get_rect(center=minus_demo_rect.center)
        self.screen.blit(minus_text, minus_text_rect)

        value_demo_rect = pygame.Rect(0, 0, 50, 50)
        value_demo_rect.center = (diagram_bg_rect.centerx, diagram_bg_rect.centery)
        pygame.draw.rect(self.screen, (240, 240, 240), value_demo_rect, border_radius=3)
        pygame.draw.rect(self.screen, (100, 100, 100), value_demo_rect, 2, border_radius=3)
        value_text = main_font.render("1", True, RED)
        value_text_rect = value_text.get_rect(center=value_demo_rect.center)
        self.screen.blit(value_text, value_text_rect)

        plus_demo_rect = pygame.Rect(0, 0, 50, 50)
        plus_demo_rect.center = (diagram_bg_rect.centerx + 55, diagram_bg_rect.centery)
        pygame.draw.rect(self.screen, (100, 149, 237), plus_demo_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), plus_demo_rect, 2, border_radius=5)
        plus_text = main_font.render("+", True, TEXT_COLOR)
        plus_text_rect = plus_text.get_rect(center=plus_demo_rect.center)
        self.screen.blit(plus_text, plus_text_rect)

        # =================================================================
        # 步骤 7: 底部提示
        # =================================================================
        prompt_parts = [("准备好后，请按 ", prompt_font, TEXT_COLOR), ("空格键", prompt_font, PROMPT_GREEN_COLOR),
                        (" 开始实验", prompt_font, TEXT_COLOR)]
        total_prompt_width = sum(f.render(t, True, c).get_width() for t, f, c in prompt_parts)
        current_x = (screen_w - total_prompt_width) / 2
        prompt_y_pos = screen_h - 100
        for text, font, color in prompt_parts:
            surf = font.render(text, True, color)
            prompt_rect = surf.get_rect(left=current_x, centery=prompt_y_pos)
            self.screen.blit(surf, prompt_rect)
            current_x += surf.get_width()

        pygame.display.update()

    def display_meditation_instructions(self, title=None, instructions=None, special_words=None):
        """显示冥想指导语"""
        BLACK = (0, 0, 0)
        GREEN = green

        self.screen.fill(grey)
        user1 = getattr(shared_data, 'user1_mark', None)
        try:
            font_large = pygame.font.Font(get_font_path(), 78)
            font_medium = pygame.font.Font(get_font_path(), 65)
        except:
            font_large = pygame.font.SysFont(None, 48)
            font_medium = pygame.font.SysFont(None, 40)

        if title is None: title = f"航天员{user1}进行2分钟静息态"
        if instructions is None:
            instructions = ["放松身体 保持静止", "避免思考 放松大脑", "睁开双眼 减少眨眼",
                            "双手双脚 避免交叉", "按空格键开始"]
        if special_words is None:
            special_words = { "空格键": GREEN}

        title_surface = font_large.render(title, True, BLACK)
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_surface, title_rect)

        y_position = 300
        line_spacing = 125
        for line in instructions:
            text_parts = [(line, BLACK)]
            for word, color in special_words.items():
                if word in line:
                    before, _, after = line.partition(word)
                    text_parts = [(before, BLACK), (word, color), (after, BLACK)]
                    break

            total_width = sum(font_medium.render(text, True, color).get_width() for text, color in text_parts)
            x_position = self.screen.get_width() // 2 - total_width // 2

            for text, color in text_parts:
                if not text: continue
                text_surface = font_medium.render(text, True, color)
                self.screen.blit(text_surface, (x_position, y_position))
                x_position += text_surface.get_width()

            y_position += line_spacing
        pygame.display.update()
    def display_end_screen(self):
        """显示实验结束画面，保持与整体风格一致"""
        BG_COLOR = (128, 128, 128)  # 与其他界面保持一致的灰色背景
        BOX_COLOR = (144, 197, 114)  # 与流程图相同的绿色框
        TEXT_COLOR = (0, 0, 0)
        ACCENT_COLOR = (144, 238, 144)  # 浅绿色强调
        TITLE_COLOR = (0, 0, 0)

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # 字体设置
        try:
            title_font = pygame.font.Font(get_font_path(), 88)
            subtitle_font = pygame.font.Font(get_font_path(), 78)
            note_font = pygame.font.Font(get_font_path(), 78)
        except IOError:
            title_font = pygame.font.SysFont(None, 100)
            subtitle_font = pygame.font.SysFont(None, 78)
            note_font = pygame.font.SysFont(None, 45)

        # 清空屏幕
        self.screen.fill(BG_COLOR)

        # 主标题
        title_surf = title_font.render("恭喜您完成实验", True, TITLE_COLOR)
        title_rect = title_surf.get_rect(center=(screen_width / 2, 220))
        self.screen.blit(title_surf, title_rect)

        # 副标题
        subtitle_surf = subtitle_font.render("数据已保存", True, TITLE_COLOR)
        subtitle_rect = subtitle_surf.get_rect(center=(screen_width / 2, 420))
        self.screen.blit(subtitle_surf, subtitle_rect)


        # 底部提示


        # Break the note into parts, each with its own text and color
        note_parts = [
            ("按", TEXT_COLOR),  # Part 1: Black
            ("Esc", ACCENT_COLOR),  # Part 2: Green
            ("返回主界面", TEXT_COLOR)  # Part 3: Black
        ]

        # --- Render each part into its own surface ---
        note_surfaces = [note_font.render(text, True, color) for text, color in note_parts]

        # --- Calculate layout for centering ---
        # Calculate the total width of all parts combined
        total_width = sum(surf.get_width() for surf in note_surfaces)
        # Determine the starting x-position to center the whole message
        current_x = (screen_width - total_width) / 2

        # --- Draw each part sequentially ---
        for surf in note_surfaces:
            # Define the position for the current part
            note_rect = surf.get_rect(left=current_x, centery=screen_height - 100)
            # Draw the current part onto the screen
            self.screen.blit(surf, note_rect)
            # Move the x-position for the next part
            current_x += surf.get_width()

        # 添加装饰元素 - 简单的完成图标
        # 在标题上方绘制一个简单的勾号
        check_center = (screen_width / 2, 120)
        check_size = 40

        # 绘制勾号背景圆圈
        pygame.draw.circle(self.screen, ACCENT_COLOR, check_center, check_size)
        pygame.draw.circle(self.screen, TEXT_COLOR, check_center, check_size, 3)

        # 绘制勾号
        check_points = [
            (check_center[0] - 15, check_center[1]),
            (check_center[0] - 5, check_center[1] + 10),
            (check_center[0] + 15, check_center[1] - 10)
        ]
        pygame.draw.lines(self.screen, TEXT_COLOR, False, check_points, 5)

        pygame.display.update()

def draw_data(self, screen, data, subject_type=None):
    """优化的数据显示函数"""
    percentages = []
    times = []
    import re
    time_pattern = re.compile(r'绘图时长：([\d.]+)')
    percentage_pattern = re.compile(r'百分比：([\d.]+)%')

    for line in data:
        try:
            time_match = time_pattern.search(line)
            percentage_match = percentage_pattern.search(line)
            if time_match: times.append(float(time_match.group(1)))
            if percentage_match: percentages.append(float(percentage_match.group(1)))
        except (ValueError, AttributeError) as e:
            print(f"处理行时出错: {str(e)}")
            continue

    if not percentages or not times:
        error_text = "无法解析数据"
        text_surface = self.font.render(error_text, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text_surface, text_rect)
        return

    total_time = sum(times)
    avg_percentage = sum(percentages) / len(percentages) if percentages else 0
    summary_lines = [f"任务平均完成度： {avg_percentage:.2f}%", f"任务总用时： {total_time:.2f}秒"]

    for i, text in enumerate(summary_lines):
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 200 + i * 100))
        screen.blit(text_surface, text_rect)


def dataloading(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3,
                timestamp4, timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time=0):
    with open("Behavioral_data/id.txt", "r") as file:
        id = file.read()
    base_path = f"./Behavioral_data/{id}/subA/output_image"
    
    # 检查基准图像是否存在
    reference_path = f"{base_path}/post_screenshot-1.png"
    if not os.path.exists(reference_path):
        print(f"Warning: Reference image not found: {reference_path}")
        return
    
    image = cv2.imread(reference_path)
    if image is None:
        print(f"Warning: Could not read reference image: {reference_path}")
        return
    
    pre_images = []
    post_images = []
    
    # 安全地读取图像文件
    for i in range(8):
        pre_path = f"{base_path}/pre_screenshot{i}.png"
        post_path = f"{base_path}/post_screenshot{i}.png"
        
        if os.path.exists(pre_path):
            pre_img = cv2.imread(pre_path)
            if pre_img is not None:
                pre_images.append(pre_img)
            else:
                print(f"Warning: Could not read pre image: {pre_path}")
                pre_images.append(None)
        else:
            print(f"Warning: Pre image not found: {pre_path}")
            pre_images.append(None)
            
        if os.path.exists(post_path):
            post_img = cv2.imread(post_path)
            if post_img is not None:
                post_images.append(post_img)
            else:
                print(f"Warning: Could not read post image: {post_path}")
                post_images.append(None)
        else:
            print(f"Warning: Post image not found: {post_path}")
            post_images.append(None)
    
    time_params = [(t1, t2), (t2, t3), (t3, t4), (t4, t5), (t5, t6), (t6, t7), (t7, t8), (t8, t9)]
    timestamps = [timestamp1, timestamp2, timestamp3, timestamp4, timestamp5, timestamp6, timestamp7, timestamp8]
    
    for i in range(8):
        if pre_images[i] is not None and post_images[i] is not None:
            calculate_pixel_difference(image, pre_images[i], post_images[i], time_params[i][0], time_params[i][1],
                                       timestamps[i], total_pause_time)
    
    for post_image in post_images:
        if post_image is not None:
            deviation_area1(post_image)

def dataloading2(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3,
                 timestamp4, timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time=0):
    # 读取ID
    with open("Behavioral_data/id.txt", "r") as file:
        id = file.read()
    base_path = f"./Behavioral_data/{id}/subAB/output_image"
    
    # 检查基准图像是否存在
    reference_path = f"{base_path}/post_screenshot-1.png"
    if not os.path.exists(reference_path):
        print(f"Warning: Reference image not found: {reference_path}")
        return
    
    image = cv2.imread(reference_path)
    if image is None:
        print(f"Warning: Could not read reference image: {reference_path}")
        return
    
    pre_images = []
    post_images = []
    
    # 安全地读取图像文件
    for i in range(8):
        pre_path = f"{base_path}/pre_screenshot{i}.png"
        post_path = f"{base_path}/post_screenshot{i}.png"
        
        if os.path.exists(pre_path):
            pre_img = cv2.imread(pre_path)
            if pre_img is not None:
                pre_images.append(pre_img)
            else:
                print(f"Warning: Could not read pre image: {pre_path}")
                pre_images.append(None)
        else:
            print(f"Warning: Pre image not found: {pre_path}")
            pre_images.append(None)
            
        if os.path.exists(post_path):
            post_img = cv2.imread(post_path)
            if post_img is not None:
                post_images.append(post_img)
            else:
                print(f"Warning: Could not read post image: {post_path}")
                post_images.append(None)
        else:
            print(f"Warning: Post image not found: {post_path}")
            post_images.append(None)
    
    time_params = [(t1, t2), (t2, t3), (t3, t4), (t4, t5),
                   (t5, t6), (t6, t7), (t7, t8), (t8, t9)]
    timestamps = [timestamp1, timestamp2, timestamp3, timestamp4,
                  timestamp5, timestamp6, timestamp7, timestamp8]
    
    for i in range(8):
        if pre_images[i] is not None and post_images[i] is not None:
            calculate_pixel_difference2(image, pre_images[i], post_images[i],
                                        time_params[i][0], time_params[i][1], timestamps[i], total_pause_time)
    
    for post_image in post_images:
        if post_image is not None:
            deviation_area2(post_image)
def dataloading3(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3,
                 timestamp4, timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time=0):
    # 读取ID
    with open("Behavioral_data/id.txt", "r") as file:
        id = file.read()
    base_path = f"./Behavioral_data/{id}/subAC/output_image"
    
    # 检查基准图像是否存在
    reference_path = f"{base_path}/post_screenshot-1.png"
    if not os.path.exists(reference_path):
        print(f"Warning: Reference image not found: {reference_path}")
        return
    
    image = cv2.imread(reference_path)
    if image is None:
        print(f"Warning: Could not read reference image: {reference_path}")
        return
    
    pre_images = []
    post_images = []
    
    # 安全地读取图像文件
    for i in range(8):
        pre_path = f"{base_path}/pre_screenshot{i}.png"
        post_path = f"{base_path}/post_screenshot{i}.png"
        
        if os.path.exists(pre_path):
            pre_img = cv2.imread(pre_path)
            if pre_img is not None:
                pre_images.append(pre_img)
            else:
                print(f"Warning: Could not read pre image: {pre_path}")
                pre_images.append(None)
        else:
            print(f"Warning: Pre image not found: {pre_path}")
            pre_images.append(None)
            
        if os.path.exists(post_path):
            post_img = cv2.imread(post_path)
            if post_img is not None:
                post_images.append(post_img)
            else:
                print(f"Warning: Could not read post image: {post_path}")
                post_images.append(None)
        else:
            print(f"Warning: Post image not found: {post_path}")
            post_images.append(None)
    
    # 时间参数和时间戳打包成列表
    time_params = [(t1, t2), (t2, t3), (t3, t4), (t4, t5),
                   (t5, t6), (t6, t7), (t7, t8), (t8, t9)]
    timestamps = [timestamp1, timestamp2, timestamp3, timestamp4,
                  timestamp5, timestamp6, timestamp7, timestamp8]
    
    # 计算像素差异
    for i in range(8):
        if pre_images[i] is not None and post_images[i] is not None:
            calculate_pixel_difference3(image, pre_images[i], post_images[i],
                                        time_params[i][0], time_params[i][1], timestamps[i], total_pause_time)
    
    # 计算偏差区域
    for post_image in post_images:
        if post_image is not None:
            deviation_area3(post_image)


def loading_animation(self, WINDOW_WIDTH, WINDOW_HEIGHT, font):
    clock = pygame.time.Clock()
    dots = [".", "..", "..."]
    dot_index = 0
    last_update = time.time()
    update_interval = 0.5
    animation_duration = 2
    start_time = time.time()
    while time.time() - start_time < animation_duration:
        current_time = time.time()
        if current_time - last_update >= update_interval:
            dot_index = (dot_index + 1) % len(dots)
            last_update = current_time
        self.screen.fill(grey)
        text = f"加载中{dots[dot_index]}"
        text_surface = font.render(text, True, black)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        clock.tick(60)


def rest_instructions(self, rest_duration=120):
    """
    显示休息指导文本并进行倒计时
    rest_duration: 休息时长（秒），默认120秒（2分钟）
    """
    import time
    
    # 颜色定义
    BLACK = (0, 0, 0)
    GREEN = green
    RED = (255, 100, 100)

    # 加载字体
    try:
        font_large = pygame.font.Font(get_font_path(), 58)
        font_medium = pygame.font.Font(get_font_path(), 50)
        font_countdown = pygame.font.Font(get_font_path(), 72)
    except:
        # 如果没有黑体字库，使用默认字体
        font_large = pygame.font.SysFont(None, 58)
        font_medium = pygame.font.SysFont(None, 50)
        font_countdown = pygame.font.SysFont(None, 72)

    # 文本内容
    title = "休息时间"
    instruction_lines = [
        "放松身体，休息期间请不要离开座位",
        "双眼可离开屏幕，适当放松",
        "倒计时结束后自动开始下一阶段"
    ]

    # 倒计时循环
    start_time = time.time()
    clock = pygame.time.Clock()
    
    while True:
        elapsed = time.time() - start_time
        remaining = max(0, rest_duration - elapsed)
        
        if remaining <= 0:
            break
            
        # 清空屏幕
        self.screen.fill(grey)
        
        # 显示标题
        title_surface = font_large.render(title, True, BLACK)
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(title_surface, title_rect)
        
        # 显示指导文本
        y_pos = 280
        for line in instruction_lines:
            text_surface = font_medium.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, y_pos))
            self.screen.blit(text_surface, text_rect)
            y_pos += 60
        
        # 显示倒计时
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        countdown_text = f"{minutes:02d}:{seconds:02d}"
        
        # 最后30秒变红色
        countdown_color = RED if remaining <= 30 else GREEN
        countdown_surface = font_countdown.render(countdown_text, True, countdown_color)
        countdown_rect = countdown_surface.get_rect(center=(self.screen.get_width() // 2, 550))
        self.screen.blit(countdown_surface, countdown_rect)
        
        # 检查退出事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(60)



if __name__ == '__main__':

    game = Game()
    game.run()