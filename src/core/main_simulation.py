from src.config.config_manager import get_id_file_path
#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import cv2
import pygame
import sys
import math
from src.core import game_function_simulation as gf
from src.utils import shared_data
from src.ui.Button import Button, Button2, Button3, Button4
from src.data.Calculate_pixel_difference import calculate_pixel_difference, calculate_pixel_difference2, \
    calculate_pixel_difference3
from src.data.Deviation_area import deviation_area1, deviation_area2, deviation_area3
from src.utils.game_stats import GameStats
from src.core.level import Level
from src.config.settings import *
import random
from src.ui.likert_scale import LikertScale
from src.data.handle_slider_event import handle_button_event
import csv
import os
from datetime import datetime
from src.core.paint import GameDrawing
from src.utils.font_utils import get_font_path
from src.utils.resource_cleanup import safe_pygame_quit
import re
import keyboard

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
            # 确保速度值在合理范围内
            return max(1, min(100, speed_value))
    except (FileNotFoundError, ValueError):
        # 如果文件不存在或值无效，创建默认文件并返回默认值
        with open('scroll_value.txt', 'w') as f:
            f.write('50')
        return 50


def handle_image_navigation(game_drawing, numbers, current_index, self, total_pause_time=0, action="next"):
    """统一处理图片导航逻辑，确保图片按固定顺序显示"""

    if current_index < len(numbers):
        return game_drawing.random_painting(numbers[current_index], self, current_index, total_pause_time)
    return None, None


# 绘图参数
dots_time = []
green = (0, 0, 255)
black = (0, 0, 0)
grey = (230, 230, 230)
RED = (255, 0, 0)
green1 = (50,128,50)
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
    hint_text_color = (0, 0, 0)  # 灰色提示文字

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
                # 屏蔽Windows键 - 增强版（包含原始键值）
                if (event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER] or 
                    event.key == 91 or event.key == 92):  # 91=左Win键, 92=右Win键
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
        clock.tick(50)


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
    hint_text_color = (0, 0, 0)  # 灰色提示文字

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
            elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                # 重绘对话框
                pass  # 对话框会在循环末尾重绘

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
                # 屏蔽Windows键 - 增强版（包含原始键值）
                if (event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER] or 
                    event.key == 91 or event.key == 92):  # 91=左Win键, 92=右Win键
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
        clock.tick(50)


