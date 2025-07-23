#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import cv2
import numpy as np
import pygame
import sys
import os
import random
import re

from src.core import game_function_simulation as gf
from src.utils import shared_data
from src.ui.Button import Button, Button3, Button4
from src.data.Deviation_area import deviation_area1
from src.utils.game_stats import GameStats
from src.data.handle_slider_event import handle_button_event
from src.core.level import Level
from src.config.settings import *
from src.ui.likert_scale import LikertScale
from src.core.paint import GameDrawing
from src.utils.font_utils import get_font_path

# --- 全局参数 ---
green = (50, 128, 50)
black = (0, 0, 0)
grey = (230, 230, 230)
RED = (255, 0, 0)


def speed_level_to_value(level): return level


def speed_value_to_level(value): return int(value)


def read_speed_value():
    """读取scroll_value.txt中的速度值，如果文件不存在或值无效则返回默认值50"""
    try:
        with open('scroll_value.txt', 'r') as f:
            return max(1, min(100, int(f.read().strip())))
    except (FileNotFoundError, ValueError):
        with open('scroll_value.txt', 'w') as f:
            f.write('50')
        return 50


def draw_key_box(screen, text, font, center_pos):
    """绘制一个带有边框的按键方框。"""
    KEY_BG_COLOR, KEY_BORDER_COLOR, KEY_TEXT_COLOR = (255, 255, 255), (100, 100, 100), black
    PADDING_X, PADDING_Y = 8, 4
    text_surf = font.render(text, True, KEY_TEXT_COLOR)
    box_rect = pygame.Rect((0, 0), (text_surf.get_width() + PADDING_X * 2, text_surf.get_height() + PADDING_Y * 2))
    box_rect.center = center_pos
    pygame.draw.rect(screen, KEY_BG_COLOR, box_rect, border_radius=5)
    pygame.draw.rect(screen, KEY_BORDER_COLOR, box_rect, 2, border_radius=5)
    screen.blit(text_surf, text_surf.get_rect(center=box_rect.center))


def show_confirm_dialog(screen, title, message):
    """显示一个标准化的确认对话框，返回 True (确认) 或 False (取消)"""
    original_screen = screen.copy()
    screen_width, screen_height = screen.get_size()
    dialog_width, dialog_height = 800, 450
    dialog_rect = pygame.Rect((screen_width - dialog_width) // 2, (screen_height - dialog_height) // 2, dialog_width,
                              dialog_height)
    try:
        title_font, msg_font, btn_font, hint_font = [pygame.font.Font(get_font_path(), size) for size in
                                                     [60, 50, 50, 35]]
    except:
        title_font, msg_font, btn_font, hint_font = [pygame.font.Font(None, size) for size in [60, 50, 50, 35]]

    btn_w, btn_h, btn_spacing = 220, 65, 65
    btns_start_x = dialog_rect.x + (dialog_rect.width - (2 * btn_w + btn_spacing)) // 2
    btn_y = dialog_rect.y + dialog_rect.height - 120
    yes_button = pygame.Rect(btns_start_x, btn_y, btn_w, btn_h)
    no_button = pygame.Rect(btns_start_x + btn_w + btn_spacing, btn_y, btn_w, btn_h)
    yes_hover, no_hover = False, False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_n]):
                screen.blit(original_screen, (0, 0));
                pygame.display.flip();
                return False
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_y]:
                screen.blit(original_screen, (0, 0));
                pygame.display.flip();
                return True
            if event.type == pygame.MOUSEMOTION:
                yes_hover, no_hover = yes_button.collidepoint(event.pos), no_button.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if yes_button.collidepoint(event.pos): screen.blit(original_screen,
                                                                   (0, 0)); pygame.display.flip(); return True
                if no_button.collidepoint(event.pos): screen.blit(original_screen,
                                                                  (0, 0)); pygame.display.flip(); return False

        screen.blit(original_screen, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA);
        overlay.fill((0, 0, 0, 128));
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (255, 255, 255), dialog_rect, border_radius=20)
        pygame.draw.rect(screen, (85, 85, 85), dialog_rect, 2, border_radius=20)

        title_surf = title_font.render(title, True, (0, 0, 0));
        screen.blit(title_surf, title_surf.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 60)))
        msg_surf = msg_font.render(message, True, (0, 0, 0));
        screen.blit(msg_surf, msg_surf.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 160)))

        # 绘制按钮和按键提示
        for btn, is_hover, text, hint_text in [(yes_button, yes_hover, "是", "按Y键"),
                                               (no_button, no_hover, "否", "按N键")]:
            btn_bg = (240, 240, 240) if is_hover else (255, 255, 255)
            btn_border = (153, 153, 153) if is_hover else (204, 204, 204)
            pygame.draw.rect(screen, btn_bg, btn, border_radius=25)
            pygame.draw.rect(screen, btn_border, btn, 2, border_radius=25)
            btn_surf = btn_font.render(text, True, (0, 0, 0));
            screen.blit(btn_surf, btn_surf.get_rect(center=btn.center))
            hint_surf = hint_font.render(hint_text, True, (136, 136, 136));
            screen.blit(hint_surf, hint_surf.get_rect(center=(btn.centerx, btn.bottom + 25)))

        pygame.display.flip()
        clock.tick(60)


