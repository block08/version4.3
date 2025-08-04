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


def speed_level_to_value(level):
    """将1-100级别转换为1-100的实际速度值"""
    return level


def speed_value_to_level(value):
    """将1-100的实际速度值转换为1-100级别"""
    return int(value)


def read_speed_value():
    """读取scroll_value.txt中的速度值，如果文件不存在或值无效则返回默认值50"""
    try:
        with open('scroll_value.txt', 'r') as f:
            speed_value = int(f.read().strip())
            return max(1, min(100, speed_value))
    except (FileNotFoundError, ValueError):
        with open('scroll_value.txt', 'w') as f:
            f.write('50')
        return 50


def draw_key_box(screen, text, font, center_pos):
    """绘制一个带有边框的按键方框。"""
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
def show_minimize_dialog(screen, message):
    """
    显示最小化恢复对话框，只有一个确认按钮
    """
    # 保存当前屏幕内容
    original_screen = screen.copy()

    # 对话框尺寸和位置（与show_confirm_dialog保持一致）
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    dialog_width = 800
    dialog_height = 450  # 增加高度
    dialog_x = (screen_width - dialog_width) // 2
    dialog_y = (screen_height - dialog_height) // 2
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

    # 颜色定义（匹配show_confirm_dialog样式）
    bg_color = (255, 255, 255)  # 白色背景
    border_color = (85, 85, 85)  # 灰色边框
    text_color = (0, 0, 0)  # 黑色文字
    button_color = (255, 255, 255)  # 白色按钮背景
    button_border = (204, 204, 204)  # 浅灰色按钮边框
    button_hover = (240, 240, 240)  # 浅灰色悬停背景
    button_border_hover = (153, 153, 153)  # 深灰色悬停边框
    button_text_color = (0, 0, 0)  # 黑色按钮文字
    hint_text_color = (136, 136, 136)  # 灰色提示文字

    # 字体设置（与show_confirm_dialog保持一致）
    try:
        message_font = pygame.font.Font(get_font_path(), 50)
        button_font = pygame.font.Font(get_font_path(), 50)
        hint_font = pygame.font.Font(get_font_path(), 35)
    except:
        message_font = pygame.font.Font(None, 50)
        button_font = pygame.font.Font(None, 50)
        hint_font = pygame.font.Font(None, 35)

    # 按钮设置（与show_confirm_dialog保持一致）
    button_width = 220
    button_height = 65
    button_x = dialog_x + (dialog_width - button_width) // 2
    button_y = dialog_y + dialog_height - 120  # 上移为提示文字留空间
    confirm_button = pygame.Rect(button_x, button_y, button_width, button_height)

    # 悬停状态
    button_hover_state = False
    clock = pygame.time.Clock()

    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:  # Y键确认
                    return
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                button_hover_state = confirm_button.collidepoint(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_pos = pygame.mouse.get_pos()
                    if confirm_button.collidepoint(mouse_pos):
                        return

        # 绘制半透明背景
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(original_screen, (0, 0))
        screen.blit(overlay, (0, 0))

        # 绘制对话框背景和边框（匹配show_confirm_dialog样式）
        pygame.draw.rect(screen, bg_color, dialog_rect, border_radius=20)
        pygame.draw.rect(screen, border_color, dialog_rect, 2, border_radius=20)

        # 绘制消息文本（与show_confirm_dialog保持一致的位置）
        message_surface = message_font.render(message, True, text_color)
        message_rect = message_surface.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 160))
        screen.blit(message_surface, message_rect)

        # 绘制确认按钮（匹配show_confirm_dialog样式）
        current_button_color = button_hover if button_hover_state else button_color
        current_border_color = button_border_hover if button_hover_state else button_border

        # 绘制按钮背景（圆角矩形）
        pygame.draw.rect(screen, current_button_color, confirm_button, border_radius=25)
        pygame.draw.rect(screen, current_border_color, confirm_button, 2, border_radius=25)

        # 绘制按钮文字
        button_text = button_font.render("确定", True, button_text_color)
        button_text_rect = button_text.get_rect(center=confirm_button.center)
        screen.blit(button_text, button_text_rect)

        # 绘制Y键提示
        hint_text = hint_font.render("按Y键", True, hint_text_color)
        hint_rect = hint_text.get_rect(center=(dialog_x + dialog_width // 2, button_y + button_height + 30))
        screen.blit(hint_text, hint_rect)

        pygame.display.flip()
        clock.tick(60)

def show_confirm_dialog(screen, title, message):
    """显示一个标准化的确认对话框，返回 True (确认) 或 False (取消)"""
    original_screen = screen.copy()
    screen_width, screen_height = screen.get_width(), screen.get_height()
    dialog_width, dialog_height = 800, 450
    dialog_x, dialog_y = (screen_width - dialog_width) // 2, (screen_height - dialog_height) // 2
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

    bg_color = (255, 255, 255)
    border_color = (85, 85, 85)
    text_color = (0, 0, 0)
    button_color = (255, 255, 255)
    button_border = (204, 204, 204)
    button_hover = (240, 240, 240)
    button_border_hover = (153, 153, 153)
    button_text_color = (0, 0, 0)
    hint_text_color = (136, 136, 136)

    try:
        title_font = pygame.font.Font(get_font_path(), 60)
        message_font = pygame.font.Font(get_font_path(), 50)
        button_font = pygame.font.Font(get_font_path(), 50)
        hint_font = pygame.font.Font(get_font_path(), 35)
    except:
        title_font = pygame.font.Font(None, 60)
        message_font = pygame.font.Font(None, 50)
        button_font = pygame.font.Font(None, 50)
        hint_font = pygame.font.Font(None, 35)

    button_width, button_height, button_spacing = 220, 65, 65
    total_buttons_width = 2 * button_width + button_spacing
    buttons_start_x = dialog_x + (dialog_width - total_buttons_width) // 2
    button_y = dialog_y + dialog_height - 120

    yes_button = pygame.Rect(buttons_start_x, button_y, button_width, button_height)
    no_button = pygame.Rect(buttons_start_x + button_width + button_spacing, button_y, button_width, button_height)
    yes_hover, no_hover = False, False

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                screen.blit(original_screen, (0, 0));
                pygame.display.flip();
                return False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                yes_hover = yes_button.collidepoint(mouse_pos)
                no_hover = no_button.collidepoint(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if yes_button.collidepoint(mouse_pos): screen.blit(original_screen,
                                                                   (0, 0)); pygame.display.flip(); return True
                if no_button.collidepoint(mouse_pos): screen.blit(original_screen,
                                                                  (0, 0)); pygame.display.flip(); return False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_y]: screen.blit(original_screen,
                                                                           (0, 0)); pygame.display.flip(); return True
                if event.key in [pygame.K_ESCAPE, pygame.K_n]: screen.blit(original_screen,
                                                                           (0, 0)); pygame.display.flip(); return False

        screen.blit(original_screen, (0, 0))
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA);
        overlay.fill((0, 0, 0, 128));
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, bg_color, dialog_rect, border_radius=20)
        pygame.draw.rect(screen, border_color, dialog_rect, 2, border_radius=20)

        title_surf = title_font.render(title, True, text_color);
        screen.blit(title_surf, title_surf.get_rect(center=(dialog_rect.centerx, dialog_y + 60)))
        msg_surf = message_font.render(message, True, text_color);
        screen.blit(msg_surf, msg_surf.get_rect(center=(dialog_rect.centerx, dialog_y + 160)))

        yes_bg = button_hover if yes_hover else button_color;
        yes_brd = button_border_hover if yes_hover else button_border
        no_bg = button_hover if no_hover else button_color;
        no_brd = button_border_hover if no_hover else button_border
        pygame.draw.rect(screen, yes_bg, yes_button, border_radius=25);
        pygame.draw.rect(screen, yes_brd, yes_button, 2, border_radius=25)
        pygame.draw.rect(screen, no_bg, no_button, border_radius=25);
        pygame.draw.rect(screen, no_brd, no_button, 2, border_radius=25)

        yes_text = button_font.render("是", True, button_text_color);
        screen.blit(yes_text, yes_text.get_rect(center=yes_button.center))
        no_text = button_font.render("否", True, button_text_color);
        screen.blit(no_text, no_text.get_rect(center=no_button.center))

        yes_hint = hint_font.render("按Y键", True, hint_text_color);
        screen.blit(yes_hint, yes_hint.get_rect(center=(yes_button.centerx, yes_button.bottom + 25)))
        no_hint = hint_font.render("按N键", True, hint_text_color);
        screen.blit(no_hint, no_hint.get_rect(center=(no_button.centerx, no_button.bottom + 25)))

        pygame.display.flip()
        clock.tick(60)