class Game:

    def __init__(self, stop_event=None):
        # 初始化
        pygame.init()
        keyboard.block_key('win')
        self.stop_event = stop_event
        # 添加初始化状态标志，避免启动时触发VIDEOEXPOSE弹窗
        self.is_initial_startup = True
        # 初始化速度为1级别（对应速度值50）
        with open('scroll_value.txt', 'w') as f:
            f.write('50')
        settings = Settings()
        stats = GameStats(settings)

        # 设置屏幕 - 使用独占全屏模式尝试更好的Windows键屏蔽
        self.screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), 
                                            pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        self.font = pygame.font.Font(get_font_path(), 60)  # 增大字体从40到60
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



        t1, t2, t3, t4, t5, t6, t7, t8, t9 = [None] * 9
        timestamp1, timestamp2, timestamp3, timestamp4, timestamp5, timestamp6, timestamp7, timestamp8 = [None] * 8
        with open('config.txt', 'w') as f:
            f.truncate(0)
            f.write('1')

        # 速度调整按钮设置
        speed_value = read_speed_value()
        speed_min, speed_max = 0, 100
        speed_step = 10

        # 按钮状态用于长按功能
        button_states = {'minus_pressed': False, 'plus_pressed': False, 'last_change_time': 0}

        # 按钮位置设置
        button_y = 30  # 调整到与暂停提示对齐的高度(40-30=10)
        button_size = 60
        button_spacing = 40

        # 减速按钮
        minus_button_rect = pygame.Rect(settings.screen_width - 275, button_y, button_size, button_size)
        # 加速按钮
        plus_button_rect = pygame.Rect(settings.screen_width - 130, button_y, button_size, button_size)
        # 数值显示区域
        value_display_rect = pygame.Rect(settings.screen_width - 210, button_y, 75, button_size)

        self.display_flowchart_instructions()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
                            sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
                        self.screen.fill(grey)
                elif event.type == pygame.QUIT:
                    safe_pygame_quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 如果是初始启动，跳过弹窗直接重绘界面
                    if self.is_initial_startup:
                        self.is_initial_startup = False
                        self.display_flowchart_instructions()
                    else:
                        # 窗口被最小化后恢复，显示简化确认对话框
                        show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                        # 重绘流程图指导语界面
                        self.display_flowchart_instructions()
            self.clock.tick(50)  # 限制帧率，减少CPU使用
        self.display_meditation_instructions()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
                            sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
                        self.screen.fill(grey)
                elif event.type == pygame.QUIT:
                    safe_pygame_quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 窗口被最小化后恢复，触发暂停确认
                    show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                    self.display_meditation_instructions()
            self.clock.tick(50)  # 限制帧率，减少CPU使用

        numbers1 = random.sample(range(1, 9), 8)
        self.screen.fill(grey)
        line_length = 20
        pygame.draw.line(self.screen, green1, (910, 540), (1010, 540), line_length)
        pygame.draw.line(self.screen, green1, (960, 490), (960, 590), line_length)
        pygame.display.update()

        start_ticks = pygame.time.get_ticks()
        running = True
        countdown_time = 120
        paused = False
        pause_start_time = 0
        total_pause_time = 0
        while running:
            # 检查停止信号
            if self.stop_event and self.stop_event.is_set():
                running = False
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    safe_pygame_quit()
                    sys.exit()
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
                    # 重绘静息态界面（绿色十字）
                    self.screen.fill(grey)
                    pygame.draw.line(self.screen, green1, (910, 540), (1010, 540), line_length)
                    pygame.draw.line(self.screen, green1, (960, 490), (960, 590), line_length)
                    pygame.display.update()
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        # 暂停计时器
                        if not paused:
                            pause_start_time = pygame.time.get_ticks()
                            paused = True

                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
                            sys.exit()
                        else:
                            # 用户选择继续，恢复计时器
                            if paused:
                                total_pause_time += pygame.time.get_ticks() - pause_start_time
                                paused = False
                    elif event.key == pygame.K_x:  # x键跳过静息态倒计时
                        running = False
                        self.screen.fill(grey)

            # 计算实际经过的时间（不包括暂停时间）
            current_ticks = pygame.time.get_ticks()
            if paused:
                elapsed_time = (pause_start_time - start_ticks - total_pause_time) / 1000
            else:
                elapsed_time = (current_ticks - start_ticks - total_pause_time) / 1000

            remaining_time = max(0, countdown_time - elapsed_time)
            if remaining_time == 0:
                running = False
                self.screen.fill(grey)
            self.clock.tick(50)  # 限制帧率，减少CPU使用
        # 使用指导语
        self.display_task_instructions_formatted(subject='A')
        waiting_for_space = True
        while waiting_for_space:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    safe_pygame_quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 窗口被最小化后恢复，触发暂停确认
                    show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                    # 重绘任务指导语界面
                    self.display_task_instructions_formatted(subject='A')
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
                            sys.exit()
                    elif event.key == pygame.K_SPACE:
                        waiting_for_space = False
            self.clock.tick(50)  # 限制帧率，减少CPU使用

        # 静息态后等待开始第一张绘图
        self.screen.fill(grey)
        stats.game_score = 0
        paused = False
        first_image_shown = False
        running = True
        current_image_index = 0  # 当前图片索引

        # 读取id变量
        with open(get_id_file_path(), "r") as file:
            id = file.read().strip()

        # 自动显示第一张图片
        t1, timestamp1 = game_drawing.random_painting(numbers1[0], self, 0, total_pause_time)
        stats.game_score = 1  
        first_image_shown = True

        while running:
            dt = self.clock.tick(50) / 1000

            # 确保背景正确刷新
            self.screen.fill(grey)

            user_button2 = Button3(settings, self.screen, f"{user1}绘图", 10, 40)
            step_button2 = Button(settings, self.screen, "", 1700, 1000)

            mouse_pos = pygame.mouse.get_pos()

            # 处理键盘和鼠标事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    safe_pygame_quit()
                    sys.exit()
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
                    if first_image_shown and 1 <= stats.game_score <= 8:
                        updated_time = game_drawing.update_current_timestamp(total_pause_time)
                        # 根据当前图片更新对应的时间变量
                        if stats.game_score == 1:
                            t1 = updated_time
                        elif stats.game_score == 2:
                            t2 = updated_time
                        elif stats.game_score == 3:
                            t3 = updated_time
                        elif stats.game_score == 4:
                            t4 = updated_time
                        elif stats.game_score == 5:
                            t5 = updated_time
                        elif stats.game_score == 6:
                            t6 = updated_time
                        elif stats.game_score == 7:
                            t7 = updated_time
                        elif stats.game_score == 8:
                            t8 = updated_time
                    # 重绘A阶段绘图界面
                    self.screen.fill(grey)
                        # 界面会在循环末尾重绘
                elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                                      speed_value, speed_step, button_states)

                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
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

                            t1, timestamp1 = game_drawing.random_painting(numbers1[0], self, 0, total_pause_time)
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


                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers1[1], self, 1, total_pause_time)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers1[2], self, 2, total_pause_time)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers1[3], self, 3, total_pause_time)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers1[4], self, 4, total_pause_time)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers1[5], self, 5, total_pause_time)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers1[6], self, 6, total_pause_time)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers1[7], self, 7, total_pause_time)
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

                            t1, timestamp1 = game_drawing.random_painting(numbers1[0], self, 0, total_pause_time)
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


                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers1[1], self, 1, total_pause_time)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers1[2], self, 2, total_pause_time)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers1[3], self, 3, total_pause_time)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers1[4], self, 4, total_pause_time)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers1[5], self, 5, total_pause_time)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers1[6], self, 6, total_pause_time)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers1[7], self, 7, total_pause_time)
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

            # --- 减速按钮 ---
            minus_disabled = speed_value <= speed_min
            minus_color = (200, 200, 200) if minus_disabled else (255, 255, 255)
            minus_border_color = (180, 180, 180) if minus_disabled else (100, 100, 100)
            minus_text_color = (180, 180, 180) if minus_disabled else (0, 0, 0)

            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, minus_border_color, minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, minus_text_color)
            minus_text_rect = minus_text.get_rect(center=minus_button_rect.center)
            self.screen.blit(minus_text, minus_text_rect)

            # --- 数值显示 ---
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            speed_level = speed_value_to_level(speed_value)
            value_text = value_font.render(f"{speed_level}", True, (0, 0, 0))
            value_text_rect = value_text.get_rect(center=value_display_rect.center)
            self.screen.blit(value_text, value_text_rect)

            # --- 加速按钮 ---
            plus_disabled = speed_value >= speed_max
            plus_color = (200, 200, 200) if plus_disabled else (255, 255, 255)
            plus_border_color = (180, 180, 180) if plus_disabled else (100, 100, 100)
            plus_text_color = (180, 180, 180) if plus_disabled else (0, 0, 0)

            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, plus_border_color, plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, plus_text_color)
            plus_text_rect = plus_text.get_rect(center=plus_button_rect.center)
            self.screen.blit(plus_text, plus_text_rect)

            # 创建按钮并设置状态
            # 中下方状态提示按钮
            center_button = Button4(settings, self.screen, "", 550, 1000)

            # 显示按键提示
            key_hint_font = pygame.font.Font(get_font_path(), 50)
            if paused:
                step_button2.text = "已暂停"
                hint_text = "按P键继续"
                center_button.text = "按Esc键返回主菜单"
                # 暂停时显示右下角按钮和顶部提示
                self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                 (settings.screen_width // 2, 60))
                step_button2.draw_button()
                center_button.draw_button()
            else:
                if first_image_shown and 1 <= stats.game_score <= 8:
                    step_button2.text = f"{stats.game_score} / 8"
                    hint_text = "按P键暂停"
                    # 只有到达终点时才显示空格键提示
                    if self.level.is_endpoint_reached():
                        center_button.text = "按空格键继续"
                    else:
                        center_button.text = ""
                    # 进行中时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 60))
                    step_button2.draw_button()
                    if center_button.text:  # 只有有文字时才绘制按钮
                        center_button.draw_button()
                elif stats.game_score > 8:
                    step_button2.text = "完成"
                    hint_text = "任务已完成"
                    center_button.text = ""
                    # 完成时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 60))
                    step_button2.draw_button()
                    # 完成时不显示中下方按钮
                else:
                    # 等待开始时：不显示右下角按钮，中下方显示"按空格键开始"
                    center_button.text = "按空格键开始"
                    center_button.draw_button()

            if 0 <= stats.game_score < 9:
                for button in [user_button2]:
                    gf.update_screen(button)

            # 处理长按（即使没有事件也要检查）
            speed_value = handle_button_event(None, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                              speed_value, speed_step, button_states)

            if not paused:
                self.level.run(dt, stats, [], self.screen)
            else:
                # 暂停时只绘制，不更新精灵位置
                self.level.draw(self.screen, stats)
            pygame.display.update()
            if stats.game_score == 9:
                self.level.clear()
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)
                dataloading(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3, timestamp4,
                            timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time)
                with open(get_id_file_path(), "r") as file:
                    id = file.read()
                with open(f"./Behavioral_data/{id}/subA/data/数据.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    data = [f"图像 {i + 1}  {lines[i].strip()} {lines[i].strip()}" for i in range(8)]


                user1 = getattr(shared_data, 'user1_mark', '01')
                # 合并显示数据和量表界面
                likert = LikertScale(screen=self.screen, question=f"请{user1}按下键盘按键1-7评估任务难度:",
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
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            # 屏蔽Windows键
                            if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                                continue
                            if event.key == pygame.K_ESCAPE:
                                # 二次确认退出
                                if show_confirm_dialog(self.screen, "确认退出", "确定要退出实验吗？"):
                                    safe_pygame_quit()
                                    sys.exit()
                            else:
                                key_pressed = event.key
                        elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                            # 窗口被最小化后恢复，触发暂停确认
                            show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                            # 重绘量表界面
                            self.screen.fill(grey)
                            draw_data(self, self.screen, data, "A")

                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(),
                                          key_pressed=key_pressed)

                    pygame.display.flip()
                    self.clock.tick(50)
                    if score is not None:
                        likert_running = False

                # 保存量表结果
                if score is not None:
                    with open(get_id_file_path(), "r") as file:
                        id = file.read()
                    with open(f"./Behavioral_data/{id}/subA/likert_scale/量表.txt", "w") as f:
                        f.write(str(score))

                stats.game_score = 10
                break

        rest_instructions(self, rest_duration=30)
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
                    safe_pygame_quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 窗口被最小化后恢复，触发暂停确认
                    show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                    # 重绘AB任务指导语界面
                    self.display_task_instructions_formatted(subject='AB')
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
                            sys.exit()
                    elif event.key == pygame.K_SPACE:
                        waiting_for_space = False
            self.clock.tick(50)  # 限制帧率，减少CPU使用

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
        speed_min, speed_max = 0, 100
        speed_step = 10

        # 按钮状态用于长按功能
        button_states = {'minus_pressed': False, 'plus_pressed': False, 'last_change_time': 0}

        # 按钮位置设置
        button_y = 30  # 调整到与暂停提示对齐的高度(40-30=10)
        button_size = 60
        button_spacing = 40

        # 减速按钮
        minus_button_rect = pygame.Rect(settings.screen_width - 275, button_y, button_size, button_size)
        # 加速按钮
        plus_button_rect = pygame.Rect(settings.screen_width - 130, button_y, button_size, button_size)
        # 数值显示区域
        value_display_rect = pygame.Rect(settings.screen_width - 210, button_y, 75, button_size)

        with open(get_id_file_path(), "r") as file:
            id = file.read().strip()

        # 自动显示第一张图片
        t1, timestamp1 = game_drawing.random_painting(numbers2[0], self, 11, total_pause_time)
        stats.game_score = 12
        first_image_shown = True

        while running:
            dt = self.clock.tick(50) / 1000

            # 确保背景正确刷新
            self.screen.fill(grey)

            # 设置按钮
            user_button2 = Button3(settings, self.screen, f"{user1}和{user2}绘图", 10, 40)
            step_button2 = Button(settings, self.screen, "", 1700, 1000)

            mouse_pos = pygame.mouse.get_pos()

            # 处理键盘和鼠标事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    safe_pygame_quit()
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
                    if first_image_shown and 12 <= stats.game_score <= 19:
                        updated_time = game_drawing.update_current_timestamp(total_pause_time)
                        # 根据当前图片更新对应的时间变量
                        if stats.game_score == 12:
                            t1 = updated_time
                        elif stats.game_score == 13:
                            t2 = updated_time
                        elif stats.game_score == 14:
                            t3 = updated_time
                        elif stats.game_score == 15:
                            t4 = updated_time
                        elif stats.game_score == 16:
                            t5 = updated_time
                        elif stats.game_score == 17:
                            t6 = updated_time
                        elif stats.game_score == 18:
                            t7 = updated_time
                        elif stats.game_score == 19:
                            t8 = updated_time
                    # 重绘AB协作绘图界面
                    self.screen.fill(grey)
                    # 界面会在循环末尾重绘
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
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

                            t1, timestamp1 = game_drawing.random_painting(numbers2[0], self, 11, total_pause_time)
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


                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers2[1], self, 12, total_pause_time)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers2[2], self, 13, total_pause_time)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers2[3], self, 14, total_pause_time)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers2[4], self, 15, total_pause_time)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers2[5], self, 16, total_pause_time)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers2[6], self, 17, total_pause_time)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers2[7], self, 18, total_pause_time)
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
                    elif event.key == pygame.K_n and not paused:  # N键下一张
                        if not first_image_shown:
                            # 显示第一张图

                            t1, timestamp1 = game_drawing.random_painting(numbers2[0], self, 11, total_pause_time)
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


                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers2[1], self, 12, total_pause_time)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers2[2], self, 13, total_pause_time)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers2[3], self, 14, total_pause_time)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers2[4], self, 15, total_pause_time)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers2[5], self, 16, total_pause_time)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers2[6], self, 17, total_pause_time)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers2[7], self, 18, total_pause_time)
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
            minus_disabled = speed_value <= speed_min
            minus_color = (200, 200, 200) if minus_disabled else (255, 255, 255)
            minus_border_color = (180, 180, 180) if minus_disabled else (100, 100, 100)
            minus_text_color = (180, 180, 180) if minus_disabled else (0, 0, 0)

            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, minus_border_color, minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, minus_text_color)
            minus_text_rect = minus_text.get_rect(center=minus_button_rect.center)
            self.screen.blit(minus_text, minus_text_rect)

            # --- 数值显示 ---
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            speed_level = speed_value_to_level(speed_value)
            value_text = value_font.render(f"{speed_level}", True, (0, 0, 0))
            value_text_rect = value_text.get_rect(center=value_display_rect.center)
            self.screen.blit(value_text, value_text_rect)

            # --- 加速按钮 ---
            plus_disabled = speed_value >= speed_max
            plus_color = (200, 200, 200) if plus_disabled else (255, 255, 255)
            plus_border_color = (180, 180, 180) if plus_disabled else (100, 100, 100)
            plus_text_color = (180, 180, 180) if plus_disabled else (0, 0, 0)

            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, plus_border_color, plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, plus_text_color)
            plus_text_rect = plus_text.get_rect(center=plus_button_rect.center)
            self.screen.blit(plus_text, plus_text_rect)

            # 创建按钮并设置状态
            # 中下方状态提示按钮
            center_button = Button4(settings, self.screen, "", 550, 1000)

            # 显示按键提示
            key_hint_font = pygame.font.Font(get_font_path(), 50)
            if paused:
                step_button2.text = "已暂停"
                hint_text = "按P键继续"
                center_button.text = "按Esc键返回主菜单"
                # 暂停时显示右下角按钮和顶部提示
                self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                 (settings.screen_width // 2, 60))
                step_button2.draw_button()
                center_button.draw_button()
            else:
                if first_image_shown and 12 <= stats.game_score <= 19:
                    step_button2.text = f"{stats.game_score - 11} / 8"
                    hint_text = "按P键暂停"
                    # 只有到达终点时才显示空格键提示
                    if self.level.is_endpoint_reached():
                        center_button.text = "按空格键继续"
                    else:
                        center_button.text = ""
                    # 进行中时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 60))
                    step_button2.draw_button()
                    if center_button.text:  # 只有有文字时才绘制按钮
                        center_button.draw_button()
                elif stats.game_score > 19:
                    step_button2.text = "完成"
                    hint_text = "任务已完成"
                    center_button.text = ""
                    # 完成时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 60))
                    step_button2.draw_button()
                    # 完成时不显示中下方按钮
                else:
                    # 等待开始时：不显示右下角按钮，中下方显示"按空格键开始"
                    center_button.text = "按空格键开始"
                    center_button.draw_button()

            if 10 < stats.game_score < 20:
                for button in [user_button2]:
                    gf.update_screen(button)

            # 处理长按（即使没有事件也要检查）
            speed_value = handle_button_event(None, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                              speed_value, speed_step, button_states)

            # 更新游戏等级
            if not paused:
                self.level.run(dt, stats, [], self.screen)
            else:
                # 暂停时只绘制，不更新精灵位置
                self.level.draw(self.screen, stats)
            pygame.display.update()
            # 处理游戏结束逻辑
            if stats.game_score == 20:
                self.level.clear()  # 调用clear方法彻底清除
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)
                dataloading2(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3, timestamp4,
                             timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time)
                with open(get_id_file_path(), "r") as file:
                    id = file.read()
                with open(f"./Behavioral_data/{id}/subAB/data/数据.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    data = [f"图像{i + 1} {lines[i].strip()} {lines[i].strip()}" for i in range(8)]


                user1 = getattr(shared_data, 'user1_mark', '01')
                # 合并显示数据和量表界面
                likert = LikertScale(screen=self.screen, question=f"请{user1}按下键盘按键1-7评估任务难度:",
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
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            # 屏蔽Windows键
                            if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                                continue
                            if event.key == pygame.K_ESCAPE:
                                # 二次确认退出
                                if show_confirm_dialog(self.screen, "确认退出", "确定要退出实验吗？"):
                                    safe_pygame_quit()
                                    sys.exit()
                            else:
                                key_pressed = event.key
                        elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                            # 窗口被最小化后恢复，触发暂停确认
                            show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                            # 重绘量表界面
                            self.screen.fill(grey)
                            draw_data(self, self.screen, data, "B")
                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(),
                                          key_pressed=key_pressed)

                    pygame.display.flip()
                    self.clock.tick(50)
                    if score is not None:
                        likert_running = False

                # 保存量表结果
                if score is not None:
                    with open(get_id_file_path(), "r") as file:
                        id = file.read()
                    with open(f"./Behavioral_data/{id}/subAB/likert_scale/量表.txt", "w") as f:
                        f.write(str(score))

                stats.game_score = 21
                break

        rest_instructions(self, rest_duration=30)  # 120秒休息倒计时
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
                    safe_pygame_quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 窗口被最小化后恢复，触发暂停确认
                    show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                    # 重绘AC任务指导语界面
                    self.display_task_instructions_formatted(subject='AC')
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
                            sys.exit()
                    elif event.key == pygame.K_SPACE:
                        waiting_for_space = False
            self.clock.tick(50)  # 限制帧率，减少CPU使用

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
        speed_min, speed_max = 0, 100
        speed_step = 10

        # 按钮状态用于长按功能
        button_states = {'minus_pressed': False, 'plus_pressed': False, 'last_change_time': 0}

        # 按钮位置设置
        button_y = 30  # 调整到与暂停提示对齐的高度(40-30=10)
        button_size = 60
        button_spacing = 40

        # 减速按钮
        minus_button_rect = pygame.Rect(settings.screen_width - 275, button_y, button_size, button_size)
        # 加速按钮
        plus_button_rect = pygame.Rect(settings.screen_width - 130, button_y, button_size, button_size)
        # 数值显示区域
        value_display_rect = pygame.Rect(settings.screen_width - 210, button_y, 75, button_size)

        with open(get_id_file_path(), "r") as file:
            id = file.read().strip()

        # 自动显示第一张图片
        t1, timestamp1 = game_drawing.random_painting(numbers3[0], self, 23, total_pause_time)
        stats.game_score = 24
        first_image_shown = True

        while running:
            dt = self.clock.tick(50) / 1000

            # 确保背景正确刷新
            self.screen.fill(grey)

            # 设置按钮
            user_button2 = Button3(settings, self.screen, f"{user1}和{user3}绘图", 10, 40)
            step_button2 = Button(settings, self.screen, "", 1700, 1000)

            mouse_pos = pygame.mouse.get_pos()
            # 检查按钮点击

            # 处理键盘事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    safe_pygame_quit()
                    sys.exit()
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
                    if first_image_shown and 24 <= stats.game_score <= 31:
                        updated_time = game_drawing.update_current_timestamp(total_pause_time)
                        # 根据当前图片更新对应的时间变量
                        if stats.game_score == 24:
                            t1 = updated_time
                        elif stats.game_score == 25:
                            t2 = updated_time
                        elif stats.game_score == 26:
                            t3 = updated_time
                        elif stats.game_score == 27:
                            t4 = updated_time
                        elif stats.game_score == 28:
                            t5 = updated_time
                        elif stats.game_score == 29:
                            t6 = updated_time
                        elif stats.game_score == 30:
                            t7 = updated_time
                        elif stats.game_score == 31:
                            t8 = updated_time
                    # 重绘AC协作绘图界面
                    self.screen.fill(grey)
                    # 界面会在循环末尾重绘
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
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

                            t1, timestamp1 = game_drawing.random_painting(numbers3[0], self, 23, total_pause_time)
                            stats.game_score = 24
                            first_image_shown = True
                        elif stats.game_score < 31 and self.level.is_endpoint_reached():
                            current_image_index = stats.game_score - 23
                            if current_image_index < 8:
                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()

                                # 保存当前绘制内容为post_screenshot
                                with open(get_id_file_path(), "r") as file:
                                    id = file.read().strip()
                                post_screenshot_path = f"./Behavioral_data/{id}/subAC/output_image/post_screenshot{current_image_index - 1}.png"
                                pygame.image.save(self.screen, post_screenshot_path)


                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers3[1], self, 24, total_pause_time)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers3[2], self, 25, total_pause_time)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers3[3], self, 26, total_pause_time)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers3[4], self, 27, total_pause_time)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers3[5], self, 28, total_pause_time)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers3[6], self, 29, total_pause_time)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers3[7], self, 30, total_pause_time)
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

                            t1, timestamp1 = game_drawing.random_painting(numbers3[0], self, 23, total_pause_time)
                            stats.game_score = 24
                            first_image_shown = True
                        elif stats.game_score < 31:
                            current_image_index = stats.game_score - 23
                            if current_image_index < 8:
                                # 确保绘制内容已经显示到屏幕上
                                self.level.run(dt, stats, [], self.screen)
                                pygame.display.update()

                                # 保存当前绘制内容为post_screenshot
                                with open(get_id_file_path(), "r") as file:
                                    id = file.read().strip()
                                post_screenshot_path = f"./Behavioral_data/{id}/subAC/output_image/post_screenshot{current_image_index - 1}.png"
                                pygame.image.save(self.screen, post_screenshot_path)


                                if current_image_index == 1:
                                    t2, timestamp2 = game_drawing.random_painting(numbers3[1], self, 24, total_pause_time)
                                elif current_image_index == 2:
                                    t3, timestamp3 = game_drawing.random_painting(numbers3[2], self, 25, total_pause_time)
                                elif current_image_index == 3:
                                    t4, timestamp4 = game_drawing.random_painting(numbers3[3], self, 26, total_pause_time)
                                elif current_image_index == 4:
                                    t5, timestamp5 = game_drawing.random_painting(numbers3[4], self, 27, total_pause_time)
                                elif current_image_index == 5:
                                    t6, timestamp6 = game_drawing.random_painting(numbers3[5], self, 28, total_pause_time)
                                elif current_image_index == 6:
                                    t7, timestamp7 = game_drawing.random_painting(numbers3[6], self, 29, total_pause_time)
                                elif current_image_index == 7:
                                    t8, timestamp8 = game_drawing.random_painting(numbers3[7], self, 30, total_pause_time)
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
            minus_disabled = speed_value <= speed_min
            minus_color = (200, 200, 200) if minus_disabled else (255, 255, 255)
            minus_border_color = (180, 180, 180) if minus_disabled else (100, 100, 100)
            minus_text_color = (180, 180, 180) if minus_disabled else (0, 0, 0)

            pygame.draw.rect(self.screen, minus_color, minus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, minus_border_color, minus_button_rect, 2, border_radius=5)
            minus_text = button_font.render("-", True, minus_text_color)
            minus_text_rect = minus_text.get_rect(center=minus_button_rect.center)
            self.screen.blit(minus_text, minus_text_rect)

            # --- 数值显示 ---
            pygame.draw.rect(self.screen, (240, 240, 240), value_display_rect, border_radius=3)
            pygame.draw.rect(self.screen, (100, 100, 100), value_display_rect, 2, border_radius=3)
            speed_level = speed_value_to_level(speed_value)
            value_text = value_font.render(f"{speed_level}", True, (0, 0, 0))
            value_text_rect = value_text.get_rect(center=value_display_rect.center)
            self.screen.blit(value_text, value_text_rect)

            # --- 加速按钮 ---
            plus_disabled = speed_value >= speed_max
            plus_color = (200, 200, 200) if plus_disabled else (255, 255, 255)
            plus_border_color = (180, 180, 180) if plus_disabled else (100, 100, 100)
            plus_text_color = (180, 180, 180) if plus_disabled else (0, 0, 0)

            pygame.draw.rect(self.screen, plus_color, plus_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, plus_border_color, plus_button_rect, 2, border_radius=5)
            plus_text = button_font.render("+", True, plus_text_color)
            plus_text_rect = plus_text.get_rect(center=plus_button_rect.center)
            self.screen.blit(plus_text, plus_text_rect)

            # 创建按钮并设置状态
            # 中下方状态提示按钮
            center_button = Button4(settings, self.screen, "", 550, 1000)

            # 显示按键提示
            key_hint_font = pygame.font.Font(get_font_path(), 50)
            if paused:
                step_button2.text = "已暂停"
                hint_text = "按P键继续"
                center_button.text = "按Esc键返回主菜单"
                # 暂停时显示右下角按钮和顶部提示
                self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                 (settings.screen_width // 2, 60))
                step_button2.draw_button()
                center_button.draw_button()
            else:
                if first_image_shown and 24 <= stats.game_score <= 31:
                    step_button2.text = f"{stats.game_score - 23} / 8"
                    hint_text = "按P键暂停"
                    # 只有到达终点时才显示空格键提示
                    if self.level.is_endpoint_reached():
                        center_button.text = "按空格键继续"
                    else:
                        center_button.text = ""
                    # 进行中时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 60))
                    step_button2.draw_button()
                    if center_button.text:  # 只有有文字时才绘制按钮
                        center_button.draw_button()
                elif stats.game_score > 31:
                    step_button2.text = "完成"
                    hint_text = "任务已完成"
                    center_button.text = ""
                    # 完成时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 60))
                    step_button2.draw_button()
                    # 完成时不显示中下方按钮
                else:
                    # 等待开始时：不显示右下角按钮，中下方显示"按空格键开始"
                    center_button.text = "按空格键开始"
                    center_button.draw_button()

            if 22 < stats.game_score < 32:
                for button in [user_button2]:
                    gf.update_screen(button)

            # 处理长按（即使没有事件也要检查）
            speed_value = handle_button_event(None, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                              speed_value, speed_step, button_states)

            # 更新游戏等级
            if not paused:
                self.level.run(dt, stats, [], self.screen)
            else:
                # 暂停时只绘制，不更新精灵位置
                self.level.draw(self.screen, stats)
            pygame.display.update()
            # 处理游戏结束逻辑
            if stats.game_score == 32:
                self.level.clear()  # 调用clear方法彻底清除
                loading_animation(self, settings.screen_width, settings.screen_height, self.font)
                dataloading3(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3, timestamp4,
                             timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time)
                with open(get_id_file_path(), "r") as file:
                    id = file.read()
                with open(f"./Behavioral_data/{id}/subAC/data/数据.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    data = [f"图像{i + 1}{lines[i].strip()}{lines[i].strip()}" for i in range(8)]



                # 合并显示数据和量表界面
                likert = LikertScale(screen=self.screen, question=f"请{user1}按下键盘按键1-7评估任务难度:",
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
                    key_pressed = None
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            # 屏蔽Windows键
                            if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                                continue
                            if event.key == pygame.K_ESCAPE:
                                # 二次确认退出
                                if show_confirm_dialog(self.screen, "确认退出", "确定要退出实验吗？"):
                                    safe_pygame_quit()
                                    sys.exit()
                            else:
                                key_pressed = event.key
                        elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                            # 窗口被最小化后恢复，触发暂停确认
                            show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                            # 重绘量表界面
                            self.screen.fill(grey)
                            draw_data(self, self.screen, data, "AB")
                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(),
                                          key_pressed=key_pressed)

                    pygame.display.flip()
                    self.clock.tick(50)
                    if score is not None:
                        likert_running = False

                # 保存量表结果
                if score is not None:
                    with open(get_id_file_path(), "r") as file:
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
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
                            sys.exit()
                    elif event.key == pygame.K_SPACE:
                        wait = False
                        self.screen.fill(grey)
                elif event.type == pygame.QUIT:
                    safe_pygame_quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 窗口被最小化后恢复，触发暂停确认
                    show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                    # 重绘冥想指导语界面
                    self.display_meditation_instructions()
            self.clock.tick(50)  # 限制帧率，减少CPU使用

        self.screen.fill(grey)
        line_length = 20
        pygame.draw.line(self.screen, green1, (910, 540), (1010, 540), line_length)
        pygame.draw.line(self.screen, green1, (960, 490), (960, 590), line_length)
        pygame.display.update()

        start_ticks = pygame.time.get_ticks()
        running = True
        countdown_time = 120
        paused = False
        pause_start_time = 0
        total_pause_time = 0
        while running:
            # 检查停止信号
            if self.stop_event and self.stop_event.is_set():
                running = False
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    safe_pygame_quit()
                    sys.exit()
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
                    # 重绘静息态界面（绿色十字）
                    self.screen.fill(grey)
                    pygame.draw.line(self.screen, green1, (910, 540), (1010, 540), line_length)
                    pygame.draw.line(self.screen, green1, (960, 490), (960, 590), line_length)
                    pygame.display.update()
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            safe_pygame_quit()
                            sys.exit()
                    elif event.key == pygame.K_x:  # x键跳过静息态倒计时
                        running = False
                        self.screen.fill(grey)
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            remaining_time = max(0, countdown_time - elapsed_time)
            if remaining_time == 0:
                running = False
                self.screen.fill(grey)
            self.clock.tick(50)  # 限制帧率，减少CPU使用
        # 实验结束
        self.display_end_screen()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # 屏蔽Windows键
                    if event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER]:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            wait = False
                        else:
                            # 如果取消，重新显示结束界面
                            self.display_end_screen()
                elif event.type == pygame.QUIT:
                    safe_pygame_quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    # 窗口被最小化后恢复，触发暂停确认
                    show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                    # 重绘结束界面
                    self.display_end_screen()
            self.clock.tick(50)  # 限制帧率，减少CPU使用
        safe_pygame_quit()
        return


    def render_text_with_green_keys(self, text, font, surface, center_pos):
        """渲染带绿色按键高亮的文本"""
        GREEN_COLOR = (0, 0, 255)
        BLACK_COLOR = (0, 0, 0)

        # 定义需要高亮的按键
        key_patterns = ['P', 'Esc', '空格键', '1', '2', '3', '4', '5', '6', '7']

        # 简化算法：使用replace方法
        parts = []
        current_text = text

        # 先找到所有需要高亮的位置
        for pattern in key_patterns:
            if pattern in current_text:
                # 分割文本
                split_parts = current_text.split(pattern)
                new_parts = []

                # 重建parts列表
                for i, part in enumerate(split_parts):
                    if i > 0:  # 在每个分割部分前添加高亮的按键
                        new_parts.append((pattern, GREEN_COLOR))
                    if part:  # 只添加非空部分
                        new_parts.append((part, BLACK_COLOR))

                # 合并文本用于下一次处理
                current_text = ''.join([p[0] for p in new_parts])
                parts = new_parts
                break  # 找到第一个匹配就停止，避免重复处理

        if not parts:
            parts = [(text, BLACK_COLOR)]

        # 计算总宽度
        total_width = sum(font.size(part[0])[0] for part in parts if part[0])
        start_x = center_pos[0] - total_width // 2
        # 使用center_pos[1]作为文本中心的y坐标，需要减去字体高度的一半
        y = center_pos[1] - font.get_height() // 2

        # 渲染所有部分
        for part_text, color in parts:
            if part_text:
                text_surface = font.render(part_text, True, color)
                surface.blit(text_surface, (start_x, y))
                start_x += text_surface.get_width()

    def display_flowchart_instructions(self):
        """以流程图的形式显示实验指导语"""
        # --- Colors and Fonts Initialization ---
        BG_COLOR = (255, 255, 255)
        BOX_COLOR = (220, 220, 220)
        TEXT_COLOR = (0, 0, 0)
        ARROW_COLOR = (0, 0, 0)
        GREEN_COLOR = green

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        try:
            title_font = pygame.font.Font(get_font_path(), 72)  # 增大标题字体
            header_font = pygame.font.Font(get_font_path(), 42)  # 增大头部字体
            main_font = pygame.font.Font(get_font_path(), 48)  # 增大主字体
            sub_font = pygame.font.Font(get_font_path(), 34)  # 增大子字体
            desc_font = pygame.font.Font(get_font_path(), 48)  # 新增描述字体
            prompt_font = pygame.font.Font(get_font_path(), 68)
            prompt_font_bold = pygame.font.Font(get_font_path(), 68)  # 加粗提示字体
            prompt_font_bold.set_bold(True)
            key_info_font = pygame.font.Font(get_font_path(), 60)
        except IOError:
            # Fallback to default system font if 'msyh.ttc' is not found
            title_font = pygame.font.SysFont(None, 75)
            header_font = pygame.font.SysFont(None, 45)
            main_font = pygame.font.SysFont(None, 55)
            sub_font = pygame.font.SysFont(None, 40)
            desc_font = pygame.font.SysFont(None, 40)
            prompt_font = pygame.font.SysFont(None, 50)
            prompt_font_bold = pygame.font.SysFont(None, 50, bold=True)  # 加粗提示字体
            key_info_font = pygame.font.SysFont(None, 30)

        self.screen.fill(BG_COLOR)

        # --- Title ---
        title_font.set_bold(True)
        title_surf = title_font.render("实验流程指导语", True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(screen_width / 2, 200))
        self.screen.blit(title_surf, title_rect)

        # --- 添加流程图描述 ---
        desc_text = "一共5个阶段，请按顺序依次完成，每个阶段均配备指导语"
        desc_surf = desc_font.render(desc_text, True, TEXT_COLOR)
        desc_rect = desc_surf.get_rect(center=(screen_width / 2, 340))
        self.screen.blit(desc_surf, desc_rect)

        user1 = getattr(shared_data, 'user1_mark', None)
        user2 = getattr(shared_data, 'user2_mark', None)
        user3 = getattr(shared_data, 'user3_mark', None)
        # --- Updated Flowchart Steps ---
        # The core change is in this data structure to reflect the new experimental flow.
        flow_steps = [
            {"header": "第1阶段", "main": f"{user1}静息态", "sub": "（2分钟）"},
            {"header": "第2阶段", "main": f"{user1}绘图", "sub": "（约7分钟）"},
            {"header": "第3阶段", "main": f"{user1}&{user2}绘图", "sub": "（约7分钟）"},
            {"header": "第4阶段", "main": f"{user1}&{user3}绘图", "sub": "（约7分钟）"},
            {"header": "第5阶段", "main": f"{user1}静息态", "sub": "（2分钟）"}
        ]

        # --- Layout Calculations for Centering the Flowchart ---
        box_width, box_height = 340, 220  # 增大流程图方框尺寸
        box_gap = 30  # 减小间距让方框更靠近箭头
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

        # Draw connecting arrows using Unicode → symbol
        for i in range(len(box_rects) - 1):
            start_point = box_rects[i].midright
            end_point = box_rects[i + 1].midleft
            
            # 计算箭头位置 (在两个方框中间)
            arrow_x = (start_point[0] + end_point[0]) // 2
            arrow_y = start_point[1]
            
            # 绘制Unicode箭头符号 (使用较小字体避免重合)
            arrow_surf = sub_font.render("→", True, ARROW_COLOR)
            arrow_rect = arrow_surf.get_rect(center=(arrow_x, arrow_y))
            self.screen.blit(arrow_surf, arrow_rect)

        # --- Bottom Prompt and Key Information ---
        # This part remains the same but is positioned lower.
        prompt_y_center = screen_height - 150
        prompt_parts = [("请按 ", TEXT_COLOR, prompt_font), ("空格键", GREEN_COLOR, prompt_font_bold), (" 开始实验", TEXT_COLOR, prompt_font)]
        prompt_surfaces = [font.render(text, True, color) for text, color, font in prompt_parts]
        total_prompt_width = sum(s.get_width() for s in prompt_surfaces)
        current_x = (screen_width - total_prompt_width) / 2
        for surf in prompt_surfaces:
            rect = surf.get_rect(left=current_x, centery=prompt_y_center)
            self.screen.blit(surf, rect)
            current_x += surf.get_width()

        key_info_y_bottom = screen_height - 40
        key_info_parts = [("实验中可按 ", TEXT_COLOR), ("P", GREEN_COLOR), (" 键暂停  ; 可按 ", TEXT_COLOR),
                          ("ESC", GREEN_COLOR), (" 键退出", TEXT_COLOR)]
        key_info_surfaces = [key_info_font.render(text, True, color) for text, color in key_info_parts]
        total_key_info_width = sum(s.get_width() for s in key_info_surfaces)
        current_x = (screen_width - total_key_info_width) / 2
        for surf in key_info_surfaces:
            rect = surf.get_rect(left=current_x, bottom=key_info_y_bottom)
            self.screen.blit(surf, rect)
            current_x += surf.get_width()

        pygame.display.update()

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
            label_y = overall_frame_rect.bottom + 15

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
            'A': f"单独绘图指导语（{user1}绘图，{user2}和{user3}休息）",
            'B': f"{user2}单独绘图指导语（{user2}绘图，{user1}和{user3}休息）",
            'C': f"{user3}单独绘图指导语（{user3}绘图，{user1}和{user2}休息）",
            'AB': f"合作绘图指导语（{user1}和{user2}绘图，{user3}休息）",
            'AC': f"合作绘图指导语（{user1}和{user3}绘图，{user2}休息）"
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
            title_part = f"双人合作绘图"

        test_titles = [title_part, "键盘控制光标", "速度调节功能"]
        max_title_width = max(body_font_bold.size(title)[0] for title in test_titles)
        colon_x = margin + max_title_width  # 冒号的固定x位置（从左边margin开始）

        # 绘制任务描述，让冒号对齐
        full_desc_text = f"{title_part}：通过键盘控制光标从绿色起点沿黑色轨迹移动至红色终点"
        title_surf = body_font_bold.render(title_part, True, TEXT_COLOR)
        colon_surf = body_font.render("：", True, TEXT_COLOR)
        content_surf = body_font.render("通过键盘控制光标从绿色起点沿黑色轨迹移动至红色终点", True, TEXT_COLOR)

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
            content_text = f"{user1}控制A键向左，D键向右； {partner_mark}控制↑键向上，↓键向下"

        # 使用正则表达式分割并高亮按键
        if subject == 'A':
            content_parts = [p for p in re.split(r'(W|S|A|D)', content_text) if p]
        elif subject in ['B', 'C']:
            content_parts = [p for p in re.split(r'(↑|↓|←|→)', content_text) if p]
        elif subject in ['AB', 'AC']:
            content_parts = [p for p in re.split(r'(A|D|↑|↓)', content_text) if p]

        content_surfaces = render_highlighted_text(content_parts, body_font, TEXT_COLOR, HIGHLIGHT_COLOR,
                                                   key_highlight_words)
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
        speed_content_surfaces = render_highlighted_text(speed_content_parts, body_font, TEXT_COLOR, HIGHLIGHT_COLOR,
                                                         speed_highlight_words)

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

    def display_meditation_instructions(self, title=None, instructions=None, special_words=None):
        """显示冥想指导语"""
        BLACK = (0, 0, 0)
        GREEN = green

        self.screen.fill(grey)
        user1 = getattr(shared_data, 'user1_mark', None)
        try:
            font_large = pygame.font.Font(get_font_path(), 78)
            font_large_bold = pygame.font.Font(get_font_path(), 78)
            font_large_bold.set_bold(True)
            font_medium = pygame.font.Font(get_font_path(), 65)
        except:
            font_large = pygame.font.SysFont(None, 48)
            font_large_bold = pygame.font.SysFont(None, 48, bold=True)
            font_medium = pygame.font.SysFont(None, 40)

        if title is None: title = f"请{user1}进行2分钟静息态实验"
        if instructions is None:
            instructions = ["放松身体 保持静止", "避免思考 放松大脑", "睁开双眼 减少眨眼",
                            "双手双脚 避免交叉", "按空格键开始"]
        if special_words is None:
            special_words = {"空格键": GREEN}

        title_surface = font_large_bold.render(title, True, BLACK)
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
        BG_COLOR = (230, 230, 230)  # 与其他界面保持一致的灰色背景
        BOX_COLOR = (144, 197, 114)  # 与流程图相同的绿色框
        TEXT_COLOR = (0, 0, 0)
        ACCENT_COLOR = (0, 0, 255) # 绿色强调
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
    # 手动对齐，确保冒号位置一致
    line1 = f"任务完成度：{avg_percentage:6.2f}%"
    line2 = f"任务总用时：{total_time:6.2f}秒"
    summary_lines = [line1, line2]

    # 创建字体对象
    summary_font = pygame.font.Font(get_font_path(), 60)
    
    # 计算文字块的整体宽度，然后居中显示，文字左对齐
    max_width = max(summary_font.size(line)[0] for line in summary_lines)
    start_x = (screen.get_width() - max_width) // 2
    
    for i, text in enumerate(summary_lines):
        text_surface = summary_font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (start_x, 200 + i * 100))


