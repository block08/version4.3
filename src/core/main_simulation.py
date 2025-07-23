#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import cv2
import pygame
import sys
import math
from src.core import game_function as gf
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


def handle_image_navigation(game_drawing, numbers, current_index, self, action="next"):
    """统一处理图片导航逻辑，确保图片按固定顺序显示"""

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
    button_hover = (240, 240, 240)  # 浅灰色悬停背景
    button_border_hover = (153, 153, 153)  # 深灰色悬停边框
    button_text_color = (0, 0, 0)  # 黑色按钮文字
    hint_text_color = (136, 136, 136)  # 灰色提示文字

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
        yes_text = button_font.render("是", True, button_text_color)
        yes_text_rect = yes_text.get_rect(center=yes_button.center)
        screen.blit(yes_text, yes_text_rect)

        no_text = button_font.render("否", True, button_text_color)
        no_text_rect = no_text.get_rect(center=no_button.center)
        screen.blit(no_text, no_text_rect)

        # 绘制按钮下方的提示文字
        yes_hint = pygame.font.Font(get_font_path(), 35).render("按Y键", True, hint_text_color)
        yes_hint_rect = yes_hint.get_rect(center=(yes_button.centerx, yes_button.bottom + 25))
        screen.blit(yes_hint, yes_hint_rect)

        no_hint = pygame.font.Font(get_font_path(), 35).render("按N键", True, hint_text_color)
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
                if event.key == pygame.K_RETURN or event.key == pygame.K_y:
                    # 恢复原始屏幕内容并刷新显示
                    screen.blit(original_screen, (0, 0))
                    pygame.display.flip()
                    return True
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                    # 恢复原始屏幕内容并刷新显示
                    screen.blit(original_screen, (0, 0))
                    pygame.display.flip()
                    return False

        # 绘制对话框
        draw_dialog()
        pygame.display.flip()
        clock.tick(60)