class Game:
    def __init__(self):
        pygame.init()
        with open('scroll_value.txt', 'w') as f: f.write('50')
        settings = Settings()
        self.screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), pygame.FULLSCREEN)
        self.font = pygame.font.Font(get_font_path(), 40)
        pygame.display.set_caption('人员①训练')
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.screen.fill(grey)
        # 添加初始化状态标志，避免启动时触发VIDEOEXPOSE弹窗
        self.is_initial_startup = True

    def render_text_with_green_keys(self, text, font, surface, center_pos):
        """渲染带有高亮按键提示的文本"""
        GREEN_COLOR = (0, 255, 0)
        BLACK_COLOR = (0, 0, 0)
        parts = re.split(r'(P|Esc|空格键)', text)
        surfaces = []
        for part in parts:
            if part in ['P', 'Esc', '空格键']:
                surfaces.append(font.render(part, True, GREEN_COLOR))
            elif part:
                surfaces.append(font.render(part, True, BLACK_COLOR))

        total_width = sum(s.get_width() for s in surfaces)
        current_x = center_pos[0] - total_width / 2
        y = center_pos[1] - surfaces[0].get_height() / 2

        for s in surfaces:
            surface.blit(s, (current_x, y))
            current_x += s.get_width()

    def run(self):
        settings = Settings()
        stats = GameStats(settings)
        user_mark = getattr(shared_data, 'user1_mark', '01')

        # 核心配置
        ROOT_DATA_FOLDER = "Training_Behavioral_data"
        PARTICIPANT_ID_FOLDER = "subA"
        TOTAL_IMAGES = 3

        # 创建数据目录并使用配置管理器获取ID
        try:
            from src.config.config_manager import get_id_file_path
            os.makedirs(ROOT_DATA_FOLDER, exist_ok=True)
            id_file_path = get_id_file_path()
            if not os.path.exists(id_file_path):
                with open(id_file_path, "w") as file: file.write("training_001")
            with open(id_file_path, "r") as file:
                id = file.read().strip()
        except Exception as e:
            print(f"处理ID文件时出错: {e}");
            pygame.quit();
            sys.exit()

        output_image_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/output_image"
        data_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/data"
        likert_folder = f"./{ROOT_DATA_FOLDER}/{id}/{PARTICIPANT_ID_FOLDER}/likert_scale"
        for folder in [output_image_folder, data_folder, likert_folder]:
            os.makedirs(folder, exist_ok=True)

        user_id_display = re.search(r'\d+$', user_mark).group() if re.search(r'\d+$', user_mark) else user_mark
        game_drawing = GameDrawing()

        # 时间戳变量
        timestamps = [None] * TOTAL_IMAGES
        time_records = [None] * (TOTAL_IMAGES + 1)

        with open('config.txt', 'w') as f:
            f.truncate(0); f.write('1')

        # 速度控制UI初始化
        speed_value = read_speed_value()
        speed_min, speed_max, speed_step = 0, 100, 10
        button_states = {'minus_pressed': False, 'plus_pressed': False, 'last_change_time': 0}
        button_y, button_size, button_spacing = 10, 60, 40
        minus_button_rect = pygame.Rect(settings.screen_width - 275, button_y, button_size, button_size)
        plus_button_rect = pygame.Rect(settings.screen_width - 130, button_y, button_size, button_size)
        value_display_rect = pygame.Rect(settings.screen_width - 210, button_y, 75, button_size)

        # 显示指导语
        self.display_task_instructions_formatted(subject='A')
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 如果是初始启动，跳过弹窗直接重绘界面
                    if self.is_initial_startup:
                        self.is_initial_startup = False
                        self.display_task_instructions_formatted(subject='A')
                    else:
                        # 窗口被最小化后恢复，显示简化确认对话框
                        show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                        # 重绘流程图指导语界面
                        self.display_task_instructions_formatted(subject='A')
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"): pygame.quit(); sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
            self.clock.tick(60)

        # 初始化游戏
        numbers = random.sample(range(1, 9), TOTAL_IMAGES)
        stats.game_score = 0
        paused, pause_start_time, total_pause_time = False, 0, 0
        running = True

        # 创建一个空的基准图
        self.screen.fill(grey)
        pygame.image.save(self.screen, f"{output_image_folder}/post_screenshot-1.png")

        # 自动显示第一张图片 (不再等待按键)
        time_records[0], timestamps[0] = game_drawing.random_painting(numbers[0], self, 0, total_pause_time)
        pygame.image.save(self.screen, f"{output_image_folder}/pre_screenshot0.png")
        stats.game_score = 1


        # 主循环
        screenshot_taken = False  # 标记是否已经截图
        while running:
            dt = self.clock.tick(60) / 1000
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 窗口被最小化后恢复，独立处理暂停时间
                    minimize_pause_start = pygame.time.get_ticks()
                    # 如果当前已经是P键暂停状态，先记录P键暂停的时间
                    if paused:
                        total_pause_time += minimize_pause_start - pause_start_time
                    show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                    minimize_pause_end = pygame.time.get_ticks()
                    # 累加最小化暂停时间
                    total_pause_time += minimize_pause_end - minimize_pause_start
                    # 如果之前是P键暂停状态，重新开始计时
                    if paused:
                        pause_start_time = minimize_pause_end
                    # 更新当前图片的时间戳以反映最小化暂停时间
                    if 1 <= stats.game_score <= 3:
                        updated_time = game_drawing.update_current_timestamp(total_pause_time)
                        # 根据当前图片更新对应的时间变量
                        if stats.game_score == 1:
                            time_records[0] = updated_time
                        elif stats.game_score == 2:
                            time_records[1] = updated_time
                        elif stats.game_score == 3:
                            time_records[2] = updated_time
                    # 重绘A阶段绘图界面
                    self.screen.fill(grey)
                    # 界面会在循环末尾重绘
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

                    # 统一的下一张图逻辑
                    is_next_trigger = (
                                                  event.key == pygame.K_SPACE and self.level.is_endpoint_reached()) or event.key == pygame.K_n
                    if is_next_trigger and not paused:
                        if stats.game_score < TOTAL_IMAGES:
                            current_idx = stats.game_score - 1
                            # 先截取当前绘制完成的画面（在屏幕清空之前）
                            pygame.image.save(self.screen, f"{output_image_folder}/post_screenshot{current_idx}.png")

                            # 再显示下一张图并截取前置画面
                            time_records[current_idx + 1], timestamps[current_idx + 1] = game_drawing.random_painting(
                                numbers[current_idx + 1], self, current_idx + 1, total_pause_time)
                            pygame.image.save(self.screen, f"{output_image_folder}/pre_screenshot{current_idx + 1}.png")
                            stats.game_score += 1
                            screenshot_taken = True  # 标记已截图，避免重复清空屏幕
                        elif stats.game_score == TOTAL_IMAGES:
                            # 截取最后一张图的绘制完成画面
                            pygame.image.save(self.screen,
                                              f"{output_image_folder}/post_screenshot{TOTAL_IMAGES - 1}.png")
                            time_records[TOTAL_IMAGES] = (pygame.time.get_ticks() - total_pause_time) / 1000
                            stats.game_score += 1  # 状态变为 4，任务结束

                        if event.key == pygame.K_SPACE: self.level.reset_endpoint_reached()

            # 只有在没有截图的情况下才清空屏幕
            if not screenshot_taken:
                self.screen.fill(grey)
            else:
                screenshot_taken = False  # 重置标记

            # 持续检查长按
            speed_value = handle_button_event(None, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                              speed_value, speed_step, button_states)

            # 绘制游戏内容
            if not paused:
                self.level.run(dt, stats, [], self.screen)
            else:
                self.level.draw(self.screen, stats)

            # 绘制UI
            Button3(settings, self.screen, f"航天员：{user_id_display}", 10, 20).draw_button()

            # 绘制速度控制
            speed_font = pygame.font.Font(get_font_path(), 50);
            button_font = pygame.font.Font(get_font_path(), 50);
            value_font = pygame.font.Font(get_font_path(), 30)
            speed_text = speed_font.render("速度:", True, black);
            self.screen.blit(speed_text,
                             speed_text.get_rect(right=minus_button_rect.left - 10, centery=minus_button_rect.centery))
            minus_disabled = speed_value <= speed_min
            minus_color = (200, 200, 200) if minus_disabled else (255, 255, 255);
            minus_border = (180, 180, 180) if minus_disabled else (100, 100, 100)
            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5);
            pygame.draw.rect(self.screen, minus_border, minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, (180, 180, 180) if minus_disabled else black);
            self.screen.blit(minus_text, minus_text.get_rect(center=minus_button_rect.center))
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3);
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            value_text = value_font.render(f"{speed_value_to_level(speed_value)}", True, black);
            self.screen.blit(value_text, value_text.get_rect(center=value_display_rect.center))
            plus_disabled = speed_value >= speed_max
            plus_color = (200, 200, 200) if plus_disabled else (255, 255, 255);
            plus_border = (180, 180, 180) if plus_disabled else (100, 100, 100)
            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5);
            pygame.draw.rect(self.screen, plus_border, plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, (180, 180, 180) if plus_disabled else black);
            self.screen.blit(plus_text, plus_text.get_rect(center=plus_button_rect.center))

            # 绘制状态提示
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
                if 1 <= stats.game_score <= TOTAL_IMAGES:
                    step_button.text = f"{stats.game_score} / {TOTAL_IMAGES}"
                    hint_text = "按P键暂停"
                    center_button.text = "按空格键继续" if self.level.is_endpoint_reached() else ""
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 40))
                    step_button.draw_button()
                    if center_button.text: center_button.draw_button()
                elif stats.game_score > TOTAL_IMAGES:
                    step_button.text, hint_text = "完成", "任务已完成"
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 40))
                    step_button.draw_button()

            pygame.display.update()

            # 任务结束处理
            if stats.game_score == TOTAL_IMAGES + 1:
                self.level.clear()
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)
                dataloading_1(time_records, timestamps, ROOT_DATA_FOLDER, id, PARTICIPANT_ID_FOLDER, TOTAL_IMAGES, total_pause_time)

                data_path = f"{data_folder}/数据.txt"
                try:
                    with open(data_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    data = [f"图像{i + 1} {lines[i].strip()}" for i in range(min(TOTAL_IMAGES, len(lines)))]
                except FileNotFoundError:
                    data = [f"图像{i + 1} 数据缺失" for i in range(TOTAL_IMAGES)]

                likert = LikertScale(screen=self.screen, question=f"请{user_id_display}按下键盘按键1-7评估任务难度:",
                                     position=(260, 400), size=(1400, 500), highlight_user=user_id_display)
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
                    with open(f"{likert_folder}/量表.txt", "w") as f: f.write(str(score))

                running = False

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
        """
        以简化和层级化的风格动态绘制绘图任务的指导语。
        【整合版：高亮按键、自动换行、速度说明、最终布局】
        """
        # --- 参数定义 ---
        BG_COLOR = (230, 230, 230)
        TEXT_COLOR = (33, 37, 41)
        BLACK = (0, 0, 0)
        DIVIDER_COLOR = (200, 200, 200)
        PROMPT_GREEN_COLOR = (40, 167, 69)
        HIGHLIGHT_COLOR = (40, 167, 69)
        GREEN_ICON_COLOR = (40, 167, 69)
        RED_ICON_COLOR = (220, 53, 69)
        # 【修改3】为示意图的方块使用一个对比度更高的灰色
        DIAGRAM_BOX_COLOR = (200, 204, 208)

        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(BG_COLOR)

        # --- 字体加载 ---
        try:
            font_name = get_font_path()
            title_font = pygame.font.Font(font_name, 70)
            title_font.set_bold(True)
            subtitle_font = pygame.font.Font(font_name, 52)
            body_font = pygame.font.Font(font_name, 42)
            key_font = pygame.font.Font(font_name, 22)
            key_font.set_bold(True)
            prompt_font = pygame.font.Font(font_name, 45)
            speed_button_symbol_font = pygame.font.Font(font_name, 50)
        except (IOError, TypeError):
            title_font = pygame.font.SysFont('sans-serif', 75, bold=True)
            subtitle_font = pygame.font.SysFont('sans-serif', 55, bold=False)
            body_font = pygame.font.SysFont('sans-serif', 45, bold=False)
            key_font = pygame.font.SysFont('sans-serif', 24, bold=True)
            prompt_font = pygame.font.SysFont('sans-serif', 50)
            speed_button_symbol_font = pygame.font.SysFont('sans-serif', 50)

        user1 = getattr(shared_data, 'user1_mark', '用户1')
        user2 = getattr(shared_data, 'user2_mark', '用户2')
        user3 = getattr(shared_data, 'user3_mark', '用户3')

        # --- 辅助函数 ---
        def render_highlighted_text(text_parts, font, default_color, highlight_color, highlight_words):
            surfaces = []
            for part in text_parts:
                is_highlighted = part in highlight_words
                color = highlight_color if is_highlighted else default_color
                surfaces.append(font.render(part, True, color))
            return surfaces

        def draw_single_key(screen, rect, text, font, color_scheme):
            pygame.draw.rect(screen, color_scheme['shadow'], (rect.x, rect.y + 3, rect.width, rect.height),
                             border_radius=8)
            pygame.draw.rect(screen, color_scheme['face'], rect, border_radius=8)
            pygame.draw.rect(screen, color_scheme['border'], rect, 2, border_radius=8)
            text_surf = font.render(text, True, color_scheme['text'])
            screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        def draw_keyboard_layout(screen, center_x, top_y, key_font, is_highlighted):
            KEY_SIZE = 60
            GAP = 8
            highlight_color_scheme = {'face': HIGHLIGHT_COLOR, 'border': (25, 135, 84), 'text': (255, 255, 255),
                                      'shadow': (150, 150, 150)}
            default_color_scheme = {'face': (245, 245, 245), 'border': (180, 180, 180), 'text': (0, 0, 0),
                                    'shadow': (150, 150, 150)}
            layout = {
                'W': {'pos': (2.5, 0)}, 'S': {'pos': (2.5, 1)}, 'A': {'pos': (1.5, 1)}, 'D': {'pos': (3.5, 1)},
                '↑': {'pos': (12, 0)}, '↓': {'pos': (12, 1)}, '←': {'pos': (11, 1)}, '→': {'pos': (13, 1)},
            }
            keyboard_width = 14 * (KEY_SIZE + GAP)
            start_x = center_x - keyboard_width / 2
            for key_name, properties in layout.items():
                x_mult, y_mult = properties['pos']
                key_rect = pygame.Rect(start_x + x_mult * (KEY_SIZE + GAP), top_y + y_mult * (KEY_SIZE + GAP), KEY_SIZE,
                                       KEY_SIZE)
                color_scheme = highlight_color_scheme if key_name in is_highlighted else default_color_scheme
                draw_single_key(screen, key_rect, key_name, key_font, color_scheme)

        # --- 布局开始 ---
        margin = 150
        y_pos = 100

        # --- Section 1: 标题与角色 ---
        title_map = {
            'A': f"单人绘图任务指导语", 'B': f"单人绘图任务指导语", 'C': f"单人绘图任务指导语",
            'AB': f"合作绘图任务指导语", 'AC': f"合作绘图任务指导语"
        }
        title_text = title_map.get(subject, "绘图任务指导语")
        title_surf = title_font.render(title_text, True, TEXT_COLOR)
        self.screen.blit(title_surf, title_surf.get_rect(center=(screen_w / 2, y_pos)))
        y_pos += title_surf.get_height()

        role_map = {
            'A': f"请{user1}绘图，辅助航天员休息", 'B': f"请{user2}绘图，辅助航天员休息",
            'C': f"请{user3}绘图，辅助航天员休息",
            'AB': f"请{user1}和辅助航天员绘图", 'AC': f"请{user1}和辅助航天员绘图"
        }
        role_text = role_map.get(subject, "")
        role_surf = subtitle_font.render(role_text, True, TEXT_COLOR)
        self.screen.blit(role_surf, role_surf.get_rect(center=(screen_w / 2, y_pos + 20)))
        y_pos += role_surf.get_height() + 50

        # --- Section 2: 任务流程图与速度 ---
        pygame.draw.line(self.screen, DIVIDER_COLOR, (margin, y_pos), (screen_w - margin, y_pos), 2)
        y_pos += 40

        user_text = {'A': user1, 'B': user2, 'C': user3, 'AB': f"{user1}和辅助航天员", 'AC': f"{user1}和辅助航天员"}.get(
            subject, "")
        full_desc_text = f"{user_text}航天员需控制键盘，从绿色起点沿黑色轨迹移动至红色终点。"
        desc_surf = body_font.render(full_desc_text, True, TEXT_COLOR)
        self.screen.blit(desc_surf, desc_surf.get_rect(center=(screen_w / 2, y_pos)))
        y_pos += desc_surf.get_height() + 40

        steps = ["任务起点", "沿轨迹绘图", "任务终点"]
        diagram_label = body_font.render("流程示意图:", True, TEXT_COLOR)
        diagram_label_gap = 20
        box_w, box_h = 200, 90
        gap = 30

        speed_label_surf = body_font.render("速度:", True, TEXT_COLOR)
        speed_gap = 40
        speed_button_size = 55
        speed_value_box_w = 75
        speed_box_gap = 10
        speed_section_width = speed_label_surf.get_width() + speed_gap + 2 * speed_button_size + speed_value_box_w + 2 * speed_box_gap
        diagram_content_width = len(steps) * box_w + (len(steps) - 1) * gap
        total_diagram_width = diagram_label.get_width() + diagram_label_gap + diagram_content_width + speed_gap + speed_section_width

        current_x = screen_w / 2 - total_diagram_width / 2
        self.screen.blit(diagram_label, diagram_label.get_rect(left=current_x, centery=y_pos + box_h / 2))
        current_x += diagram_label.get_width() + diagram_label_gap

        for i, step_text in enumerate(steps):
            box_rect = pygame.Rect(current_x, y_pos, box_w, box_h)
            # 【修改3】使用新的、对比度更高的颜色
            pygame.draw.rect(self.screen, DIAGRAM_BOX_COLOR, box_rect, border_radius=10)
            if i == 0:
                pygame.draw.circle(self.screen, GREEN_ICON_COLOR, box_rect.center, 12)
            elif i == 1:
                pygame.draw.lines(self.screen, BLACK, False, [(box_rect.left + 30, box_rect.centery + 15),
                                                              (box_rect.centerx, box_rect.centery - 15),
                                                              (box_rect.right - 30, box_rect.centery + 15)], 4)
            else:
                pygame.draw.rect(self.screen, RED_ICON_COLOR, (box_rect.centerx - 12, box_rect.centery - 12, 24, 24))

            label_surf = body_font.render(step_text, True, TEXT_COLOR)
            self.screen.blit(label_surf, label_surf.get_rect(center=(box_rect.centerx, box_rect.bottom + 25)))

            if i < len(steps) - 1:
                arrow_start = (box_rect.right + 5, box_rect.centery)
                arrow_end = (box_rect.right + gap - 5, box_rect.centery)
                # 【修改2】缩短箭头的线，使其被箭头头部完美覆盖
                pygame.draw.line(self.screen, DIVIDER_COLOR, arrow_start, (arrow_end[0] - 10, arrow_end[1]), 4)
                pygame.draw.polygon(self.screen, DIVIDER_COLOR,
                                    [(arrow_end[0], arrow_end[1]), (arrow_end[0] - 12, arrow_end[1] - 7),
                                     (arrow_end[0] - 12, arrow_end[1] + 7)])
            current_x += box_w + gap

        speed_start_x = current_x - gap + speed_gap
        self.screen.blit(speed_label_surf, speed_label_surf.get_rect(
            center=(speed_start_x + speed_label_surf.get_width() / 2, y_pos + box_h / 2)))
        speed_controls_x = speed_start_x + speed_label_surf.get_width() + speed_box_gap
        minus_rect = pygame.Rect(speed_controls_x, y_pos + (box_h - speed_button_size) / 2, speed_button_size,
                                 speed_button_size)
        value_rect = pygame.Rect(minus_rect.right + speed_box_gap, minus_rect.top, speed_value_box_w, speed_button_size)
        plus_rect = pygame.Rect(value_rect.right + speed_box_gap, minus_rect.top, speed_button_size, speed_button_size)

        for rect, symbol in [(minus_rect, "-"), (plus_rect, "+")]:
            pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=5)
            symbol_surf = speed_button_symbol_font.render(symbol, True, BLACK)
            self.screen.blit(symbol_surf, symbol_surf.get_rect(center=rect.center))

        pygame.draw.rect(self.screen, (240, 240, 240), value_rect, border_radius=3)
        pygame.draw.rect(self.screen, (100, 100, 100), value_rect, 2, border_radius=3)
        value_surf = body_font.render("50", True, BLACK)
        self.screen.blit(value_surf, value_surf.get_rect(center=value_rect.center))

        # 【修改1】修正高亮问题
        full_hint_text = '+ 和 - 可调节速度'
        speed_highlight_words = ['+', '-']
        # 使用 re.split 来正确地分割字符串以进行高亮
        speed_hint_parts = [part for part in re.split(r'(\+|-)', full_hint_text) if part]

        speed_hint_surfaces = render_highlighted_text(
            speed_hint_parts, body_font, TEXT_COLOR, HIGHLIGHT_COLOR, speed_highlight_words
        )

        total_hint_width = sum(s.get_width() for s in speed_hint_surfaces)
        speed_module_center_x = speed_start_x + (plus_rect.right - speed_start_x) / 2
        hint_start_x = speed_module_center_x - total_hint_width / 2
        hint_y_pos = minus_rect.bottom + 25

        for surf in speed_hint_surfaces:
            self.screen.blit(surf, (hint_start_x, hint_y_pos))
            hint_start_x += surf.get_width()

        y_pos += box_h + 80

        # --- Section 3: 按键说明 ---
        pygame.draw.line(self.screen, DIVIDER_COLOR, (margin, y_pos), (screen_w - margin, y_pos), 2)
        y_pos += 40

        instruction_parts_list = []
        key_highlight_words = []
        if subject == 'A':
            key_highlight_words = ['W', 'A', 'S', 'D']
            instruction_parts_list.append(
                re.split(r'(W|A|S|D)', f"请{user1}按键：W键控制上, A键控制左, S键控制下, D键控制右。"))
        elif subject in ['B', 'C']:
            key_highlight_words = ['↑', '←', '↓', '→']
            user_mark = user2 if subject == 'B' else user3
            instruction_parts_list.append(
                re.split(r'(↑|←|↓|→)', f"请{user_mark}按键：↑键控制上, ←键控制左, ↓键控制下, →键控制右。"))
        elif subject in ['AB', 'AC']:
            key_highlight_words = ['A', 'D', '↑', '↓']
            partner_mark = user2 if subject == 'AB' else user3
            line1_parts = re.split(r'(A|D)', f"合作任务：请{user1}使用A键控制左, D键控制右")
            line2_parts = re.split(r'(↑|↓)', f"　　　　　请{partner_mark}使用↑键控制上, ↓键控制下")
            instruction_parts_list.append(line1_parts)
            instruction_parts_list.append(line2_parts)

        for parts in instruction_parts_list:
            # 过滤掉 re.split 可能产生的空字符串
            parts = [p for p in parts if p]
            surfaces = render_highlighted_text(parts, body_font, TEXT_COLOR, HIGHLIGHT_COLOR, key_highlight_words)
            total_width = sum(s.get_width() for s in surfaces)
            current_text_x = screen_w / 2 - total_width / 2
            for surf in surfaces:
                self.screen.blit(surf, (current_text_x, y_pos))
                current_text_x += surf.get_width()
            y_pos += body_font.get_height() + 10
        y_pos += 20

        # --- Section 4: 键盘示意图 ---
        draw_keyboard_layout(self.screen, screen_w / 2, y_pos, key_font, key_highlight_words)
        y_pos += 140

        # --- Section 5: 底部提示 ---
        prompt_bar_rect = pygame.Rect(0, screen_h - 80, screen_w, 80)
        pygame.draw.rect(self.screen, (222, 226, 230), prompt_bar_rect)
        prompt_part1 = prompt_font.render("准备好后，请按", True, TEXT_COLOR)
        prompt_part2_key = prompt_font.render("空格", True, PROMPT_GREEN_COLOR)
        prompt_part3_suffix = prompt_font.render("键开始实验", True, TEXT_COLOR)
        prompt_parts = [prompt_part1, prompt_part2_key, prompt_part3_suffix]
        total_prompt_width = sum(part.get_width() for part in prompt_parts) + 16
        current_x = (screen_w - total_prompt_width) / 2
        for part in prompt_parts:
            self.screen.blit(part, part.get_rect(left=current_x, centery=prompt_bar_rect.centery))
            current_x += part.get_width() + 8

        pygame.display.update()

    def display_end_screen(self, is_training=False):
        """显示标准化的结束画面"""
        BG_COLOR, TEXT_COLOR, ACCENT_COLOR = (230, 230, 230), (0, 0, 0), (0, 255, 0)
        screen_width, screen_height = self.screen.get_width(), self.screen.get_height()

        try:
            title_font, subtitle_font, note_font = pygame.font.Font(get_font_path(), 88), pygame.font.Font(
                get_font_path(), 78), pygame.font.Font(get_font_path(), 78)
        except IOError:
            title_font, subtitle_font, note_font = pygame.font.SysFont(None, 100), pygame.font.SysFont(None,
                                                                                                       78), pygame.font.SysFont(
                None, 45)

        self.screen.fill(BG_COLOR)

        title_text = "恭喜您完成练习" if is_training else "恭喜您完成实验"
        title_surf = title_font.render(title_text, True, TEXT_COLOR)
        self.screen.blit(title_surf, title_surf.get_rect(center=(screen_width / 2, 220)))

        subtitle_surf = subtitle_font.render("数据已保存", True, TEXT_COLOR)
        self.screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(screen_width / 2, 420)))

        note_parts = [("按", TEXT_COLOR), ("Esc", ACCENT_COLOR), ("返回主界面", TEXT_COLOR)]
        note_surfaces = [note_font.render(text, True, color) for text, color in note_parts]
        total_width = sum(surf.get_width() for surf in note_surfaces)
        current_x = (screen_width - total_width) / 2
        for surf in note_surfaces:
            self.screen.blit(surf, surf.get_rect(left=current_x, centery=screen_height - 100))
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
    time_pattern = re.compile(r'绘图时长：([\d.]+)')
    percentage_pattern = re.compile(r'百分比：([\d.]+)%')

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
    total_time = sum(times)
    summary_lines = [f"任务平均完成度: {avg_percentage:.2f}%", f"任务总用时: {total_time:.2f}秒"]
    for i, text in enumerate(summary_lines):
        text_surface = summary_font.render(text, True, black)
        screen.blit(text_surface, text_surface.get_rect(center=(screen.get_width() / 2, 200 + i * 100)))


