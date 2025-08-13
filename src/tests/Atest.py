#!/usr/bin/python3
from src.utils.resource_cleanup import safe_pygame_quit
# -*- coding: utf-8 -*-
import time
import cv2
import numpy as np
import pygame
import sys
import os
import random
import re
import gc

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
import keyboard
# --- 全局参数 ---
green = (0, 0, 255)
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
    button_hover = (31, 71, 136)  # 深蓝色悬停背景
    button_border_hover = (31, 71, 136)  # 深蓝色悬停边框
    button_text_color = (0, 0, 0)  # 黑色按钮文字
    hint_text_color = (0, 0, 0)  # 黑色提示文字

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
                # 屏蔽Windows键
                if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                    continue
                if event.key == pygame.K_f:
                    return
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                button_hover_state = confirm_button.collidepoint(mouse_pos)
                # 设置鼠标光标
                if button_hover_state:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
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
        current_text_color = (255, 255, 255) if button_hover_state else button_text_color
        button_text = button_font.render("确定", True, current_text_color)
        button_text_rect = button_text.get_rect(center=confirm_button.center)
        screen.blit(button_text, button_text_rect)

        # 绘制Y键提示
        hint_text = hint_font.render("按F键", True, hint_text_color)
        hint_rect = hint_text.get_rect(center=(dialog_x + dialog_width // 2, button_y + button_height + 30))
        screen.blit(hint_text, hint_rect)

        pygame.display.flip()
        clock.tick(20)

def show_confirm_dialog(screen, title, message):
    """
    显示确认对话框的函数版本，避免状态保存问题
    返回 True (确认) 或 False (取消)
    """
    # 保存当前屏幕内容
    original_screen = screen.copy()

    # 对话框尺寸和位置（增加高度以容纳提示文字）
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    dialog_width = 800
    dialog_height = 450  # 增加高度
    dialog_x = (screen_width - dialog_width) // 2
    dialog_y = (screen_height - dialog_height) // 2
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

    # 颜色定义（匹配CustomDialog样式）
    bg_color = (255, 255, 255)  # 白色背景
    border_color = (85, 85, 85)  # 灰色边框
    text_color = (0, 0, 0)  # 黑色文字
    button_color = (255, 255, 255)  # 白色按钮背景
    button_border = (204, 204, 204)  # 浅灰色按钮边框
    button_hover = (31, 71, 136)  # 深蓝色悬停背景
    button_border_hover = (31, 71, 136)  # 深蓝色悬停边框
    button_text_color = (0, 0, 0)  # 黑色按钮文字
    hint_text_color = (0, 0, 0)

    # 字体设置
    try:
        title_font = pygame.font.Font(get_font_path(), 60)
        message_font = pygame.font.Font(get_font_path(), 50)
        button_font = pygame.font.Font(get_font_path(), 50)
    except:
        title_font = pygame.font.Font(None, 60)
        message_font = pygame.font.Font(None, 50)
        button_font = pygame.font.Font(None, 50)

    # 按钮设置
    button_width = 220
    button_height = 65
    button_spacing = 65
    total_buttons_width = 2 * button_width + button_spacing
    buttons_start_x = dialog_x + (dialog_width - total_buttons_width) // 2
    button_y = dialog_y + dialog_height - 120  # 上移为提示文字留空间

    yes_button = pygame.Rect(buttons_start_x, button_y, button_width, button_height)
    no_button = pygame.Rect(buttons_start_x + button_width + button_spacing, button_y, button_width, button_height)

    # 悬停状态
    yes_hover = False
    no_hover = False

    def draw_dialog():
        """绘制对话框"""
        # 恢复原始屏幕内容
        screen.blit(original_screen, (0, 0))

        # 绘制半透明背景
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 绘制对话框背景（圆角匹配CustomDialog）
        pygame.draw.rect(screen, bg_color, dialog_rect, border_radius=20)
        pygame.draw.rect(screen, border_color, dialog_rect, 2, border_radius=20)

        # 绘制标题
        title_surface = title_font.render(title, True, text_color)
        title_rect = title_surface.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 60))
        screen.blit(title_surface, title_rect)

        # 绘制消息
        message_surface = message_font.render(message, True, text_color)
        message_rect = message_surface.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 160))
        screen.blit(message_surface, message_rect)

        # 绘制按钮（匹配CustomDialog样式）
        yes_bg_color = button_hover if yes_hover else button_color
        yes_border_color = button_border_hover if yes_hover else button_border
        no_bg_color = button_hover if no_hover else button_color
        no_border_color = button_border_hover if no_hover else button_border

        # 绘制按钮背景（圆角矩形）
        pygame.draw.rect(screen, yes_bg_color, yes_button, border_radius=25)
        pygame.draw.rect(screen, yes_border_color, yes_button, 2, border_radius=25)
        pygame.draw.rect(screen, no_bg_color, no_button, border_radius=25)
        pygame.draw.rect(screen, no_border_color, no_button, 2, border_radius=25)

        # 绘制按钮文字
        yes_text_color = (255, 255, 255) if yes_hover else button_text_color
        no_text_color = (255, 255, 255) if no_hover else button_text_color
        yes_text = button_font.render("是", True, yes_text_color)
        yes_text_rect = yes_text.get_rect(center=yes_button.center)
        screen.blit(yes_text, yes_text_rect)

        no_text = button_font.render("否", True, no_text_color)
        no_text_rect = no_text.get_rect(center=no_button.center)
        screen.blit(no_text, no_text_rect)

        # 绘制按钮下方的提示文字
        yes_hint = pygame.font.Font(get_font_path(), 35).render("按F键", True, hint_text_color)
        yes_hint_rect = yes_hint.get_rect(center=(yes_button.centerx, yes_button.bottom + 25))
        screen.blit(yes_hint, yes_hint_rect)

        no_hint = pygame.font.Font(get_font_path(), 35).render("按J键", True, hint_text_color)
        no_hint_rect = no_hint.get_rect(center=(no_button.centerx, no_button.bottom + 25))
        screen.blit(no_hint, no_hint_rect)

    # 主循环
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 恢复原始屏幕内容并刷新显示
                screen.blit(original_screen, (0, 0))
                pygame.display.flip()
                return False

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                yes_hover = yes_button.collidepoint(mouse_pos)
                no_hover = no_button.collidepoint(mouse_pos)
                # 设置鼠标光标
                if yes_hover or no_hover:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    mouse_pos = pygame.mouse.get_pos()
                    if yes_button.collidepoint(mouse_pos):
                        # 恢复原始屏幕内容并刷新显示
                        screen.blit(original_screen, (0, 0))
                        pygame.display.flip()
                        return True
                    elif no_button.collidepoint(mouse_pos):
                        # 恢复原始屏幕内容并刷新显示
                        screen.blit(original_screen, (0, 0))
                        pygame.display.flip()
                        return False

            elif event.type == pygame.KEYDOWN:
                # 屏蔽Windows键
                if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                    continue
                if event.key == pygame.K_RETURN or event.key == pygame.K_f:
                    # 恢复原始屏幕内容并刷新显示
                    screen.blit(original_screen, (0, 0))
                    pygame.display.flip()
                    return True
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_j:
                    # 恢复原始屏幕内容并刷新显示
                    screen.blit(original_screen, (0, 0))
                    pygame.display.flip()
                    return False

        # 绘制对话框
        draw_dialog()
        pygame.display.flip()
        clock.tick(20)