class Game:
    def __init__(self):
        pygame.init()
        with open('scroll_value.txt', 'w') as f: f.write('50')
        settings = Settings()
        self.screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), pygame.FULLSCREEN)
        self.font = pygame.font.Font(get_font_path(), 40)
        pygame.display.set_caption('人员①&②合作训练')
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.screen.fill(grey)

    def render_text_with_green_keys(self, text, font, surface, center_pos):
        """渲染带有高亮按键提示的文本"""
        GREEN_COLOR, BLACK_COLOR = (0, 255, 0), (0, 0, 0)
        parts = re.split(r'(P|Esc|空格键)', text)
        surfaces = [font.render(part, True, GREEN_COLOR) if part in ['P', 'Esc', '空格键'] else font.render(part, True,
                                                                                                            BLACK_COLOR)
                    for part in parts if part]
        total_width = sum(s.get_width() for s in surfaces)
        current_x, y = center_pos[0] - total_width / 2, center_pos[1] - surfaces[0].get_height() / 2
        for s in surfaces:
            surface.blit(s, (current_x, y));
            current_x += s.get_width()

    def run(self):
        # ------------------- 初始化设置 -------------------
        settings = Settings()
        stats = GameStats(settings)
        user1_mark = getattr(shared_data, 'user1_mark', '01')
        user2_mark = getattr(shared_data, 'user2_mark', '02')

        # 核心配置：定义此脚本的角色
        ROOT_DATA_FOLDER = "Training_Behavioral_data"  # 训练数据根目录
        PARTICIPANT_ID_FOLDER = "subA+B"  # 本次训练的特定文件夹
        TOTAL_IMAGES = 3  # 训练任务总图片数

        # ------------------- 文件与目录设置 -------------------
        id_file_path = f"{ROOT_DATA_FOLDER}/id.txt"
        try:
            os.makedirs(ROOT_DATA_FOLDER, exist_ok=True)
            if not os.path.exists(id_file_path):
                with open(id_file_path, "w") as file: file.write("training_001")
            with open(id_file_path, "r") as file:
                id = file.read().strip()
        except Exception as e:
            print(f"处理ID文件时出错: {e}");
            pygame.quit();
            sys.exit()

        # 确保所有需要的子文件夹都存在
        output_image_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/output_image"
        data_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/data"
        likert_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/likert_scale"
        for folder in [output_image_folder, data_folder, likert_folder]:
            os.makedirs(folder, exist_ok=True)

        user_id1 = re.search(r'\d+$', user1_mark).group() if re.search(r'\d+$', user1_mark) else user1_mark
        user_id2 = re.search(r'\d+$', user2_mark).group() if re.search(r'\d+$', user2_mark) else user2_mark
        game_drawing = GameDrawing()

        timestamps = [None] * TOTAL_IMAGES
        time_records = [None] * (TOTAL_IMAGES + 1)
        with open('config.txt', 'w') as f:
            f.truncate(0); f.write('3')  # '3' 代表双人合作模式

        # ------------------- UI元素初始化 -------------------
        speed_value = read_speed_value()
        speed_min, speed_max, speed_step = 0, 100, 10
        button_states = {'minus_pressed': False, 'plus_pressed': False, 'last_change_time': 0}
        button_y, button_size, button_spacing = 10, 60, 40
        minus_button_rect = pygame.Rect(settings.screen_width - 275, button_y, button_size, button_size)
        plus_button_rect = pygame.Rect(settings.screen_width - 130, button_y, button_size, button_size)
        value_display_rect = pygame.Rect(settings.screen_width - 210, button_y, 75, button_size)

        # ------------------- 显示指导语并等待开始 -------------------
        self.display_task_instructions_formatted(subject='AB')
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"): pygame.quit(); sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
            self.clock.tick(60)

        # ------------------- 游戏主循环初始化 -------------------
        numbers = random.sample(range(1, 9), TOTAL_IMAGES)
        # 【关键】恢复原有的计分逻辑，这些特定数值可能关联到其他模块
        stats.game_score = 23  # AB合作阶段的起始分数
        paused, pause_start_time, total_pause_time = False, 0, 0
        running = True

        self.screen.fill(grey)
        pygame.image.save(self.screen, f"{output_image_folder}/post_screenshot-1.png")

        # 【关键】自动显示第一张图片，无需按键
        time_records[0], timestamps[0] = game_drawing.random_painting(numbers[0], self, 11)  # 合作模式从索引11开始
        pygame.image.save(self.screen, f"{output_image_folder}/pre_screenshot0.png")
        stats.game_score = 24  # 更新分数为进行中

        # ------------------- 游戏主循环 -------------------
        while running:
            dt = self.clock.tick(60) / 1000
            self.screen.fill(grey)

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                                      speed_value, speed_step, button_states)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"): pygame.quit(); sys.exit()
                    elif event.key == pygame.K_p:
                        paused = not paused
                        if paused:
                            pause_start_time = pygame.time.get_ticks()
                        else:
                            total_pause_time += pygame.time.get_ticks() - pause_start_time
                    elif event.key in [pygame.K_EQUALS, pygame.K_PLUS]:
                        speed_value = min(speed_max, speed_value + speed_step);
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                    elif event.key == pygame.K_MINUS:
                        speed_value = max(speed_min, speed_value - speed_step);
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))

                    # 统一的下一张图逻辑 (空格需到终点，N键可跳过)
                    is_next_trigger = (
                                                  event.key == pygame.K_SPACE and self.level.is_endpoint_reached()) or event.key == pygame.K_n
                    if is_next_trigger and not paused:
                        # 使用 -24 作为偏移量来计算当前是第几张图 (0, 1, 2)
                        current_img_idx = stats.game_score - 24

                        if current_img_idx < TOTAL_IMAGES - 1:  # 处理第1张和第2张图完成时
                            pygame.image.save(self.screen,
                                              f"{output_image_folder}/post_screenshot{current_img_idx}.png")
                            # 绘图索引也需要增加
                            time_records[current_img_idx + 1], timestamps[
                                current_img_idx + 1] = game_drawing.random_painting(numbers[current_img_idx + 1], self,
                                                                                    11 + current_img_idx + 1)
                            pygame.image.save(self.screen,
                                              f"{output_image_folder}/pre_screenshot{current_img_idx + 1}.png")
                            stats.game_score += 1
                        elif current_img_idx == TOTAL_IMAGES - 1:  # 处理最后一张图完成时
                            pygame.image.save(self.screen,
                                              f"{output_image_folder}/post_screenshot{current_img_idx}.png")
                            time_records[TOTAL_IMAGES] = (pygame.time.get_ticks() - total_pause_time) / 1000
                            stats.game_score += 1  # 结束任务, 分数变为27

                        if event.key == pygame.K_SPACE: self.level.reset_endpoint_reached()

            # 持续检查长按调整速度
            speed_value = handle_button_event(None, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                              speed_value, speed_step, button_states)

            # 绘制游戏画面
            if not paused:
                self.level.run(dt, stats, [], self.screen)
            else:
                self.level.draw(self.screen, stats)

            # ------------------- 绘制UI元素 -------------------
            Button3(settings, self.screen, f"航天员：{user_id1} & {user_id2}", 10, 20).draw_button()

            # 绘制速度控制模块
            speed_font = pygame.font.Font(get_font_path(), 50);
            button_font = pygame.font.Font(get_font_path(), 50);
            value_font = pygame.font.Font(get_font_path(), 30)
            speed_text = speed_font.render("速度:", True, black);
            self.screen.blit(speed_text,
                             speed_text.get_rect(right=minus_button_rect.left - 10, centery=minus_button_rect.centery))
            minus_disabled = speed_value <= speed_min
            minus_color, minus_border = ((200, 200, 200), (180, 180, 180)) if minus_disabled else (
            (255, 255, 255), (100, 100, 100))
            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5);
            pygame.draw.rect(self.screen, minus_border, minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, (180, 180, 180) if minus_disabled else black);
            self.screen.blit(minus_text, minus_text.get_rect(center=minus_button_rect.center))
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3);
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            value_text = value_font.render(f"{speed_value_to_level(speed_value)}", True, black);
            self.screen.blit(value_text, value_text.get_rect(center=value_display_rect.center))
            plus_disabled = speed_value >= speed_max
            plus_color, plus_border = ((200, 200, 200), (180, 180, 180)) if plus_disabled else (
            (255, 255, 255), (100, 100, 100))
            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5);
            pygame.draw.rect(self.screen, plus_border, plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, (180, 180, 180) if plus_disabled else black);
            self.screen.blit(plus_text, plus_text.get_rect(center=plus_button_rect.center))

            # 绘制状态提示信息
            step_button = Button(settings, self.screen, "", 1700, 1000)
            center_button = Button4(settings, self.screen, "", 550, 1000)
            key_hint_font = pygame.font.Font(get_font_path(), 50)

            if paused:
                step_button.text, hint_text, center_button.text = "已暂停", "按P键继续", "按Esc键返回主菜单"
                self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                 (settings.screen_width // 2, 40))
                step_button.draw_button();
                center_button.draw_button()
            else:
                current_img_num = stats.game_score - 23  # 转换回 1, 2, 3
                if 1 <= current_img_num <= TOTAL_IMAGES:
                    step_button.text = f"{current_img_num} / {TOTAL_IMAGES}"
                    hint_text = "按P键暂停"
                    center_button.text = "按空格键继续" if self.level.is_endpoint_reached() else ""
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 40))
                    step_button.draw_button()
                    if center_button.text: center_button.draw_button()
                else:  # 任务完成
                    step_button.text, hint_text = "完成", "任务已完成"
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 40))
                    step_button.draw_button()

            pygame.display.update()

            # ------------------- 任务结束处理 -------------------
            if stats.game_score == 23 + TOTAL_IMAGES + 1:  # 分数到达27时
                self.level.clear()
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)

                dataloading_1(time_records, timestamps, ROOT_DATA_FOLDER, id, PARTICIPANT_ID_FOLDER, TOTAL_IMAGES)

                data_path = f"{data_folder}/数据.txt"
                try:
                    with open(data_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    data = [f"图像{i + 1} {lines[i].strip()}" for i in range(min(TOTAL_IMAGES, len(lines)))]
                except FileNotFoundError:
                    data = [f"图像{i + 1} 数据缺失" for i in range(TOTAL_IMAGES)]

                # 显示量表
                likert = LikertScale(screen=self.screen, question=f"请{user_id1}按下键盘按键1-7评估任务难度:",
                                     position=(260, 400), size=(1400, 500), highlight_user=user_id1)
                likert_running, score = True, None
                while likert_running:
                    self.screen.fill(grey)
                    draw_data(self, self.screen, data)
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                if show_confirm_dialog(self.screen, "",
                                                       "您确定要返回主页面吗？"): pygame.quit(); sys.exit()
                            else:
                                key_pressed = event.key

                    score = likert.update(mouse_pos=pygame.mouse.get_pos(), key_pressed=key_pressed)
                    pygame.display.flip()
                    if score is not None: likert_running = False

                if score is not None:
                    likert_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/likert_scale"
                    with open(f"{likert_folder}/量表.txt", "w") as f: f.write(str(score))

                running = False  # 退出主循环

        # ------------------- 显示结束画面 -------------------
        self.display_end_screen(is_training=True)
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: wait = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"): wait = False
            self.clock.tick(60)

        pygame.quit()

    def display_task_instructions_formatted(self, subject='AB'):
        """以标准风格动态绘制AB合作任务的指导语"""
        BG_COLOR, TEXT_COLOR, BLACK, GREEN_COLOR, RED, PROMPT_GREEN_COLOR = (230, 230, 230), (0, 0, 0), (0, 0, 0), (
        0, 255, 0), (255, 0, 0), (0, 180, 0)
        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(BG_COLOR)

        try:
            font_name = get_font_path()
            title_font, main_font, key_font, prompt_font = pygame.font.Font(font_name, 65), pygame.font.Font(font_name,
                                                                                                             44), pygame.font.Font(
                font_name, 42), pygame.font.Font(font_name, 50)
            main_font_bold = pygame.font.Font(font_name, 48);
            main_font_bold.set_bold(True)
        except (IOError, TypeError):
            title_font, main_font, key_font, prompt_font = pygame.font.SysFont('sans-serif', 70), pygame.font.SysFont(
                'sans-serif', 45), pygame.font.SysFont('sans-serif', 40), pygame.font.SysFont('sans-serif', 55)
            main_font_bold = pygame.font.SysFont('sans-serif', 45, bold=True)

        user1, user2, user3 = getattr(shared_data, 'user1_mark', '用户1'), getattr(shared_data, 'user2_mark',
                                                                                   '用户2'), getattr(shared_data,
                                                                                                     'user3_mark',
                                                                                                     '用户3')

        def render_composite_line(y, line_def):
            total_width = 0;
            surfaces = []
            for content, font, part_type in line_def:
                if part_type == "key":
                    text_surf = font.render(content, True,
                                            (0, 0, 0)); total_width += text_surf.get_width() + 16; surfaces.append(
                        {'type': 'key', 'content': content, 'font': font})
                else:
                    text_surf = font.render(content, True,
                                            TEXT_COLOR); total_width += text_surf.get_width(); surfaces.append(
                        {'type': 'text', 'surf': text_surf})
            x_pos = (screen_w - total_width) / 2
            for item in surfaces:
                if item['type'] == "key":
                    temp_surf = item['font'].render(item['content'], True, (
                    0, 0, 0)); key_rect_width = temp_surf.get_width() + 16; draw_key_box(self.screen, item['content'],
                                                                                         item['font'], (
                                                                                         x_pos + key_rect_width / 2,
                                                                                         y + item[
                                                                                             'font'].get_height() / 2 - 4)); x_pos += key_rect_width
                else:
                    self.screen.blit(item['surf'], (x_pos, y)); x_pos += item['surf'].get_width()

        def render_line(parts, x, y):
            for text, font, color in parts:
                surf = font.render(text, True, color);
                self.screen.blit(surf, (x, y))
                if font == main_font_bold: pygame.draw.line(self.screen, color, (x, y + surf.get_height() - 2),
                                                            (x + surf.get_width(), y + surf.get_height() - 2), 2)
                x += surf.get_width()

        y_pos, line_height = 160, 65

        title_text = f"{user1}和{user2}合作绘图练习指导语"
        title_surf = title_font.render(title_text, True, TEXT_COLOR);
        self.screen.blit(title_surf, title_surf.get_rect(center=(screen_w / 2, 80)))

        role_text = f"请 {user1} 和 {user2} 合作完成任务"
        role_surf = main_font.render(role_text, True, TEXT_COLOR);
        self.screen.blit(role_surf, role_surf.get_rect(center=(screen_w / 2, y_pos)));
        y_pos += line_height

        parts1 = [(f"航天员控制键盘沿", main_font, TEXT_COLOR), ("黑色轨迹", main_font_bold, TEXT_COLOR),
                  ("从", main_font, TEXT_COLOR), ("绿色起点", main_font_bold, TEXT_COLOR),
                  ("移至", main_font, TEXT_COLOR), ("红色终点", main_font_bold, TEXT_COLOR)]
        total_width_parts1 = sum(f.render(t, True, c).get_width() for t, f, c in parts1);
        render_line(parts1, (screen_w - total_width_parts1) / 2, y_pos);
        y_pos += line_height + 20

        diagram_y = y_pos;
        steps = ["任务开始", "沿轨迹绘图", "到达终点"];
        box_w, box_h, gap = 220, 100, 80
        total_width_diagram = len(steps) * box_w + (len(steps) - 1) * gap;
        start_x = (screen_w - total_width_diagram) / 2
        for i, step_text in enumerate(steps):
            box_x = start_x + i * (box_w + gap);
            box_rect = pygame.Rect(box_x, diagram_y, box_w, box_h)
            pygame.draw.rect(self.screen, (200, 200, 200), box_rect, border_radius=10);
            pygame.draw.rect(self.screen, TEXT_COLOR, box_rect, 2, border_radius=10)
            if i == 0:
                pygame.draw.rect(self.screen, GREEN_COLOR, (box_rect.centerx - 15, box_rect.centery - 15, 30, 30))
            elif i == 1:
                path_points = [(box_rect.left + 30, box_rect.centery + 15), (box_rect.centerx, box_rect.centery - 15),
                               (box_rect.right - 30, box_rect.centery + 15)]; pygame.draw.lines(self.screen, TEXT_COLOR,
                                                                                                False, path_points, 4)
            else:
                pygame.draw.rect(self.screen, RED, (box_rect.centerx - 15, box_rect.centery - 15, 30, 30))
            label_surf = main_font.render(step_text, True, TEXT_COLOR);
            self.screen.blit(label_surf, label_surf.get_rect(center=(box_rect.centerx, box_rect.bottom + 30)))
            if i < len(steps) - 1: arrow_start = (box_rect.right + 10, box_rect.centery); arrow_end = (
            box_rect.right + gap - 10, box_rect.centery); pygame.draw.line(self.screen, TEXT_COLOR, arrow_start,
                                                                           arrow_end, 4); pygame.draw.polygon(
                self.screen, TEXT_COLOR, [(arrow_end[0], arrow_end[1]), (arrow_end[0] - 15, arrow_end[1] - 8),
                                          (arrow_end[0] - 15, arrow_end[1] + 8)])
        y_pos += box_h + 80

        line_def = [(f"请{user1}: 使用", main_font, "text"), ("A", key_font, "key"), ("控制左,", main_font, "text"),
                    ("D", key_font, "key"), ("控制右。", main_font, "text"), (f"  请{user2}:使用 ", main_font, "text"),
                    ("↑", key_font, "key"), ("控制上,", main_font, "text"), ("↓", key_font, "key"),
                    ("控制下。", main_font, "text")]
        render_composite_line(y_pos, line_def);
        y_pos += line_height + 20

        button_text = [("您还可以通过键盘上的: ", main_font, "text"), ("-", key_font, "key"), ("和", main_font, "text"),
                       ("+", key_font, "key"), ("按钮来调整绘图速度", main_font, "text")]
        render_composite_line(y_pos, button_text);
        y_pos += line_height + 50

        diagram_bg_rect = pygame.Rect(0, 0, 500, 100);
        diagram_bg_rect.center = (screen_w / 2, y_pos)
        speed_label_surf = main_font.render("速度:", True, TEXT_COLOR);
        self.screen.blit(speed_label_surf,
                         speed_label_surf.get_rect(center=(diagram_bg_rect.centerx - 160, diagram_bg_rect.centery)))
        minus_demo_rect = pygame.Rect(0, 0, 50, 50);
        minus_demo_rect.center = (diagram_bg_rect.centerx - 55, diagram_bg_rect.centery);
        pygame.draw.rect(self.screen, (255, 255, 255), minus_demo_rect, border_radius=5);
        pygame.draw.rect(self.screen, (180, 180, 180), minus_demo_rect, 2, border_radius=5);
        minus_text = main_font.render("-", True, TEXT_COLOR);
        self.screen.blit(minus_text, minus_text.get_rect(center=minus_demo_rect.center))
        value_demo_rect = pygame.Rect(0, 0, 50, 50);
        value_demo_rect.center = (diagram_bg_rect.centerx, diagram_bg_rect.centery);
        pygame.draw.rect(self.screen, (240, 240, 240), value_demo_rect, border_radius=3);
        pygame.draw.rect(self.screen, (100, 100, 100), value_demo_rect, 2, border_radius=3);
        value_text = main_font.render("50", True, BLACK);
        self.screen.blit(value_text, value_text.get_rect(center=value_demo_rect.center))
        plus_demo_rect = pygame.Rect(0, 0, 50, 50);
        plus_demo_rect.center = (diagram_bg_rect.centerx + 55, diagram_bg_rect.centery);
        pygame.draw.rect(self.screen, (255, 255, 255), plus_demo_rect, border_radius=5);
        pygame.draw.rect(self.screen, (180, 180, 180), plus_demo_rect, 2, border_radius=5);
        plus_text = main_font.render("+", True, TEXT_COLOR);
        self.screen.blit(plus_text, plus_text.get_rect(center=plus_demo_rect.center))

        prompt_parts = [("准备好后，请按 ", prompt_font, TEXT_COLOR), ("空格键", prompt_font, PROMPT_GREEN_COLOR),
                        (" 开始练习", prompt_font, TEXT_COLOR)]
        total_prompt_width = sum(f.render(t, True, c).get_width() for t, f, c in prompt_parts);
        current_x = (screen_w - total_prompt_width) / 2;
        prompt_y_pos = screen_h - 100
        for text, font, color in prompt_parts: surf = font.render(text, True, color); self.screen.blit(surf,
                                                                                                       surf.get_rect(
                                                                                                           left=current_x,
                                                                                                           centery=prompt_y_pos)); current_x += surf.get_width()

        pygame.display.update()

    def display_end_screen(self, is_training=False):
        """显示标准化的结束画面"""
        BG_COLOR, TEXT_COLOR, ACCENT_COLOR = (230, 230, 230), (0, 0, 0), (0, 255, 0)
        screen_width, screen_height = self.screen.get_size()
        try:
            title_font, subtitle_font, note_font = [pygame.font.Font(get_font_path(), size) for size in [88, 78, 78]]
        except IOError:
            title_font, subtitle_font, note_font = [pygame.font.SysFont(None, size) for size in [100, 78, 45]]

        self.screen.fill(BG_COLOR)

        title_text = "恭喜您完成练习" if is_training else "恭喜您完成实验"
        title_surf = title_font.render(title_text, True, TEXT_COLOR);
        self.screen.blit(title_surf, title_surf.get_rect(center=(screen_width / 2, 220)))
        subtitle_surf = subtitle_font.render("数据已保存", True, TEXT_COLOR);
        self.screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(screen_width / 2, 420)))

        note_parts = [("按", TEXT_COLOR), ("Esc", ACCENT_COLOR), ("返回主界面", TEXT_COLOR)]
        note_surfaces = [note_font.render(text, True, color) for text, color in note_parts]
        total_width = sum(surf.get_width() for surf in note_surfaces);
        current_x = (screen_width - total_width) / 2
        for surf in note_surfaces:
            self.screen.blit(surf, surf.get_rect(left=current_x, centery=screen_height - 100));
            current_x += surf.get_width()

        check_center, check_size = (screen_width / 2, 120), 40
        pygame.draw.circle(self.screen, ACCENT_COLOR, check_center, check_size)
        pygame.draw.circle(self.screen, TEXT_COLOR, check_center, check_size, 3)
        check_points = [(check_center[0] - 15, check_center[1]), (check_center[0] - 5, check_center[1] + 10),
                        (check_center[0] + 15, check_center[1] - 10)]
        pygame.draw.lines(self.screen, TEXT_COLOR, False, check_points, 5)
        pygame.display.update()


