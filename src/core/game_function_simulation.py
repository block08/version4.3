#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import pygame
from src.data.handle_slider_event import handle_slider_event
from src.core.paint import GameDrawing


grey = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
# 滚轮参数
wheel_x = 50
wheel_y = 50
wheel_width = 20
wheel_height = 100
handle_height = 20
handle_y = wheel_y
# 初始化记录变量
current_value = 125
value = 0  # 滚轮数值

import os  # 导入一个专门处理文件路径的工具


try:
    # 获取当前这个python脚本文件所在的文件夹的完整路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(script_dir, '..', '..', 'sound', 'click.wav')
    if not os.path.exists(sound_path):
        # 备用方案：如果 sound 文件夹和您的脚本在同一个文件夹里
        sound_path = os.path.join(script_dir, 'sound', 'click.wav')
    pygame.mixer.init()
    click_sound = pygame.mixer.Sound(sound_path)

except Exception as e:
    print(f"加载声音文件时出错: {e}")
    print(f"尝试加载的路径是: {sound_path}")
    # 如果找不到文件，最好让程序停下来，这样能立刻发现问题
    sys.exit()

game_drawing = GameDrawing()

# 响应按键和鼠标事件
def check_events(self, stats, button1, button2, numbers, paused, t1, t2, t3, t4, t5, t6, t7, t8, t9,
                 timestamp1, timestamp2, timestamp3, timestamp4, timestamp5, timestamp6, timestamp7, timestamp8,
                 slider_rect, knob_rect, slider_min, slider_max, slider_value, dragging):
    global this_level
    self.display_surface = pygame.display.get_surface()
    # sprite groups
    self.all_sprites = pygame.sprite.Group()
    current_time = pygame.time.get_ticks()


    with open(f"Behavioral_data/id.txt", "r") as file:
        id = file.read()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # 检测ESC键
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # +键增加速度
                try:
                    with open('scroll_value.txt', 'r') as f:
                        current_speed = float(f.read().strip())
                    # 限制速度范围在50-150之间，每次增加10
                    new_speed = min(150, current_speed + 10)
                    with open('scroll_value.txt', 'w') as f:
                        f.write(str(int(new_speed)))
                except (FileNotFoundError, ValueError):
                    # 如果文件不存在或值无效，设置默认值
                    with open('scroll_value.txt', 'w') as f:
                        f.write('60')
            elif event.key == pygame.K_MINUS:  # -键降低速度
                try:
                    with open('scroll_value.txt', 'r') as f:
                        current_speed = float(f.read().strip())
                    # 限制速度范围在50-150之间，每次减少10
                    new_speed = max(50, current_speed - 10)
                    with open('scroll_value.txt', 'w') as f:
                        f.write(str(int(new_speed)))
                except (FileNotFoundError, ValueError):
                    # 如果文件不存在或值无效，设置默认值
                    with open('scroll_value.txt', 'w') as f:
                        f.write('50')
        # 使用新的按钮事件处理方法
        if button1.handle_event(event, current_time):
            click_sound.play()
            paused = not paused
        if button2.handle_event(event, current_time):
            click_sound.play()
            stats.game_active = True
            if stats.game_active:
                if stats.game_score == 0:

                    t1, timestamp1 = game_drawing.random_painting(numbers[stats.game_score], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 1:

                    t2, timestamp2 = game_drawing.random_painting(numbers[stats.game_score], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 2:

                    t3, timestamp3 = game_drawing.random_painting(numbers[stats.game_score], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 3:

                    t4, timestamp4 = game_drawing.random_painting(numbers[stats.game_score], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 4:

                    t5, timestamp5 = game_drawing.random_painting(numbers[stats.game_score], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 5:

                    t6, timestamp6 = game_drawing.random_painting(numbers[stats.game_score], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 6:

                    t7, timestamp7 = game_drawing.random_painting(numbers[stats.game_score], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 7:

                    t8, timestamp8 = game_drawing.random_painting(numbers[stats.game_score], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 8:
                    t9 = pygame.time.get_ticks() / 1000
                    pygame.image.save(self.screen, f"./Behavioral_data/{id}/subA/output_image/post_screenshot7.png")
                    stats.game_score += 1
                elif stats.game_score == 10:
                    stats.game_score += 1
                elif stats.game_score == 11:

                    t1, timestamp1 = game_drawing.random_painting(numbers[stats.game_score - 11], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 12:


                    t2, timestamp2 = game_drawing.random_painting(numbers[stats.game_score - 11], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 13:


                    t3, timestamp3 = game_drawing.random_painting(numbers[stats.game_score - 11], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 14:


                    t4, timestamp4 = game_drawing.random_painting(numbers[stats.game_score - 11], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 15:


                    t5, timestamp5 = game_drawing.random_painting(numbers[stats.game_score - 11], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 16:


                    t6, timestamp6 = game_drawing.random_painting(numbers[stats.game_score - 11], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 17:


                    t7, timestamp7 = game_drawing.random_painting(numbers[stats.game_score - 11], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 18:


                    t8, timestamp8 = game_drawing.random_painting(numbers[stats.game_score - 11], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 19:

                    t9 = pygame.time.get_ticks() / 1000
                    pygame.image.save(self.screen, f"./Behavioral_data/{id}/subB/output_image/post_screenshot7.png")
                    stats.game_score += 1
                elif stats.game_score == 23:


                    t1, timestamp1 = game_drawing.random_painting(numbers[stats.game_score - 23], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 24:


                    t2, timestamp2 = game_drawing.random_painting(numbers[stats.game_score - 23], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 25:


                    t3, timestamp3 = game_drawing.random_painting(numbers[stats.game_score - 23], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 26:


                    t4, timestamp4 = game_drawing.random_painting(numbers[stats.game_score - 23], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 27:


                    t5, timestamp5 = game_drawing.random_painting(numbers[stats.game_score - 23], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 28:


                    t6, timestamp6 = game_drawing.random_painting(numbers[stats.game_score - 23], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 29:


                    t7, timestamp7 = game_drawing.random_painting(numbers[stats.game_score - 23], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 30:


                    t8, timestamp8 = game_drawing.random_painting(numbers[stats.game_score - 23], self, stats.game_score)
                    stats.game_score += 1
                elif stats.game_score == 31:
                    t9 = pygame.time.get_ticks() / 1000
                    pygame.image.save(self.screen, f"./Behavioral_data/{id}/subA+B/output_image/post_screenshot7.png")
                    stats.game_score += 1

        # 添加滑块事件处理
        slider_value, dragging = handle_slider_event(event, slider_rect, knob_rect,
                                                     slider_min, slider_max,
                                                     slider_value, dragging)
    return paused, t1, t2, t3, t4, t5, t6, t7, t8, t9, timestamp1, timestamp2, timestamp3, timestamp4, timestamp5, timestamp6, timestamp7, timestamp8, slider_value, dragging


# 更新屏幕上的图像，并切换到新屏幕
def update_screen(button):
    button.draw_button()
# 让最近绘制的屏幕可见