class Game:
    def __init__(self):
        pygame.init()
        keyboard.block_key('win')
        with open('scroll_value.txt', 'w') as f: f.write('50')
        settings = Settings()
        self.screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), pygame.FULLSCREEN)
        self.font = pygame.font.Font(get_font_path(), 60)
        pygame.display.set_caption('人员①训练')
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.screen.fill(grey)
        # 添加初始化状态标志，避免启动时触发VIDEOEXPOSE弹窗
        self.is_initial_startup = True
        
    def cleanup_game_resources(self):
        """游戏结束时清理资源"""
        try:
            print("[Atest清理] 开始清理游戏资源")
            
            # 1. 清理绘图相关资源
            if hasattr(self, 'level'):
                self.level.clear()
                
            # 2. 清理绘图生成器
            try:
                from src.core.paint import GameDrawing
                game_drawing = GameDrawing()
                if hasattr(game_drawing, 'line_generator'):
                    game_drawing.line_generator.clear_cache()
                print("[Atest清理] 绘图生成器清理完成")
            except Exception as e:
                print(f"[Atest清理] 绘图生成器清理警告: {e}")
            
            # 3. 清理pygame表面
            try:
                if hasattr(self, 'screen') and self.screen:
                    self.screen.fill((128, 128, 128))  # 填充灰色释放内存
                print("[Atest清理] pygame表面清理完成")
            except Exception as e:
                print(f"[Atest清理] pygame表面清理警告: {e}")
            
            # 4. 强制垃圾回收
            gc.collect()
            
            print("[Atest清理] 游戏资源清理完成")
            
        except Exception as e:
            print(f"[Atest清理] 清理过程出现错误: {e}")

    def render_text_with_green_keys(self, text, font, surface, center_pos):
        """渲染带有高亮按键提示的文本"""
        GREEN_COLOR = (0, 0, 255)
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
            self.cleanup_game_resources(); safe_pygame_quit();
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
        button_y, button_size, button_spacing = 30, 60, 40
        minus_button_rect = pygame.Rect(settings.screen_width - 275, button_y, button_size, button_size)
        plus_button_rect = pygame.Rect(settings.screen_width - 130, button_y, button_size, button_size)
        value_display_rect = pygame.Rect(settings.screen_width - 210, button_y, 75, button_size)

        # 显示指导语
        self.display_task_instructions_formatted(subject='A')
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.cleanup_game_resources(); safe_pygame_quit(); sys.exit()
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
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"): self.cleanup_game_resources(); safe_pygame_quit(); sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
            self.clock.tick(20)

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
            dt = self.clock.tick(20) / 1000
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.cleanup_game_resources(); safe_pygame_quit(); sys.exit()
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

                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"): self.cleanup_game_resources(); safe_pygame_quit(); sys.exit()
                    elif event.key == pygame.K_p:
                        paused = not paused
                        if paused:
                            pause_start_time = pygame.time.get_ticks()
                        else:
                            total_pause_time += pygame.time.get_ticks() - pause_start_time
                    elif event.key in [pygame.K_EQUALS, pygame.K_PLUS]:
                        speed_value = min(speed_max, speed_value + speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))
                    elif event.key == pygame.K_MINUS:
                        speed_value = max(speed_min, speed_value - speed_step)
                        with open('scroll_value.txt', 'w') as f:
                            f.write(str(int(speed_value)))

                    # 统一的下一张图逻辑
                    is_next_trigger = (event.key == pygame.K_SPACE and self.level.is_endpoint_reached()) or event.key == pygame.K_n
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
            Button3(settings, self.screen, f"{user_id_display}绘图", 10, 40).draw_button()

            # 绘制速度控制
            speed_font = pygame.font.Font(get_font_path(), 50)
            button_font = pygame.font.Font(get_font_path(), 50)
            value_font = pygame.font.Font(get_font_path(), 30)
            speed_text = speed_font.render("速度:", True, black)
            self.screen.blit(speed_text,
                             speed_text.get_rect(right=minus_button_rect.left - 10, centery=minus_button_rect.centery))
            minus_disabled = speed_value <= speed_min
            minus_color = (200, 200, 200) if minus_disabled else (255, 255, 255);
            minus_border = (180, 180, 180) if minus_disabled else (100, 100, 100)
            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5);
            pygame.draw.rect(self.screen, minus_border, minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, (180, 180, 180) if minus_disabled else black)
            self.screen.blit(minus_text, minus_text.get_rect(center=minus_button_rect.center))
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3);
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            value_text = value_font.render(f"{speed_value_to_level(speed_value)}", True, black)
            self.screen.blit(value_text, value_text.get_rect(center=value_display_rect.center))
            plus_disabled = speed_value >= speed_max
            plus_color = (200, 200, 200) if plus_disabled else (255, 255, 255)
            plus_border = (180, 180, 180) if plus_disabled else (100, 100, 100)
            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, plus_border, plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, (180, 180, 180) if plus_disabled else black)
            self.screen.blit(plus_text, plus_text.get_rect(center=plus_button_rect.center))

            # 绘制状态提示
            step_button = Button(settings, self.screen, "", 1700, 1000)
            center_button = Button4(settings, self.screen, "", 550, 1000)
            key_hint_font = pygame.font.Font(get_font_path(), 50)

            if paused:
                step_button.text, hint_text, center_button.text = "已暂停", "按P键继续", "按Esc键返回主菜单"
                self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                 (settings.screen_width // 2, 60))
                step_button.draw_button();
                center_button.draw_button()
            else:
                if 1 <= stats.game_score <= TOTAL_IMAGES:
                    step_button.text = f"{stats.game_score} / {TOTAL_IMAGES}"
                    hint_text = "按P键暂停"
                    center_button.text = "按空格键继续" if self.level.is_endpoint_reached() else ""
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 60))
                    step_button.draw_button()
                    if center_button.text: center_button.draw_button()
                elif stats.game_score > TOTAL_IMAGES:
                    step_button.text, hint_text = "完成", "任务已完成"
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 60))
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

                likert = LikertScale(screen=self.screen, question=f"请{user_id_display}通过数字键1至7对任务难度进行评分",
                                     position=(260, 400), size=(1400, 500), highlight_user=user_id_display)
                likert_running, score = True, None
                while likert_running:
                    self.screen.fill(grey)
                    draw_data(self, self.screen, data)
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            # 屏蔽Windows键
                            if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                                continue
                            if event.key == pygame.K_ESCAPE:
                                if show_confirm_dialog(self.screen, "",
                                                       "您确定要返回主页面吗？"): self.cleanup_game_resources(); safe_pygame_quit(); sys.exit()
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
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"): wait = False
            self.clock.tick(20)

        self.cleanup_game_resources()
        safe_pygame_quit()

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
        PROMPT_GREEN_COLOR = (0, 0, 255)
        HIGHLIGHT_COLOR = (0, 0, 255)
        GREEN_ICON_COLOR = (0, 0, 255)
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
            body_font_bold = pygame.font.Font(font_name, 42)
            body_font_bold.set_bold(True)
            key_font = pygame.font.Font(font_name, 22)
            key_font.set_bold(True)
            prompt_font = pygame.font.Font(font_name, 45)
            speed_button_symbol_font = pygame.font.Font(font_name, 50)
        except (IOError, TypeError):
            title_font = pygame.font.SysFont('sans-serif', 75, bold=True)
            subtitle_font = pygame.font.SysFont('sans-serif', 55, bold=False)
            body_font = pygame.font.SysFont('sans-serif', 45, bold=False)
            body_font_bold = pygame.font.SysFont('sans-serif', 45, bold=True)
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

        def draw_keyboard_layout(screen, center_x, top_y, key_font, is_highlighted, subject):
            KEY_SIZE = 60
            GAP = 8
            highlight_color_scheme = {'face': HIGHLIGHT_COLOR, 'border': (25, 135, 84), 'text': (255, 255, 255),
                                      'shadow': (150, 150, 150)}
            default_color_scheme = {'face': (245, 245, 245), 'border': (180, 180, 180), 'text': (0, 0, 0),
                                    'shadow': (150, 150, 150)}

            if subject in ['A', 'B', 'C']:  # 单人模式，只显示相应的键盘部分并居中
                if subject == 'A':
                    # 只显示WASD键盘
                    layout = {
                        'W': {'pos': (1, 0)}, 'S': {'pos': (1, 1)}, 'A': {'pos': (0, 1)}, 'D': {'pos': (2, 1)},
                    }
                    user_label = user1
                else:
                    # B和C用户显示方向键
                    layout = {
                        '↑': {'pos': (1, 0)}, '↓': {'pos': (1, 1)}, '←': {'pos': (0, 1)}, '→': {'pos': (2, 1)},
                    }
                    user_label = user2 if subject == 'B' else user3

                # 计算单个键盘的边界
                all_positions = [layout[key]['pos'] for key in layout.keys()]
                min_x = min(pos[0] for pos in all_positions) * (KEY_SIZE + GAP)
                max_x = max(pos[0] for pos in all_positions) * (KEY_SIZE + GAP) + KEY_SIZE
                min_y = min(pos[1] for pos in all_positions) * (KEY_SIZE + GAP)
                max_y = max(pos[1] for pos in all_positions) * (KEY_SIZE + GAP) + KEY_SIZE

                keyboard_width = max_x - min_x
                start_x = center_x - keyboard_width / 2

            else:  # 双人模式，显示完整键盘
                layout = {
                    'W': {'pos': (2.5, 0)}, 'S': {'pos': (2.5, 1)}, 'A': {'pos': (1.5, 1)}, 'D': {'pos': (3.5, 1)},
                    '↑': {'pos': (12, 0)}, '↓': {'pos': (12, 1)}, '←': {'pos': (11, 1)}, '→': {'pos': (13, 1)},
                }
                # 计算整个键盘布局的边界（包含WASD和方向键）
                all_positions = [layout[key]['pos'] for key in layout.keys()]
                min_x = min(pos[0] for pos in all_positions) * (KEY_SIZE + GAP)
                max_x = max(pos[0] for pos in all_positions) * (KEY_SIZE + GAP) + KEY_SIZE
                min_y = min(pos[1] for pos in all_positions) * (KEY_SIZE + GAP)
                max_y = max(pos[1] for pos in all_positions) * (KEY_SIZE + GAP) + KEY_SIZE

                keyboard_width = max_x - min_x
                start_x = center_x - keyboard_width / 2

            # 绘制键盘外围框
            frame_padding = 25
            overall_frame_rect = pygame.Rect(
                start_x + min_x - frame_padding,
                top_y + min_y - frame_padding,
                max_x - min_x + 2 * frame_padding,
                max_y - min_y + 2 * frame_padding
            )
            # 使用更深的边框颜色和更粗的线条，让它看起来像一张完整的键盘图
            pygame.draw.rect(screen, (120, 120, 120), overall_frame_rect, 4, border_radius=15)
            # 添加内部的浅色背景，增强键盘图的视觉效果
            pygame.draw.rect(screen, (250, 250, 250), overall_frame_rect, border_radius=15)

            # 绘制按键
            for key_name, properties in layout.items():
                x_mult, y_mult = properties['pos']
                key_rect = pygame.Rect(start_x + x_mult * (KEY_SIZE + GAP), top_y + y_mult * (KEY_SIZE + GAP), KEY_SIZE,
                                       KEY_SIZE)
                color_scheme = highlight_color_scheme if key_name in is_highlighted else default_color_scheme
                draw_single_key(screen, key_rect, key_name, key_font, color_scheme)

            # 在键盘下方显示用户代号
            label_y = overall_frame_rect.bottom + 30

            if subject in ['A', 'B', 'C']:  # 单人模式
                # 计算单个键盘的中心位置
                keyboard_center_x = start_x + (min_x + max_x) / 2
                user_surf = body_font.render(user_label, True, TEXT_COLOR)
                user_rect = user_surf.get_rect(center=(keyboard_center_x, label_y))
                screen.blit(user_surf, user_rect)

            elif subject == 'AB':  # AB合作
                # 左边显示user1，右边显示user2
                left_keys = ['W', 'A', 'S', 'D']
                right_keys = ['↑', '←', '↓', '→']

                left_positions = [layout[key]['pos'] for key in left_keys]
                left_center_x = start_x + (
                            min(pos[0] for pos in left_positions) + max(pos[0] for pos in left_positions)) / 2 * (
                                            KEY_SIZE + GAP) + KEY_SIZE / 2

                right_positions = [layout[key]['pos'] for key in right_keys]
                right_center_x = start_x + (
                            min(pos[0] for pos in right_positions) + max(pos[0] for pos in right_positions)) / 2 * (
                                             KEY_SIZE + GAP) + KEY_SIZE / 2

                # 绘制user1
                user1_surf = body_font.render(user1, True, TEXT_COLOR)
                user1_rect = user1_surf.get_rect(center=(left_center_x, label_y))
                screen.blit(user1_surf, user1_rect)

                # 绘制user2
                user2_surf = body_font.render(user2, True, TEXT_COLOR)
                user2_rect = user2_surf.get_rect(center=(right_center_x, label_y))
                screen.blit(user2_surf, user2_rect)

            elif subject == 'AC':  # AC合作
                # 左边显示user1，右边显示user3
                left_keys = ['W', 'A', 'S', 'D']
                right_keys = ['↑', '←', '↓', '→']

                left_positions = [layout[key]['pos'] for key in left_keys]
                left_center_x = start_x + (
                            min(pos[0] for pos in left_positions) + max(pos[0] for pos in left_positions)) / 2 * (
                                            KEY_SIZE + GAP) + KEY_SIZE / 2

                right_positions = [layout[key]['pos'] for key in right_keys]
                right_center_x = start_x + (
                            min(pos[0] for pos in right_positions) + max(pos[0] for pos in right_positions)) / 2 * (
                                             KEY_SIZE + GAP) + KEY_SIZE / 2

                # 绘制user1
                user1_surf = body_font.render(user1, True, TEXT_COLOR)
                user1_rect = user1_surf.get_rect(center=(left_center_x, label_y))
                screen.blit(user1_surf, user1_rect)

                # 绘制user3
                user3_surf = body_font.render(user3, True, TEXT_COLOR)
                user3_rect = user3_surf.get_rect(center=(right_center_x, label_y))
                screen.blit(user3_surf, user3_rect)

        # --- 布局开始 ---
        margin = 150
        y_pos = 100

        # --- Section 1: 标题与角色 ---
        title_map = {
            'A': f"单独绘图指导语（{user1}绘图，{user2}和{user3}休息）", 'B': f"{user2}单独绘图指导语（{user2}绘图，{user1}和{user3}休息）", 'C': f"{user3}单独绘图指导语（{user3}绘图，{user1}和{user2}休息）",
            'AB': f"合作绘图指导语（{user1}和{user2}绘图，{user3}休息）", 'AC': f"合作绘图指导语（{user1}和{user3}绘图，{user2}休息）"
        }
        title_text = title_map.get(subject, "绘图指导语")
        title_surf = title_font.render(title_text, True, TEXT_COLOR)
        self.screen.blit(title_surf, title_surf.get_rect(center=(screen_w / 2, y_pos)))
        y_pos += title_surf.get_height()
        # --- Section 2: 任务流程 ---
        pygame.draw.line(self.screen, DIVIDER_COLOR, (margin, y_pos), (screen_w - margin, y_pos), 2)
        y_pos += 5  # 进一步减少分割线后的间距，让第一行紧贴

        # 计算最长标题的宽度，用于对齐冒号
        user_text = {'A': user1, 'B': user2, 'C': user3, 'AB': f"{user1}和{user2}", 'AC': f"{user1}和{user3}"}.get(
            subject, "")

        # 测算三个可能的标题长度
        if subject in ['A', 'B', 'C']:
            title_part = f"请{user_text}单独绘图"
        else:
            title_part = f"请{user_text}合作绘图"

        test_titles = [title_part, "键盘控制光标", "速度调节功能"]
        max_title_width = max(body_font_bold.size(title)[0] for title in test_titles)
        colon_x = margin + max_title_width  # 冒号的固定x位置（从左边margin开始）

        # 绘制任务描述，让冒号对齐
        full_desc_text = f"{title_part}：通过键盘控制光标从蓝色起点沿黑色轨迹移动至红色终点"
        title_surf = body_font_bold.render(title_part, True, TEXT_COLOR)
        colon_surf = body_font.render("：", True, TEXT_COLOR)
        content_surf = body_font.render("通过键盘控制光标从蓝色起点沿黑色轨迹移动至红色终点", True, TEXT_COLOR)

        # 绘制标题部分（右对齐到冒号位置）
        title_x = colon_x - title_surf.get_width()
        self.screen.blit(title_surf, (title_x, y_pos))
        # 绘制冒号
        self.screen.blit(colon_surf, (colon_x, y_pos))
        # 绘制内容部分（基于整个屏幕宽度居中，但确保不与左侧标题重叠）
        ideal_content_x = (screen_w - content_surf.get_width()) / 2
        min_content_x = colon_x + colon_surf.get_width() + 20  # 冒号后至少留20px间距
        content_x = max(ideal_content_x, min_content_x)
        self.screen.blit(content_surf, (content_x, y_pos))
        y_pos += body_font.get_height() + 50  # 增加第一行后的间距，让第一条分割线往下移

        # 绘制任务流程图（无"流程示意图："标签）
        steps = ["任务起点", "沿轨迹绘图", "任务终点"]
        box_w, box_h = 180, 80
        gap = 30
        diagram_content_width = len(steps) * box_w + (len(steps) - 1) * gap
        current_x = screen_w / 2 - diagram_content_width / 2

        for i, step_text in enumerate(steps):
            box_rect = pygame.Rect(current_x, y_pos, box_w, box_h)
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
                pygame.draw.line(self.screen, DIVIDER_COLOR, arrow_start, (arrow_end[0] - 10, arrow_end[1]), 4)
                pygame.draw.polygon(self.screen, DIVIDER_COLOR,
                                    [(arrow_end[0], arrow_end[1]), (arrow_end[0] - 12, arrow_end[1] - 7),
                                     (arrow_end[0] - 12, arrow_end[1] + 7)])
            current_x += box_w + gap

        y_pos += box_h + 75  # 增加更多间距，让第二条分割线出现在01下面

        # --- Section 3: 按键说明 ---
        pygame.draw.line(self.screen, DIVIDER_COLOR, (margin, y_pos), (screen_w - margin, y_pos), 2)
        y_pos += 35

        instruction_parts_list = []
        key_highlight_words = []

        # 添加按键说明文字，冒号对齐
        control_title = "键盘控制光标"
        control_title_surf = body_font_bold.render(control_title, True, TEXT_COLOR)
        colon_surf = body_font.render("：", True, TEXT_COLOR)

        # 绘制标题部分（右对齐到冒号位置）
        title_x = colon_x - control_title_surf.get_width()
        self.screen.blit(control_title_surf, (title_x, y_pos))
        # 绘制冒号
        self.screen.blit(colon_surf, (colon_x, y_pos))

        # 绘制内容部分（高亮按键）
        if subject == 'A':
            key_highlight_words = ['W', 'S', 'A', 'D']
            content_text = f"{user1}控制W键向上，S键向下，A键向左，D键向右"
        elif subject in ['B', 'C']:
            key_highlight_words = ['↑', '↓', '←', '→']
            user_mark = user2 if subject == 'B' else user3
            content_text = f"{user_mark}控制↑键向上，↓键向下，←键向左，→键向右"
        elif subject in ['AB', 'AC']:
            key_highlight_words = ['A', 'D', '↑', '↓']
            partner_mark = user2 if subject == 'AB' else user3
            content_text = f"       {user1}控制A键向左，D键向右；   {partner_mark}控制↑键向上，↓键向下"

        # 使用正则表达式分割并高亮按键
        if subject == 'A':
            content_parts = [p for p in re.split(r'(W|S|A|D)', content_text) if p]
        elif subject in ['B', 'C']:
            content_parts = [p for p in re.split(r'(↑|↓|←|→)', content_text) if p]
        elif subject in ['AB', 'AC']:
            content_parts = [p for p in re.split(r'(A|D|↑|↓)', content_text) if p]

        content_surfaces = render_highlighted_text(content_parts, body_font, TEXT_COLOR, HIGHLIGHT_COLOR, key_highlight_words)
        # 计算内容总宽度并基于整个屏幕宽度居中显示，但确保不与左侧标题重叠
        total_content_width = sum(s.get_width() for s in content_surfaces)
        ideal_text_x = (screen_w - total_content_width) / 2
        min_text_x = colon_x + colon_surf.get_width() + 20  # 冒号后至少留20px间距
        current_text_x = max(ideal_text_x, min_text_x)
        for surf in content_surfaces:
            self.screen.blit(surf, (current_text_x, y_pos))
            current_text_x += surf.get_width()
        y_pos += body_font.get_height() + 40  # 增加间距

        # 绘制键盘图
        if subject == 'A':
            draw_keyboard_layout(self.screen, screen_w / 2, y_pos, key_font, key_highlight_words, subject)
        elif subject in ['B', 'C']:
            draw_keyboard_layout(self.screen, screen_w / 2, y_pos, key_font, key_highlight_words, subject)
        elif subject in ['AB', 'AC']:
            draw_keyboard_layout(self.screen, screen_w / 2, y_pos, key_font, key_highlight_words, subject)

        y_pos += 200  # 增加键盘图和第三条分割线之间的间距，让第三条分割线出现在01下面
        y_pos += 10  # 将第三条分割线往下移动10像素，避免与人员代号重叠
        
        # 在键盘控制光标和速度调节功能之间加一条分割线
        pygame.draw.line(self.screen, DIVIDER_COLOR, (margin, y_pos), (screen_w - margin, y_pos), 2)
        y_pos += 30  # 减少第三条分割线后的间距，让第三行往上移

        # 添加速度调节功能说明，冒号对齐，高亮+和-
        speed_title = "速度调节功能"
        speed_title_surf = body_font_bold.render(speed_title, True, TEXT_COLOR)
        colon_surf = body_font.render("：", True, TEXT_COLOR)

        # 绘制标题部分（右对齐到冒号位置）
        title_x = colon_x - speed_title_surf.get_width()
        self.screen.blit(speed_title_surf, (title_x, y_pos))
        # 绘制冒号
        self.screen.blit(colon_surf, (colon_x, y_pos))

        # 绘制内容部分（高亮+和-符号）
        speed_content_text = "如需要调节光标移动速度，可通过键盘上的-或+键进行操作"
        speed_highlight_words = ['+', '-']

        # 分割文本并高亮+和-
        speed_content_parts = []
        temp_text = speed_content_text

        # 处理 + 符号
        if '+' in temp_text:
            parts = temp_text.split('+')
            for i, part in enumerate(parts):
                if part:
                    speed_content_parts.append(part)
                if i < len(parts) - 1:
                    speed_content_parts.append('+')
        else:
            speed_content_parts.append(temp_text)

        # 重新组合并处理 - 符号
        final_content_parts = []
        for part in speed_content_parts:
            if '-' in part and part != '-':
                sub_parts = part.split('-')
                for i, sub_part in enumerate(sub_parts):
                    if sub_part:
                        final_content_parts.append(sub_part)
                    if i < len(sub_parts) - 1:
                        final_content_parts.append('-')
            else:
                final_content_parts.append(part)

        speed_content_parts = [part for part in final_content_parts if part]
        speed_content_surfaces = render_highlighted_text(speed_content_parts, body_font, TEXT_COLOR, HIGHLIGHT_COLOR, speed_highlight_words)

        # 计算总宽度并基于整个屏幕宽度居中显示，但确保不与左侧标题重叠
        total_speed_content_width = sum(s.get_width() for s in speed_content_surfaces)
        ideal_speed_x = (screen_w - total_speed_content_width) / 2
        min_speed_x = colon_x + colon_surf.get_width() + 20  # 冒号后至少留20px间距
        current_speed_x = max(ideal_speed_x, min_speed_x)
        for surf in speed_content_surfaces:
            self.screen.blit(surf, (current_speed_x, y_pos))
            current_speed_x += surf.get_width()
        y_pos += speed_title_surf.get_height() + 40  # 增加间距

        # --- Section 4: 速度示意图 ---
        speed_button_size = 55
        speed_value_box_w = 75
        speed_box_gap = 10

        # 计算速度示意图的总宽度
        speed_controls_width = 2 * speed_button_size + speed_value_box_w + 2 * speed_box_gap
        speed_start_x = screen_w / 2 - speed_controls_width / 2

        minus_rect = pygame.Rect(speed_start_x, y_pos, speed_button_size, speed_button_size)
        value_rect = pygame.Rect(minus_rect.right + speed_box_gap, y_pos, speed_value_box_w, speed_button_size)
        plus_rect = pygame.Rect(value_rect.right + speed_box_gap, y_pos, speed_button_size, speed_button_size)

        for rect, symbol in [(minus_rect, "-"), (plus_rect, "+")]:
            pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=5)
            symbol_surf = speed_button_symbol_font.render(symbol, True, BLACK)
            self.screen.blit(symbol_surf, symbol_surf.get_rect(center=rect.center))

        pygame.draw.rect(self.screen, (240, 240, 240), value_rect, border_radius=3)
        pygame.draw.rect(self.screen, (100, 100, 100), value_rect, 2, border_radius=3)
        value_surf = body_font.render("50", True, BLACK)
        self.screen.blit(value_surf, value_surf.get_rect(center=value_rect.center))

        y_pos += speed_button_size + 30

        # --- Section 5: 底部提示 ---
        prompt_bar_rect = pygame.Rect(0, screen_h - 80, screen_w, 80)
        pygame.draw.rect(self.screen, (222, 226, 230), prompt_bar_rect)
        prompt_part1 = prompt_font.render("准备就绪后，请按键盘", True, TEXT_COLOR)
        prompt_part2_key = prompt_font.render("空格", True, PROMPT_GREEN_COLOR)
        prompt_part3_suffix = prompt_font.render("键开始绘图", True, TEXT_COLOR)
        prompt_parts = [prompt_part1, prompt_part2_key, prompt_part3_suffix]
        total_prompt_width = sum(part.get_width() for part in prompt_parts) + 16
        current_x = (screen_w - total_prompt_width) / 2
        for part in prompt_parts:
            self.screen.blit(part, part.get_rect(left=current_x, centery=prompt_bar_rect.centery))
            current_x += part.get_width() + 8

        pygame.display.update()

    def display_end_screen(self, is_training=False):
        """显示标准化的结束画面"""
        BG_COLOR, TEXT_COLOR, ACCENT_COLOR = (255, 255, 255), (0, 0, 0), (0, 0, 255)
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
    # 手动对齐，确保冒号位置一致
    line1 = f"任务完成度：{avg_percentage:6.2f}%"
    line2 = f"任务总用时：{total_time:6.2f}秒"
    summary_lines = [line1, line2]
    
    # 计算文字块的整体宽度，然后居中显示，文字左对齐
    max_width = max(summary_font.size(line)[0] for line in summary_lines)
    start_x = (screen.get_width() - max_width) // 2
    
    for i, text in enumerate(summary_lines):
        text_surface = summary_font.render(text, True, black)
        screen.blit(text_surface, (start_x, 200 + i * 100))


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
        clock.tick(20)


def calculate_pixel_difference_test(origin_image, image1, image2, t1, t2, timestamp, root_folder, id, participant_folder, total_pause_time=0):
    x, y, width, height = 0, 50, 1920, 920
    image1_cropped = image1[y:y + height, x:x + width]
    image2_cropped = image2[y:y + height, x:x + width]
    gray_origin = cv2.cvtColor(image1_cropped, cv2.COLOR_BGR2GRAY)
    black_mask = (gray_origin < 50)
    hsv_image2 = cv2.cvtColor(image2_cropped, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv_image2, lower_blue, upper_blue) > 0
    overlap_mask = black_mask & blue_mask
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