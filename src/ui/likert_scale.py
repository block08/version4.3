import time

import pygame
from typing import Optional, Callable


class LikertScale:
    def __init__(
            self,
            screen: pygame.Surface,  # 传入现有的屏幕对象
            question: str,
            position: tuple = (0, 0),  # 量表在屏幕上的位置
            size: tuple = (1200, 600),  # 量表的大小
            callback: Optional[Callable[[int], None]] = None,
            highlight_user: str = None  # 需要高亮显示的用户名
    ):
        self.screen = screen
        self.position = position
        self.WIDTH, self.HEIGHT = size

        # 颜色定义likert
        self.WHITE = (211, 211, 211)
        self.BLACK = (0, 0, 0)
        self.GRAY = (211, 211, 211)
        self.BLUE = (0, 123, 255)

        # 创建量表的surface
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.surface.fill(self.WHITE)

        # 设置字体
        self.font = pygame.font.SysFont('SimHei', 60)
        self.small_font = pygame.font.SysFont('SimHei', 48)

        # 量表设置
        self.SCALE_LENGTH = int(self.WIDTH * 0.75)
        self.SCALE_Y = self.HEIGHT // 2
        self.SCALE_START_X = (self.WIDTH - self.SCALE_LENGTH) // 2
        self.CIRCLE_RADIUS = 25
        self.SELECTED_CIRCLE_RADIUS = 35

        # 问题文本和回调
        self.question = question
        self.callback = callback
        self.highlight_user = highlight_user

        # 状态变量
        self.selected_score = None
        self.animation_alpha = 0
        self.fade_in = True
        self.key_press_time = None

        # 初始化等级和点位置
        self._init_levels()
        self._init_points()

    def _init_levels(self):
        """初始化等级定义"""
        self.LEVELS = [
            {"score": 1, "label": "非常简单"},
            {"score": 2, "label": "简单"},
            {"score": 3, "label": "有点简单"},
            {"score": 4, "label": "一般"},
            {"score": 5, "label": "有点困难"},
            {"score": 6, "label": "困难"},
            {"score": 7, "label": "非常困难"}
        ]

    def _init_points(self):
        """初始化点的位置"""
        self.points = []
        # 增加间距，留出更多空间分隔各级别
        spacing = self.SCALE_LENGTH // (len(self.LEVELS) - 1)
        # 为了更好的分隔，可以增加一些额外的间距
        extra_spacing = 20
        total_extra = extra_spacing * (len(self.LEVELS) - 1)
        adjusted_spacing = (self.SCALE_LENGTH - total_extra) // (len(self.LEVELS) - 1)
        
        for i in range(len(self.LEVELS)):
            x = self.SCALE_START_X + (i * (adjusted_spacing + extra_spacing))
            self.points.append({
                "x": x,
                "y": self.SCALE_Y,
                "level": self.LEVELS[i]
            })

    def _draw_scale(self):
        """绘制量表"""
        # 绘制横线
        pygame.draw.line(self.surface, self.BLACK,
                         (self.SCALE_START_X, self.SCALE_Y),
                         (self.SCALE_START_X + self.SCALE_LENGTH, self.SCALE_Y), 2)

        # 绘制刻度点和标签
        for point in self.points:
            # 绘制刻度点
            if self.selected_score == point["level"]["score"]:
                pygame.draw.circle(self.surface, self.BLUE,
                                   (point["x"], point["y"]),
                                   self.SELECTED_CIRCLE_RADIUS)
            else:
                pygame.draw.circle(self.surface, self.BLACK,
                                   (point["x"], point["y"]),
                                   self.CIRCLE_RADIUS)

            # 绘制分数
            score_text = self.font.render(str(point["level"]["score"]), True, self.BLACK)
            score_rect = score_text.get_rect(center=(point["x"], point["y"] - 50))
            self.surface.blit(score_text, score_rect)

            # 绘制标签
            label_text = self.small_font.render(point["level"]["label"], True, self.BLACK)
            label_rect = label_text.get_rect(center=(point["x"], point["y"] + 50))
            self.surface.blit(label_text, label_rect)

    def _draw_question(self):
        """绘制问题，支持用户名和按键高亮"""
        # 绿色用于按键高亮
        GREEN_COLOR = (0, 255, 0)
        
        # 处理问题文本，分离需要高亮的部分
        question = self.question
        parts = []
        
        # 先处理数字键1-7的高亮
        import re
        # 匹配 "1 到 7" 或 "1到7" 的模式
        pattern = r'(\d+)-(\d+)'
        match = re.search(pattern, question)
        
        if match:
            # 分割文本
            before_match = question[:match.start()]
            matched_text = question[match.start():match.end()]
            after_match = question[match.end():]
            
            parts = [
                (before_match, self.font, self.BLACK),
                (matched_text, self.font, GREEN_COLOR),
                (after_match, self.font, self.BLACK)
            ]
        else:
            parts = [(question, self.font, self.BLACK)]
        
        # 如果有用户名高亮，进一步处理
        if self.highlight_user and self.highlight_user in question:
            new_parts = []
            bold_font = pygame.font.SysFont('SimHei', 60, bold=True)
            
            for text, font, color in parts:
                if self.highlight_user in text:
                    user_parts = text.split(self.highlight_user)
                    if len(user_parts) >= 2:
                        new_parts.append((user_parts[0], font, color))
                        new_parts.append((self.highlight_user, bold_font, self.BLACK))
                        new_parts.append((user_parts[1], font, color))
                    else:
                        new_parts.append((text, font, color))
                else:
                    new_parts.append((text, font, color))
            parts = new_parts
        
        # 计算总宽度并居中显示
        total_width = sum(font.size(text)[0] for text, font, color in parts if text)
        start_x = (self.WIDTH - total_width) // 2
        y = 50
        
        # 渲染所有部分
        for text, font, color in parts:
            if text:  # 只渲染非空文本
                text_surface = font.render(text, True, color)
                self.surface.blit(text_surface, (start_x, y))
                start_x += text_surface.get_width()

    def _draw_selected_score(self):
        """绘制选中的分数"""
        if self.selected_score is not None:
            feedback_surface = pygame.Surface((self.WIDTH, 60))
            feedback_surface.fill(self.WHITE)
            feedback_surface.set_alpha(self.animation_alpha)

            feedback_text = self.font.render(
                f"您的评分是: {self.selected_score} - " +
                next(level["label"] for level in self.LEVELS
                     if level["score"] == self.selected_score),
                True, self.BLUE)
            feedback_rect = feedback_text.get_rect(
                center=(self.WIDTH // 2, self.HEIGHT - 50))

            self.surface.blit(feedback_surface, (0, self.HEIGHT - 80))
            self.surface.blit(feedback_text, feedback_rect)

    def update(self, mouse_pos, key_pressed=None):
        """
        更新量表状态

        Args:
            mouse_pos: 鼠标位置 (相对于整个窗口)
            key_pressed: 按下的键盘按键

        Returns:
            选中的分数，如果没有选中则返回 None
        """
        # 调整鼠标位置到量表坐标系
        local_mouse_pos = (
            mouse_pos[0] - self.position[0],
            mouse_pos[1] - self.position[1]
        )

        # 检查键盘输入
        if key_pressed:
            if key_pressed == pygame.K_1:
                self.selected_score = 1
            elif key_pressed == pygame.K_2:
                self.selected_score = 2
            elif key_pressed == pygame.K_3:
                self.selected_score = 3
            elif key_pressed == pygame.K_4:
                self.selected_score = 4
            elif key_pressed == pygame.K_5:
                self.selected_score = 5
            elif key_pressed == pygame.K_6:
                self.selected_score = 6
            elif key_pressed == pygame.K_7:
                self.selected_score = 7

            # 如果有有效的键盘输入，记录按键时间
            if self.selected_score is not None:
                self.key_press_time = time.time()
                self.animation_alpha = 0
                self.fade_in = True
                if self.callback:
                    self.callback(self.selected_score)


        # 更新动画
        if self.selected_score is not None and self.fade_in:
            self.animation_alpha += 10
            if self.animation_alpha >= 255:
                self.animation_alpha = 255
                self.fade_in = False

        # 绘制
        self.surface.fill(self.WHITE)
        self._draw_question()
        self._draw_scale()
        self._draw_selected_score()

        # 添加操作提示
        if self.selected_score is None:
            # 显示键盘输入提示
            hint_font = pygame.font.SysFont('SimHei', 32)
            hint_text = hint_font.render("请按下键盘数字键1-7进行选择", True, self.GRAY)
            hint_rect = hint_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT - 20))
            self.surface.blit(hint_text, hint_rect)

        # 绘制到主屏幕
        self.screen.blit(self.surface, self.position)

        # 检查是否满足3秒延时条件
        if self.selected_score is not None and self.key_press_time:
            if time.time() - self.key_press_time >= 2.0:
                return self.selected_score
        
        return None

    def is_selected(self):
        """检查是否已选择分数"""
        return self.selected_score is not None