def draw_data(self, screen, data):
    """优化的数据显示函数"""
    percentages, times = [], []
    summary_font = pygame.font.Font(get_font_path(), 60)
    time_pattern, percentage_pattern = re.compile(r'绘图时长：([\d.]+)'), re.compile(r'百分比：([\d.]+)%')
    for line in data:
        try:
            if (t := time_pattern.search(line)): times.append(float(t.group(1)))
            if (p := percentage_pattern.search(line)): percentages.append(float(p.group(1)))
        except (ValueError, AttributeError):
            continue
    if not percentages and not times:
        error_text = summary_font.render("无有效的练习数据", True, (255, 0, 0))
        screen.blit(error_text, error_text.get_rect(center=(screen.get_width() // 2, 250)))
        return
    avg_percentage = sum(percentages) / len(percentages) if percentages else 0
    summary_lines = [f"任务平均完成度: {avg_percentage:.2f}%", f"任务总用时: {sum(times):.2f}秒"]
    for i, text in enumerate(summary_lines):
        text_surface = summary_font.render(text, True, black)
        screen.blit(text_surface, text_surface.get_rect(center=(screen.get_width() / 2, 200 + i * 100)))


def dataloading_1(time_records, timestamps, root_folder, id, participant_folder, total_images):
    """统一的数据加载和计算函数"""
    base_path = f"./{root_folder}/{id}/{participant_folder}/output_image"
    data_file_path = f"./{root_folder}/{id}/{participant_folder}/data/数据.txt"
    if os.path.exists(data_file_path): os.remove(data_file_path)
    for i in range(total_images):
        pre_img = cv2.imread(f"{base_path}/pre_screenshot{i}.png")
        post_img = cv2.imread(f"{base_path}/post_screenshot{i}.png")
        if pre_img is not None and post_img is not None:
            calculate_pixel_difference_test(pre_img, post_img, time_records[i], time_records[i + 1], timestamps[i],
                                            root_folder, id, participant_folder)


def loading_animation(self, WINDOW_WIDTH, WINDOW_HEIGHT, font):
    """标准化的加载动画"""
    clock, dots, dot_index, last_update = pygame.time.Clock(), [".", "..", "..."], 0, time.time()
    start_time = time.time()
    while time.time() - start_time < 2:
        if time.time() - last_update >= 0.5:
            dot_index = (dot_index + 1) % len(dots);
            last_update = time.time()
        self.screen.fill(grey)
        text_surface = font.render(f"数据处理中{dots[dot_index]}", True, black)
        self.screen.blit(text_surface, text_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)))
        pygame.display.flip()
        clock.tick(60)


def calculate_pixel_difference_test(image1, image2, t1, t2, timestamp, root_folder, id, participant_folder):
    """像素差异计算函数"""
    x, y, width, height = 0, 50, 1920, 920
    image1_cropped = image1[y:y + height, x:x + width]
    image2_cropped = image2[y:y + height, x:x + width]
    gray_origin = cv2.cvtColor(image1_cropped, cv2.COLOR_BGR2GRAY)
    black_mask = (gray_origin < 50)
    hsv_image2 = cv2.cvtColor(image2_cropped, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 50, 50]);
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv_image2, lower_green, upper_green) > 0
    overlap_mask = black_mask & green_mask
    total_pixels = np.sum(black_mask)
    overlap_pixels = np.sum(overlap_mask)
    overlap_percentage = (overlap_pixels / total_pixels * 100) if total_pixels > 0 else 0
    time_diff = abs(t2 - t1) if t1 and t2 else 0
    output_path = f"./{root_folder}/{id}/{participant_folder}/data/数据.txt"
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(
            f"有效像素: {overlap_pixels}, 总像素: {total_pixels}, 百分比：{overlap_percentage:.2f}%, 绘图时长：{time_diff:.2f}\n")


if __name__ == '__main__':
    game = Game()
    game.run()