class Game:

    def __init__(self, stop_event=None):
        # 初始化
        pygame.init()
        self.stop_event = stop_event
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
        button_y = 10  # 调整到与暂停提示对齐的高度(40-30=10)
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
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # 暂停计时器
                        if not paused:
                            pause_start_time = pygame.time.get_ticks()
                            paused = True

                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            pygame.quit()
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
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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

        # 自动显示第一张图片
        t1, timestamp1 = game_drawing.random_painting(numbers1[0], self, 0)
        stats.game_score = 1  
        first_image_shown = True

        while running:
            dt = self.clock.tick(60) / 1000

            # 确保背景正确刷新
            self.screen.fill(grey)

            user_button2 = Button3(settings, self.screen, f"航天员:{user1}", 10, 20)
            step_button2 = Button(settings, self.screen, "", 1700, 1000)

            mouse_pos = pygame.mouse.get_pos()

            # 处理键盘和鼠标事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEOEXPOSE:  # 处理窗口重绘事件
                    self.screen.fill(grey)
                elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                    speed_value = handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max,
                                                      speed_value, speed_step, button_states)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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
                                                 (settings.screen_width // 2, 40))
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
                                                     (settings.screen_width // 2, 40))
                    step_button2.draw_button()
                    if center_button.text:  # 只有有文字时才绘制按钮
                        center_button.draw_button()
                elif stats.game_score > 8:
                    step_button2.text = "完成"
                    hint_text = "任务已完成"
                    center_button.text = ""
                    # 完成时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 40))
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
                with open(f"Behavioral_data/id.txt", "r") as file:
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
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
                            else:
                                key_pressed = event.key

                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(),
                                          key_pressed=key_pressed)

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
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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
        speed_min, speed_max = 0, 100
        speed_step = 10

        # 按钮状态用于长按功能
        button_states = {'minus_pressed': False, 'plus_pressed': False, 'last_change_time': 0}

        # 按钮位置设置
        button_y = 10  # 调整到与暂停提示对齐的高度(40-30=10)
        button_size = 60
        button_spacing = 40

        # 减速按钮
        minus_button_rect = pygame.Rect(settings.screen_width - 275, button_y, button_size, button_size)
        # 加速按钮
        plus_button_rect = pygame.Rect(settings.screen_width - 130, button_y, button_size, button_size)
        # 数值显示区域
        value_display_rect = pygame.Rect(settings.screen_width - 210, button_y, 75, button_size)

        with open(f"Behavioral_data/id.txt", "r") as file:
            id = file.read().strip()

        # 自动显示第一张图片
        t1, timestamp1 = game_drawing.random_painting(numbers2[0], self, 11)
        stats.game_score = 12
        first_image_shown = True

        while running:
            dt = self.clock.tick(60) / 1000

            # 确保背景正确刷新
            self.screen.fill(grey)

            # 设置按钮
            user_button2 = Button3(settings, self.screen, f"航天员:{user1}和{user2}", 10, 20)
            step_button2 = Button(settings, self.screen, "", 1700, 1000)

            mouse_pos = pygame.mouse.get_pos()

            # 处理键盘和鼠标事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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
                                                 (settings.screen_width // 2, 40))
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
                                                     (settings.screen_width // 2, 40))
                    step_button2.draw_button()
                    if center_button.text:  # 只有有文字时才绘制按钮
                        center_button.draw_button()
                elif stats.game_score > 19:
                    step_button2.text = "完成"
                    hint_text = "任务已完成"
                    center_button.text = ""
                    # 完成时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 40))
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
                with open(f"Behavioral_data/id.txt", "r") as file:
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
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
                            else:
                                key_pressed = event.key

                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(),
                                          key_pressed=key_pressed)

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

        rest_instructions(self, rest_duration=2)  # 120秒休息倒计时
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
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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
        speed_min, speed_max = 0, 100
        speed_step = 10

        # 按钮状态用于长按功能
        button_states = {'minus_pressed': False, 'plus_pressed': False, 'last_change_time': 0}

        # 按钮位置设置
        button_y = 10  # 调整到与暂停提示对齐的高度(40-30=10)
        button_size = 60
        button_spacing = 40

        # 减速按钮
        minus_button_rect = pygame.Rect(settings.screen_width - 275, button_y, button_size, button_size)
        # 加速按钮
        plus_button_rect = pygame.Rect(settings.screen_width - 130, button_y, button_size, button_size)
        # 数值显示区域
        value_display_rect = pygame.Rect(settings.screen_width - 210, button_y, 75, button_size)

        with open(f"Behavioral_data/id.txt", "r") as file:
            id = file.read().strip()

        # 自动显示第一张图片
        t1, timestamp1 = game_drawing.random_painting(numbers3[0], self, 23)
        stats.game_score = 24
        first_image_shown = True

        while running:
            dt = self.clock.tick(60) / 1000

            # 确保背景正确刷新
            self.screen.fill(grey)

            # 设置按钮
            user_button2 = Button3(settings, self.screen, f"航天员:{user1}和{user3}", 10, 20)
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
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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
                                                 (settings.screen_width // 2, 40))
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
                                                     (settings.screen_width // 2, 40))
                    step_button2.draw_button()
                    if center_button.text:  # 只有有文字时才绘制按钮
                        center_button.draw_button()
                elif stats.game_score > 31:
                    step_button2.text = "完成"
                    hint_text = "任务已完成"
                    center_button.text = ""
                    # 完成时显示右下角按钮和顶部提示
                    self.render_text_with_green_keys(hint_text, key_hint_font, self.screen,
                                                     (settings.screen_width // 2, 40))
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
                with open(f"Behavioral_data/id.txt", "r") as file:
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
                            if event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
                            else:
                                key_pressed = event.key

                    # 更新量表
                    score = likert.update(mouse_pos=pygame.mouse.get_pos(),
                                          key_pressed=key_pressed)

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
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
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

        start_ticks = pygame.time.get_ticks()
        running = True
        countdown_time = 1
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
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            pygame.quit()
                            sys.exit()
                    elif event.key == pygame.K_x:  # x键跳过静息态倒计时
                        running = False
                        self.screen.fill(grey)
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
                        if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                            wait = False
                        else:
                            # 如果取消，重新显示结束界面
                            self.display_end_screen()
            self.clock.tick(60)  # 限制帧率，减少CPU使用
        pygame.quit()
        return


    def render_text_with_green_keys(self, text, font, surface, center_pos):
        """渲染带绿色按键高亮的文本"""
        GREEN_COLOR = (0, 255, 0)
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
            main_font = pygame.font.Font(get_font_path(), 48)  # 增大主字体
            sub_font = pygame.font.Font(get_font_path(), 34)  # 增大子字体
            desc_font = pygame.font.Font(get_font_path(), 48)  # 新增描述字体
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
        desc_rect = desc_surf.get_rect(center=(screen_width / 2, 340))
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
                arrow_tip,  # 箭头尖端
                (line_end[0], line_end[1] - arrow_size // 2),  # 左上角 (与线条终点对齐)
                (line_end[0], line_end[1] + arrow_size // 2)  # 左下角 (与线条终点对齐)
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
        key_info_parts = [("实验中可按 ", TEXT_COLOR), ("P", GREEN_COLOR), (" 键暂停  ;  按 ", TEXT_COLOR),
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
            'A': f"{user1}单人绘图任务指导语", 'B': f"{user2}单人绘图任务指导语", 'C': f"{user3}单人绘图任务指导语",
            'AB': f"{user1}和{user2}合作绘图任务指导语", 'AC': f"{user1}和{user3}合作绘图任务指导语"
        }
        title_text = title_map.get(subject, "绘图任务指导语")
        title_surf = title_font.render(title_text, True, TEXT_COLOR)
        self.screen.blit(title_surf, title_surf.get_rect(center=(screen_w / 2, y_pos)))
        y_pos += title_surf.get_height()

        role_map = {
            'A': f"请{user1}绘图，{user2}和{user3}休息", 'B': f"请{user2}绘图，{user1}和{user3}休息",
            'C': f"请{user3}绘图，{user1}和{user2}休息",
            'AB': f"请{user1}和{user2}绘图，{user3}休息", 'AC': f"请{user1}和{user3}绘图，{user2}休息"
        }
        role_text = role_map.get(subject, "")
        role_surf = subtitle_font.render(role_text, True, TEXT_COLOR)
        self.screen.blit(role_surf, role_surf.get_rect(center=(screen_w / 2, y_pos + 20)))
        y_pos += role_surf.get_height() + 50

        # --- Section 2: 任务流程图与速度 ---
        pygame.draw.line(self.screen, DIVIDER_COLOR, (margin, y_pos), (screen_w - margin, y_pos), 2)
        y_pos += 40

        user_text = {'A': user1, 'B': user2, 'C': user3, 'AB': f"{user1}和{user2}", 'AC': f"{user1}和{user3}"}.get(
            subject, "")
        full_desc_text = f"{user_text}航天员需控制键盘，沿黑色轨迹从绿色起点移动至红色终点。"
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
            line1_parts = re.split(r'(A|D)', f"合作任务：请{user1}使用A键控制左, D键控制右；")
            line2_parts = re.split(r'(↑|↓)', f"请{partner_mark}使用↑键控制上, ↓键控制下。")
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
            special_words = {"空格键": GREEN}

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
        BG_COLOR = (230, 230, 230)  # 与其他界面保持一致的灰色背景
        BOX_COLOR = (144, 197, 114)  # 与流程图相同的绿色框
        TEXT_COLOR = (0, 0, 0)
        ACCENT_COLOR = (0, 255, 0)  # 绿色强调
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


def rest_instructions(self, rest_duration=2):
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

        # 如果暂停，添加暂停提示
        if paused:
            countdown_text += " (已暂停)"

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
                    # 暂停计时器
                    if not paused:
                        pause_start_time = time.time()
                        paused = True

                    if show_confirm_dialog(self.screen, "", "您确定要返回主页面吗？"):
                        pygame.quit()
                        sys.exit()
                    else:
                        # 用户选择继续，恢复计时器
                        if paused:
                            total_pause_time += time.time() - pause_start_time
                            paused = False

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    game = Game()
    game.run()