def dataloading(t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3,
                timestamp4, timestamp5, timestamp6, timestamp7, timestamp8, total_pause_time=0):
    with open(get_id_file_path(), "r") as file:
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
    with open(get_id_file_path(), "r") as file:
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
    with open(get_id_file_path(), "r") as file:
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
        clock.tick(50)


def rest_instructions(self, rest_duration=30):
    """
    显示休息指导文本并进行倒计时
    rest_duration: 休息时长（秒），默认120秒（2分钟）
    """
    import time

    # 颜色定义
    BLACK = (0, 0, 0)
    GREEN = green
    RED = (0, 0, 255)

    # 加载字体
    try:
        font_large = pygame.font.Font(get_font_path(), 72)
        font_large.set_bold(True)  # 设置标题字体为加粗
        font_medium = pygame.font.Font(get_font_path(), 50)
        font_countdown = pygame.font.Font(get_font_path(), 72)
    except:
        # 如果没有黑体字库，使用默认字体
        font_large = pygame.font.SysFont(None, 72, bold=True)  # 设置为加粗
        font_medium = pygame.font.SysFont(None, 50)
        font_countdown = pygame.font.SysFont(None, 72)

    # 文本内容
    title = "休息期间指导语"
    instruction_lines = [
        "请您保持身体处于放松状态，可暂时将视线从屏幕移开。",
        "休息期间，请尽量减少肢体活动，避免剧烈运动，",
        "以防影响电极的导电性能和数据采集质量。"

    ]

    # 倒计时循环
    start_time = time.time()
    clock = pygame.time.Clock()
    paused = False
    pause_start_time = 0
    total_pause_time = 0

    while True:
        # 检查停止信号
        if hasattr(self, 'stop_event') and self.stop_event and self.stop_event.is_set():
            break

        # 计算实际经过的时间（不包括暂停时间）
        current_time = time.time()
        if paused:
            elapsed = pause_start_time - start_time - total_pause_time
        else:
            elapsed = current_time - start_time - total_pause_time

        remaining = max(0, rest_duration - elapsed)

        if remaining <= 0:
            break

        # 清空屏幕
        self.screen.fill(grey)

        # 显示标题
        title_surface = font_large.render(title, True, BLACK)
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title_surface, title_rect)

        # 显示指导文本（自动换行，以最长行为基准居中，其他行左边界对齐）
        y_pos = 280
        line_height = 150
        max_width = 600  # 文本块最大宽度
        
        for paragraph in instruction_lines:
            # 将长文本分割成多行
            words = paragraph.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                test_surface = font_medium.render(test_line, True, BLACK)
                if test_surface.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                        current_line = word + " "
                    else:
                        lines.append(word)
                        current_line = ""
            
            if current_line:
                lines.append(current_line.strip())
            
            # 找到最长的行
            max_line_width = 0
            for line in lines:
                line_width = font_medium.size(line)[0]
                if line_width > max_line_width:
                    max_line_width = line_width
            
            # 以最长行为基准计算左边界位置（居中）
            start_x = (self.screen.get_width() - max_line_width) // 2
            
            # 渲染每一行，都从同样的左边界开始
            for line in lines:
                text_surface = font_medium.render(line, True, BLACK)
                self.screen.blit(text_surface, (start_x, y_pos - text_surface.get_height() // 2))
                y_pos += line_height

        # 显示倒计时
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        countdown_text = f"{minutes:02d}:{seconds:02d}"

        # 如果暂停，添加暂停提示
        if paused:
            countdown_text += " (已暂停)"

        # 最后30秒变红色
        countdown_color = RED if remaining <= 30 else GREEN
        countdown_surface = font_countdown.render(countdown_text, True, countdown_color)
        countdown_rect = countdown_surface.get_rect(center=(self.screen.get_width() // 2, 750))
        self.screen.blit(countdown_surface, countdown_rect)

        # 检查退出事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                safe_pygame_quit()
                sys.exit()
            elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                # 窗口被最小化后恢复，独立处理暂停时间
                minimize_pause_start = time.time()
                # 如果当前已经是P键暂停状态，先记录P键暂停的时间
                if paused:
                    total_pause_time += minimize_pause_start - pause_start_time
                show_minimize_dialog(self.screen, "检测到最小化，点击继续")
                minimize_pause_end = time.time()
                # 累加最小化暂停时间
                total_pause_time += minimize_pause_end - minimize_pause_start
                # 如果之前是P键暂停状态，重新开始计时
                if paused:
                    pause_start_time = minimize_pause_end
                pass
            elif event.type == pygame.KEYDOWN:
                # 屏蔽Windows键 - 增强版（包含原始键值）
                if (event.key in [pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER] or 
                    event.key == 91 or event.key == 92):  # 91=左Win键, 92=右Win键
                    continue
                if event.key == pygame.K_ESCAPE:
                    # 暂停计时器
                    if not paused:
                        pause_start_time = time.time()
                        paused = True

                    if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                        safe_pygame_quit()
                        sys.exit()
                    else:
                        # 用户选择继续，恢复计时器
                        if paused:
                            total_pause_time += time.time() - pause_start_time
                            paused = False

        pygame.display.flip()
        clock.tick(50)


if __name__ == '__main__':
    game = Game()
    game.run()