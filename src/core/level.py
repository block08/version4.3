from src.config.config_manager import get_id_file_path
#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pygame
from typing import List

draw_width = 2
# 颜色定义
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
grey = (230,230,230)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
LINEWIDTH = 4
RED = (255, 0, 0)
DARK_BLUE = (0, 0, 139)  # 深蓝色
TOP_MARGIN = 100  # 顶部预留空间
BOTTOM_MARGIN = 100  # 底部预留空间


class EndPoint(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, control_mode=None):
        super().__init__()
        self.x = pos[0]
        self.y = pos[1]
        self.base_speed = 0.5
        self.angle = 0
        self.angle_speed = 0.8
        self.last_speed_check = 0  # 上次检查速度文件的时间
        self.image = pygame.Surface((6, 6))
        self.image.fill((0, 255, 0))  # GREEN
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.last_pos = (self.x, self.y)
        self.initial_pos = (self.x, self.y)  # 记录初始起点位置
        self.turning_left = False
        self.turning_right = False
        self.is_moving = False
        self.current_direction = None  # 记录当前移动方向
        self.key_press_count = {
            'up': 0,
            'down': 0,
            'left': 0,
            'right': 0
        }
        self.key_pressed_last_frame = {
            'up': False,
            'down': False,
            'left': False,
            'right': False
        }
        # 如果没有传入控制模式，则自己读取配置文件
        if control_mode is None:
            try:
                with open('config.txt', 'r') as f:
                    current_state = f.read().strip()
                    if current_state == '1':
                        self.control_mode = 'A'
                    elif current_state == '2':
                        self.control_mode = 'B'
                    elif current_state == '3':
                        self.control_mode = 'C'
            except FileNotFoundError:
                self.control_mode = 'A'  # 默认使用A模式
        else:
            self.control_mode = control_mode

    def move(self, keys):
        current_key_states = {
            'up': keys[pygame.K_UP],
            'down': keys[pygame.K_DOWN],
            'left': keys[pygame.K_a],
            'right': keys[pygame.K_d]
        }

        # 计算按键次数
        for direction, is_pressed in current_key_states.items():
            if is_pressed and not self.key_pressed_last_frame[direction]:
                self.key_press_count[direction] += 1

            # 更新上一帧的按键状态
            self.key_pressed_last_frame[direction] = is_pressed
        moved = False
        dx = 0
        dy = 0

        # 获取屏幕边界
        screen = pygame.display.get_surface()
        sprite_width = self.rect.width
        sprite_height = self.rect.height

        playable_left = 0
        playable_right = screen.get_width()
        playable_top = 50  # TOP_MARGIN
        playable_bottom = screen.get_height() - 50  # BOTTOM_MARGIN

        # 根据控制模式判断移动键
        move_up = move_down = move_left = move_right = False
        if self.control_mode == 'A':
            # 被试A：WASD控制上下左右
            move_up = keys[pygame.K_w]
            move_down = keys[pygame.K_s]
            move_left = keys[pygame.K_a]
            move_right = keys[pygame.K_d]
        elif self.control_mode == 'B':  # 控制模式B
            move_up = keys[pygame.K_UP]
            move_down = keys[pygame.K_DOWN]
            move_left = keys[pygame.K_LEFT]
            move_right = keys[pygame.K_RIGHT]
        elif self.control_mode == 'C':
            # C模式：AD控制左右，上下键控制上下
            move_up = keys[pygame.K_UP]
            move_down = keys[pygame.K_DOWN]
            move_left = keys[pygame.K_a]
            move_right = keys[pygame.K_d]

        # 检测是否有移动键被按下
        any_movement_key = move_up or move_down or move_left or move_right
        self.is_moving = any_movement_key

        # 如果没有移动，立即将角度重置为0
        if not self.is_moving:
            self.angle = 0
            self.current_direction = None
            return False

        # 检测转向意图
        if keys[pygame.K_LEFT]:
            self.turning_left = True
            self.turning_right = False
        elif keys[pygame.K_RIGHT]:
            self.turning_right = True
            self.turning_left = False
        else:
            self.turning_left = False
            self.turning_right = False

        # 确定移动方向
        if move_left:  # 左
            dx = -self.base_speed
            moved = True
            self.current_direction = 'left'
        if move_right:  # 右
            dx = self.base_speed
            moved = True
            self.current_direction = 'right'
        if move_up:  # 上
            dy = -self.base_speed
            moved = True
            self.current_direction = 'up'
        if move_down:  # 下
            dy = self.base_speed
            moved = True
            self.current_direction = 'down'

        # 根据移动方向调整角度变化
        if moved:
            # 保存当前位置
            self.last_pos = (self.x, self.y)

            # 计算新位置
            new_x = self.x + dx
            new_y = self.y + dy

            # 边界检查
            if (new_x >= playable_left + sprite_width / 2 and
                    new_x <= playable_right - sprite_width / 2):
                self.x = new_x

            if (new_y >= playable_top + sprite_height / 2 and
                    new_y <= playable_bottom - sprite_height / 2):
                self.y = new_y

            self.rect.center = (self.x, self.y)

        return moved

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        if current_time % 1000 == 0:
            try:
                with open('config.txt', 'r') as f:
                    current_state = f.read().strip()
                    if current_state == '1':
                        self.control_mode = 'A'
                    elif current_state == '2':
                        self.control_mode = 'B'
                    elif current_state == '3':
                        self.control_mode = 'C'
            except FileNotFoundError:
                pass

        if current_time - self.last_speed_check >= 200:
            try:
                with open('scroll_value.txt', 'r') as f:
                    speed_value = float(f.read().strip())
                    self.base_speed = speed_value / 100.0
            except (FileNotFoundError, ValueError):
                pass

        keys = pygame.key.get_pressed()
        self.move(keys)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def get_position(self):
        return (self.x, self.y)

    def get_angle(self):
        return self.angle

    def get_key_press_count(self):
        return self.key_press_count

    def reset_key_press_count(self):
        for key in self.key_press_count:
            self.key_press_count[key] = 0
        for key in self.key_pressed_last_frame:
            self.key_pressed_last_frame[key] = False