def dataloading_1(time_records, timestamps, root_folder, id, participant_folder, total_images):
    base_path = f"./{root_folder}/{id}/{participant_folder}/output_image"
    data_file_path = f"./{root_folder}/{id}/{participant_folder}/data/数据.txt"

    if os.path.exists(data_file_path): os.remove(data_file_path)

    for i in range(total_images):
        pre_img = cv2.imread(f"{base_path}/pre_screenshot{i}.png")
        post_img = cv2.imread(f"{base_path}/post_screenshot{i}.png")
        if pre_img is not None and post_img is not None:
            calculate_pixel_difference_test(pre_img, post_img, time_records[i], time_records[i + 1], timestamps[i],
                                            root_folder, id, participant_folder)

    # 偏差区域计算（如果需要）
    # for i in range(total_images):
    #     post_img = cv2.imread(f"{base_path}/post_screenshot{i}.png")
    #     if post_img is not None:
    #         deviation_area1(post_img)


def loading_animation(self, WINDOW_WIDTH, WINDOW_HEIGHT, font):
    """标准化的加载动画"""
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


def calculate_pixel_difference_test(origin_image, image1, image2, t1, t2, timestamp, root_folder, id, participant_folder, total_pause_time=0):
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
    # 计算纯绘图时间（t1,t2已经在paint.py中减去了暂停时间）
    time_diff = abs(t2 - t1) if t1 and t2 else 0
    output_path = f"./{root_folder}/{id}/{participant_folder}/data/数据.txt"
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(
            f"有效像素: {overlap_pixels}   总像素: {total_pixels}   百分比：{overlap_percentage:.2f}%   绘图时长：{time_diff} \n")


def dataloading_1(time_records, timestamps, root_folder, id, participant_folder, total_images, total_pause_time=0):
    """统一的数据加载和计算函数"""
    base_path = f"./{root_folder}/{id}/{participant_folder}/output_image"
    data_file_path = f"./{root_folder}/{id}/{participant_folder}/data/数据.txt"
    if os.path.exists(data_file_path): os.remove(data_file_path)
    
    # 检查基准图像是否存在
    reference_path = f"{base_path}/post_screenshot-1.png"
    if not os.path.exists(reference_path):
        print(f"Warning: Reference image not found: {reference_path}")
        return
    
    image = cv2.imread(reference_path)
    if image is None:
        print(f"Warning: Could not read reference image: {reference_path}")
        return
    
    for i in range(total_images):
        pre_img = cv2.imread(f"{base_path}/pre_screenshot{i}.png")
        post_img = cv2.imread(f"{base_path}/post_screenshot{i}.png")
        if pre_img is not None and post_img is not None:
            calculate_pixel_difference_test(image, pre_img, post_img, time_records[i], time_records[i + 1], timestamps[i],
                                            root_folder, id, participant_folder, total_pause_time)


if __name__ == '__main__':
    game = Game()
    game.run()