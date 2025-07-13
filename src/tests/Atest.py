#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import cv2
import numpy as np
import pygame
import sys
from src.core import game_function_simulation as gf
from src.utils import shared_data
from src.ui.Button import Button, Button2
from src.data.Deviation_area import deviation_area1
from src.utils.game_stats import GameStats
from src.data.handle_slider_event import handle_button_event
from src.core.level import Level
from src.config.settings import *
import random
from src.ui.likert_scale import LikertScale
import os
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

# --- 全局配置：模式开关 ---
IS_TRAINING_MODE = True

# --- 全局参数 ---
dots_time = []
green = (50, 128, 50)
black = (0, 0, 0)
grey = (230, 230, 230)
RED = (255, 0, 0)


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
        pygame.init()
        # 初始化速度为1级别（对应速度值50）
        with open('scroll_value.txt', 'w') as f:
            f.write('50')
        settings = Settings()
        self.screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), pygame.FULLSCREEN)
        self.font = pygame.font.Font(get_font_path(), 40)
        pygame.display.set_caption('人员①训练')
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.screen.fill(grey)

    def run(self):
        settings = Settings()
        stats = GameStats(settings)
        user_mark = getattr(shared_data, 'user1_mark', '01')
        ROOT_DATA_FOLDER = "Training_Behavioral_data" if IS_TRAINING_MODE else "Behavioral_data"
        PARTICIPANT_ID_FOLDER = "subA"

        if not os.path.exists(ROOT_DATA_FOLDER):
            os.makedirs(f"{ROOT_DATA_FOLDER}")
            print(f"已创建文件夹: {ROOT_DATA_FOLDER}")

        def extract_number(mark):
            if mark and isinstance(mark, str):
                if '-' in mark: return mark.split('-')[-1]
                import re
                match = re.search(r'\d+$', mark)
                if match: return match.group()
            return mark

        user_id_display = extract_number(user_mark)

        game_drawing = GameDrawing()

        t1, t2, t3, t4 = None, None, None, None
        timestamp1, timestamp2, timestamp3 = None, None, None

        with open('config.txt', 'w') as f:
            f.truncate(0)
            f.write('1')
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
        value_display_rect = pygame.Rect(settings.screen_width - 200, button_y, 55, button_size)

        self.display_task_instructions_formatted(subject='A')
        waiting_for_space = True
        while waiting_for_space:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting_for_space = False
            self.clock.tick(60)

        numbers = random.sample(range(1, 9), 3)
        stats.game_score = 0
        paused, pause_start_time, total_pause_time = False, 0, 0
        first_image_shown, running = False, True

        id_file_path = f"{ROOT_DATA_FOLDER}/id.txt"
        try:
            if not os.path.exists(id_file_path):
                with open(id_file_path, "w") as file: file.write("training_001")
            with open(id_file_path, "r") as file:
                id = file.read().strip()
        except Exception as e:
            print(f"处理ID文件时出错: {e}")
            pygame.quit()
            sys.exit()

        output_image_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/output_image"
        data_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/data"
        likert_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/likert_scale"
        os.makedirs(output_image_folder, exist_ok=True)
        os.makedirs(data_folder, exist_ok=True)
        os.makedirs(likert_folder, exist_ok=True)

        self.screen.fill(grey)
        pygame.image.save(self.screen, f"{output_image_folder}/post_screenshot-1.png")

        action_pending = False

        while running:
            dt = self.clock.tick(60) / 1000
            self.screen.fill(grey)

            # --- 1. 事件处理 ---
            mouse_pos = pygame.mouse.get_pos()
            user_button = Button2(settings, self.screen, f"航天员：{user_id_display}", 10, 10)
            step_button = Button(settings, self.screen, "", 1700, 1000)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                                      speed_value, speed_step)
                elif event.type == pygame.MOUSEMOTION:  # 处理鼠标移动
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                                      speed_value, speed_step)
                elif event.type == pygame.MOUSEBUTTONDOWN:  # 处理鼠标点击
                    current_time = pygame.time.get_ticks()
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                                      speed_value, speed_step)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                    elif event.key == pygame.K_p:
                        paused = not paused
                        if paused:
                            pause_start_time = pygame.time.get_ticks()
                        else:
                            total_pause_time += pygame.time.get_ticks() - pause_start_time
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # +键增加速度
                        speed_value = min(speed_max, speed_value + speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                    elif event.key == pygame.K_MINUS:  # -键降低速度
                        speed_value = max(speed_min, speed_value - speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                    if event.key == pygame.K_SPACE and not paused:
                        action_pending = True

            # --- 2. 绘制所有UI和游戏内容 ---
            # 速度调整按钮设置

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

            self.level.run(dt, stats, [], self.screen)
            for button in [user_button, step_button]: gf.update_screen(button)

            # --- 3. 根据标志执行截图和状态更新 ---
            if action_pending:
                if not first_image_shown:
                    t1, timestamp1 = game_drawing.random_painting(numbers[0], self, 0)
                    pygame.image.save(self.screen, f"{output_image_folder}/pre_screenshot0.png")
                    stats.game_score = 1
                    first_image_shown = True
                elif stats.game_score < 3:
                    current_image_index = stats.game_score - 1
                    pygame.image.save(self.screen, f"{output_image_folder}/post_screenshot{current_image_index}.png")
                    if stats.game_score == 1:
                        t2, timestamp2 = game_drawing.random_painting(numbers[1], self, 1)
                        pygame.image.save(self.screen, f"{output_image_folder}/pre_screenshot1.png")
                    elif stats.game_score == 2:
                        t3, timestamp3 = game_drawing.random_painting(numbers[2], self, 2)
                        pygame.image.save(self.screen, f"{output_image_folder}/pre_screenshot2.png")
                    stats.game_score += 1
                elif stats.game_score == 3:
                    pygame.image.save(self.screen, f"{output_image_folder}/post_screenshot2.png")
                    t4 = (pygame.time.get_ticks() - total_pause_time) / 1000
                    stats.game_score = 4
                action_pending = False

            # --- 4. 绘制提示文本和进度 ---
            key_hint_font = pygame.font.Font(get_font_path(), 60)
            if paused:
                step_button.text, hint_text = "已暂停", "按P键继续 | 按ESC键退出"
            else:
                if first_image_shown and 1 <= stats.game_score <= 3:
                    step_button.text = f"{stats.game_score} / 3"
                    hint_text = "按P键暂停 | 按空格键继续"
                elif stats.game_score > 3:
                    step_button.text, hint_text = "完成", "任务已完成"
                else:
                    step_button.text, hint_text = "等待开始", "按空格键开始"

            hint_surface = key_hint_font.render(hint_text, True, black)
            hint_rect = hint_surface.get_rect(center=(settings.screen_width // 2, 50))
            self.screen.blit(hint_surface, hint_rect)
            step_button.draw_button()

            pygame.display.update()

            # --- 5. 任务结束 ---
            if stats.game_score == 4:
                self.level.clear()
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)
                dataloading_1(t1, t2, t3, t4, timestamp1, timestamp2, timestamp3, ROOT_DATA_FOLDER, id,
                              PARTICIPANT_ID_FOLDER)
                data_path = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/data/数据.txt"
                likert_path = f"{likert_folder}/量表.txt"
                try:
                    with open(data_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        data = [f"图像{i + 1} {lines[i].strip()}" for i in range(min(3, len(lines)))]
                        while len(data) < 3:
                            data.append(f"图像{len(data) + 1} 绘图时长：0.00秒, 完成百分比：0.00%")
                except FileNotFoundError:
                    print(f"数据文件 {data_path} 未找到，将使用默认值。")
                    data = [f"图像{i + 1} 绘图时长：0.00秒, 完成百分比：0.00%" for i in range(3)]
                user1 = getattr(shared_data, 'user1_mark', '01')
                likert = LikertScale(screen=self.screen, question=f"请{user1}按下键盘按键1到7评估任务难度:",
                                     position=(260, 400),
                                     size=(1400, 500),
                                     highlight_user=user1)

                likert_running, score = True, None
                while likert_running:
                    self.screen.fill(grey)
                    draw_data(self, self.screen, data)
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_clicked = False
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN: mouse_clicked = True
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                            else: key_pressed = event.key
                    score = likert.update(mouse_pos=mouse_pos, mouse_clicked=mouse_clicked, key_pressed=key_pressed)
                    pygame.display.flip()
                    if score is not None: likert_running = False
                if score is not None:
                    with open(likert_path, "w") as f: f.write(str(score))
                running = False

        self.display_training_complete_instructions()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit();
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    wait = False
            self.clock.tick(60)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            self.clock.tick(60)

    def display_task_instructions_formatted(self, subject='A'):
        """
        以简化风格动态绘制绘图任务的指导语。
        【已按照用户最终指定的顺序重排布局，代码完整无省略】
        """
        # --- 参数定义 ---
        BG_COLOR = (211, 211, 211)
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

    def display_training_complete_instructions(self):
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
            title_font = pygame.font.Font(get_font_path(), 68)
            subtitle_font = pygame.font.Font(get_font_path(), 58)
            note_font = pygame.font.Font(get_font_path(), 58)
        except IOError:
            title_font = pygame.font.SysFont(None, 80)
            subtitle_font = pygame.font.SysFont(None, 58)
            note_font = pygame.font.SysFont(None, 35)

        # 清空屏幕
        self.screen.fill(BG_COLOR)

        # 主标题
        title_surf = title_font.render("恭喜您完成练习", True, TITLE_COLOR)
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


def draw_data(self, screen, data):
    percentages, times = [], []
    summary_font = pygame.font.Font(get_font_path(), 60)
    import re
    time_pattern, percentage_pattern = re.compile(r'绘图时长：([\d.]+)'), re.compile(r'百分比：([\d.]+)%')
    for line in data:
        try:
            if (t := time_pattern.search(line)): times.append(float(t.group(1)))
            if (p := percentage_pattern.search(line)): percentages.append(float(p.group(1)))
        except (ValueError, AttributeError):
            continue
    if not percentages or not times: return
    avg_percentage = sum(percentages) / len(percentages) if percentages else 0
    summary_lines = [f"任务平均完成度: {avg_percentage:.2f}%", f"任务总用时: {sum(times):.2f}秒"]
    for i, text in enumerate(summary_lines):
        text_surface = summary_font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, text_surface.get_rect(center=(screen.get_width() / 2, 200 + i * 100)))


def dataloading_1(t1, t2, t3, t4, timestamp1, timestamp2, timestamp3, root_folder, id, participant_folder):
    base_path = f"./{root_folder}/{id}/{participant_folder}/output_image"
    data_file_path = f"./{root_folder}/{id}/{participant_folder}/data/数据.txt"

    if os.path.exists(data_file_path):
        os.remove(data_file_path)

    pre_images = [cv2.imread(f"{base_path}/pre_screenshot{i}.png") for i in range(3)]
    post_images = [cv2.imread(f"{base_path}/post_screenshot{i}.png") for i in range(3)]
    time_params = [(t1, t2), (t2, t3), (t3, t4)]
    timestamps = [timestamp1, timestamp2, timestamp3]

    for i in range(3):
        if pre_images[i] is not None and post_images[i] is not None:
            calculate_pixel_difference_test(pre_images[i], post_images[i], time_params[i][0], time_params[i][1],
                                            timestamps[i], root_folder, id, participant_folder)
    for post_image in post_images:
        if post_image is not None:
            deviation_area1(post_image)


def loading_animation(self, WINDOW_WIDTH, WINDOW_HEIGHT, font):
    clock, dots, dot_index, last_update = pygame.time.Clock(), [".", "..", "..."], 0, time.time()
    start_time = time.time()
    while time.time() - start_time < 2:
        if time.time() - last_update >= 0.5:
            dot_index = (dot_index + 1) % len(dots)
            last_update = time.time()
        self.screen.fill(grey)
        text_surface = font.render(f"数据处理中{dots[dot_index]}", True, black)
        self.screen.blit(text_surface, text_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)))
        pygame.display.flip()
        clock.tick(60)


def calculate_pixel_difference_test(image1, image2, t1, t2, timestamp, root_folder, id, participant_folder):
    x, y, width, height = 0, 50, 1920, 920
    image1_cropped = image1[y:y + height, x:x + width]
    image2_cropped = image2[y:y + height, x:x + width]
    gray_origin = cv2.cvtColor(image1_cropped, cv2.COLOR_BGR2GRAY)
    black_mask = (gray_origin < 50)
    hsv_image2 = cv2.cvtColor(image2_cropped, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 50, 50]);
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv_image2, lower_green, upper_green)
    green_mask = (green_mask > 0)
    overlap_mask = black_mask & green_mask
    total_pixels = np.sum(black_mask)
    overlap_pixels = np.sum(overlap_mask)
    overlap_percentage = (overlap_pixels / total_pixels * 100) if total_pixels > 0 else 0
    time_diff = t2 - t1 if t1 and t2 else 0
    output_path = f"./{root_folder}/{id}/{participant_folder}/data/数据.txt"
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(
            f"有效像素: {overlap_pixels}   总像素: {total_pixels}   百分比：{overlap_percentage:.2f}%   绘图时长：{time_diff:.2f} \n")


if __name__ == '__main__':
    game = Game()
    game.run()