class Level:
    MAX_SPRITES = 30

    def __init__(self):
        self.last_key_press_count = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        self.display_surface = pygame.display.get_surface()
        self.drawing_surface = pygame.Surface((
            self.display_surface.get_width(),
            self.display_surface.get_height() - TOP_MARGIN - BOTTOM_MARGIN
        ))
        self.drawing_surface.fill(grey)
        self.player = None
        self.font = pygame.font.Font(None, 24)
        self.all_sprites = {i: pygame.sprite.Group() for i in range(self.MAX_SPRITES)}
        self.end_sprites = {i: pygame.sprite.Group() for i in range(self.MAX_SPRITES)}
        self.current_sprite_index = 0
        self.line_points = {}
        self.endpoint_reached = False

    def _setup_player(self, index: int, x: int, y: int) -> None:
        self.player = Player((x, y + TOP_MARGIN))
        self.all_sprites[index].add(self.player)

    def _setup_endpoint(self, index: int, x: int, y: int) -> None:
        self.end_sprites[index].add(EndPoint((x, y + TOP_MARGIN), self.end_sprites[index]))

    for i in range(MAX_SPRITES):
        exec(f"""def setup{i}(self, x, y): self._setup_player({i}, x, y)""")
        exec(f"""def setup_endpoint{i}(self, x, y): self._setup_endpoint({i}, x, y)""")

    def draw(self, screen, stats=None):
        try:
            temp_surface = screen.copy()
        except pygame.error as e:
            print(f"屏幕复制错误: {e}")
            # 创建一个新的surface作为备选
            temp_surface = pygame.Surface(screen.get_size())
            temp_surface.fill((255, 255, 255))  # 白色背景
        try:
            with open('config.txt', 'r') as f:
                current_state = f.read().strip()
        except FileNotFoundError:
            current_state = '1'

        # 【重要修正】只修改这里的判断条件，并统一为单个变量
        condition_met = False
        if stats:
            # 个人A模式：游戏分数0-8
            if current_state == '1' and 0 <= stats.game_score <= 8:
                condition_met = True
            # Btest模式：游戏分数11-15
            elif current_state == '2' and 11 <= stats.game_score <= 15:
                condition_met = True
            # 协作AB模式：游戏分数11-19
            elif current_state == '3' and 11 <= stats.game_score <= 19:
                condition_met = True
            # 协作AC模式：游戏分数23-31  
            elif current_state == '3' and 23 <= stats.game_score <= 31:
                condition_met = True

        if condition_met:
            screen.blit(self.drawing_surface, (0, TOP_MARGIN))

        for endpoint_group in self.end_sprites.values():
            endpoint_group.draw(screen)

        if self.player:
            current_pos = (self.player.x, self.player.y)
            if self.player.last_pos != current_pos:
                last_pos_adjusted = (self.player.last_pos[0], self.player.last_pos[1] - TOP_MARGIN)
                current_pos_adjusted = (current_pos[0], current_pos[1] - TOP_MARGIN)

                # 【重要修正】使用与上面相同的条件变量
                if condition_met:
                    pygame.draw.line(
                        self.drawing_surface, GREEN,
                        last_pos_adjusted, current_pos_adjusted,
                        LINEWIDTH
                    )
            self.player.draw(screen)
            
            # 在原始起点位置绘制固定的绿色标记
            initial_pos_screen = (int(self.player.initial_pos[0]), int(self.player.initial_pos[1]))
            pygame.draw.rect(screen, (0, 255, 0), 
                           (initial_pos_screen[0] - 8, initial_pos_screen[1] - 8, 16, 16))

        pygame.draw.rect(screen, BLACK, (
            0, TOP_MARGIN,
            screen.get_width(), screen.get_height() - TOP_MARGIN - BOTTOM_MARGIN
        ), 2)

        # 保留您原始的绘图逻辑
        top_area = pygame.Rect(0, 0, screen.get_width(), TOP_MARGIN)
        bottom_area = pygame.Rect(0, screen.get_height() - BOTTOM_MARGIN, screen.get_width(), BOTTOM_MARGIN)
        screen.blit(temp_surface, top_area, top_area)
        screen.blit(temp_surface, bottom_area, bottom_area)

    def _handle_collision(self, sprite_group: pygame.sprite.Group, end_group: pygame.sprite.Group):
        if pygame.sprite.groupcollide(sprite_group, end_group, False, False):
            for sprite in sprite_group:
                if sprite == self.player:
                    self.last_key_press_count = self.player.get_key_press_count()
                for endpoint in end_group:
                    if sprite.rect.colliderect(endpoint.rect):
                        start_pos = (sprite.x - sprite.rect.width / 2, sprite.y - TOP_MARGIN - sprite.rect.height / 2)
                        end_pos = (endpoint.rect.centerx, endpoint.rect.centery - TOP_MARGIN)
                        pygame.draw.line(self.drawing_surface, GREEN,
                                         (sprite.last_pos[0], sprite.last_pos[1] - TOP_MARGIN), start_pos, LINEWIDTH)
                        pygame.draw.line(self.drawing_surface, GREEN, start_pos, end_pos, LINEWIDTH)
                        endpoint.image.fill((0, 255, 0))
                        self.endpoint_reached = True
            sprite_group.empty()
            self.player = None

    def run(self, dt: float, stats: object, numbers: List[int], screen: pygame.Surface) -> None:
        if self.player:
            self.player.update(dt)
        for i in range(self.MAX_SPRITES):
            self._handle_collision(self.all_sprites[i], self.end_sprites[i])
        self.draw(screen, stats)

    def clear(self):
        self.drawing_surface.fill(grey)
        for i in range(self.MAX_SPRITES):
            self.all_sprites[i].empty()
            self.end_sprites[i].empty()
        self.player = None
        self.endpoint_reached = False
        if self.player:
            self.player.x = self.display_surface.get_width() // 2
            self.player.y = (self.display_surface.get_height() - 100) // 2
            self.player.rect.center = (self.player.x, self.player.y)
            self.player.angle = 0
            self.player.last_pos = (self.player.x, self.player.y)

    def set_player_speed(self, speed: float) -> None:
        if self.player:
            self.player.base_speed = speed

    def hide_surface(self):
        for i in range(self.MAX_SPRITES):
            self.all_sprites[i].empty()
            self.end_sprites[i].empty()
        self.player = None
        self.drawing_surface.set_alpha(0)

    def show_surface(self):
        self.drawing_surface.set_alpha(255)

    def store_line_points(self, line_number, points):
        self.line_points[line_number] = {'start': points[0], 'end': points[-1]}

    def get_line_endpoints(self, line_number):
        if line_number in self.line_points:
            return self.line_points[line_number]['start'], self.line_points[line_number]['end']
        return None, None

    def get_key_press_count(self):
        if self.player is not None:
            return self.player.get_key_press_count()
        return self.last_key_press_count

    def reset_key_press_count(self):
        if self.player is not None:
            self.player.reset_key_press_count()
        self.last_key_press_count = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
    
    def is_endpoint_reached(self):
        return self.endpoint_reached
    
    def reset_endpoint_reached(self):
        self.endpoint_reached = False