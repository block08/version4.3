import pygame.font
from src.utils.font_utils import get_font_path

white = (255, 255, 255)
black = (0, 0, 0)
gray = (140, 140 ,140)
light_gray = (100, 100, 100)
green = (0, 255, 0)
back_color = (230, 230, 230)

class Button:
    def __init__(self, setting, screen, text, x, y):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        # 设置按钮的尺寸和其他属性
        self.width, self.height = 200, 50
        self.button_color = back_color
        self.text = text
        self.text_color = black
        self.hover_color = light_gray
        self.current_color = self.button_color
        self.font = pygame.font.Font(get_font_path(), 40)
        # 创建按钮的rect的对象，并使其设置在指定位置
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.clicked = False  # 添加点击状态
        self.last_click_time = 0  # 添加最后点击时间

    def handle_event(self, event, current_time):
        """处理按钮事件，返回是否触发点击"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    if current_time - self.last_click_time > 200:  # 防止快速重复点击
                        self.clicked = True
                        self.last_click_time = current_time
                        return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
        return False

    def check_hover(self, pos):
        """检查鼠标悬停状态"""
        if self.rect.collidepoint(pos):
            if not self.clicked:
                self.current_color = self.hover_color
        else:
            self.current_color = self.button_color

    # 绘制一个用颜色填充的按钮，再绘制文本
    def draw_button(self):
        pygame.draw.rect(self.screen, self.current_color, self.rect, border_radius=8)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

class Button2:
    def __init__(self, setting, screen, text, x, y):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        # 设置按钮的尺寸和其他属性
        self.width, self.height = 350, 50
        self.button_color = gray
        self.text = text
        self.text_color = black
        self.hover_color = light_gray
        self.current_color = self.button_color
        self.font = pygame.font.Font(get_font_path(), 40)
        # 创建按钮的rect的对象，并使其设置在指定位置
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.clicked = False  # 添加点击状态
        self.last_click_time = 0  # 添加最后点击时间

    def handle_event(self, event, current_time):
        """处理按钮事件，返回是否触发点击"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    if current_time - self.last_click_time > 200:  # 防止快速重复点击
                        self.clicked = True
                        self.last_click_time = current_time
                        return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
        return False

    def check_hover(self, pos):
        """检查鼠标悬停状态"""
        if self.rect.collidepoint(pos):
            if not self.clicked:
                self.current_color = self.hover_color
        else:
            self.current_color = self.button_color

    # 绘制一个用颜色填充的按钮，再绘制文本
    def draw_button(self):
        pygame.draw.rect(self.screen, self.current_color, self.rect, border_radius=8)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

class Button3:
    def __init__(self, setting, screen, text, x, y):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        # 设置按钮的尺寸和其他属性
        self.width, self.height = 350, 50
        self.button_color = back_color
        self.text = text
        self.text_color = black
        self.hover_color = light_gray
        self.current_color = self.button_color
        self.font = pygame.font.Font(get_font_path(), 50)
        # 创建按钮的rect的对象，并使其设置在指定位置
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.clicked = False  # 添加点击状态
        self.last_click_time = 0  # 添加最后点击时间

    def handle_event(self, event, current_time):
        """处理按钮事件，返回是否触发点击"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    if current_time - self.last_click_time > 200:  # 防止快速重复点击
                        self.clicked = True
                        self.last_click_time = current_time
                        return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
        return False

    def check_hover(self, pos):
        """检查鼠标悬停状态"""
        if self.rect.collidepoint(pos):
            if not self.clicked:
                self.current_color = self.hover_color
        else:
            self.current_color = self.button_color

    # 绘制一个用颜色填充的按钮，再绘制文本
    def draw_button(self):
        pygame.draw.rect(self.screen, self.current_color, self.rect, border_radius=8)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

class Button4:
    def __init__(self, setting, screen, text, x, y):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        # 设置按钮的尺寸和其他属性
        self.width, self.height = 800, 50
        self.button_color = back_color
        self.text = text
        self.text_color = black
        self.hover_color = light_gray
        self.current_color = self.button_color
        self.font = pygame.font.Font(get_font_path(), 50)
        # 创建按钮的rect的对象，并使其设置在指定位置
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.clicked = False  # 添加点击状态
        self.last_click_time = 0  # 添加最后点击时间

    def handle_event(self, event, current_time):
        """处理按钮事件，返回是否触发点击"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    if current_time - self.last_click_time > 200:  # 防止快速重复点击
                        self.clicked = True
                        self.last_click_time = current_time
                        return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
        return False

    def check_hover(self, pos):
        """检查鼠标悬停状态"""
        if self.rect.collidepoint(pos):
            if not self.clicked:
                self.current_color = self.hover_color
        else:
            self.current_color = self.button_color

    def render_text_with_green_keys(self, text, font, surface, center_pos):
        """渲染带绿色按键高亮的文本"""
        GREEN_COLOR = (0, 0, 255)
        BLACK_COLOR = (0, 0, 0)
        
        # 定义需要高亮的按键
        key_patterns = ['P键', 'Esc键', '空格键', '1', '2', '3', '4', '5', '6', '7']
        
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
        y = center_pos[1] - font.get_height() // 2
        
        # 渲染所有部分
        for part_text, color in parts:
            if part_text:
                text_surface = font.render(part_text, True, color)
                surface.blit(text_surface, (start_x, y))
                start_x += text_surface.get_width()

    # 绘制一个用颜色填充的按钮，再绘制文本
    def draw_button(self):
        pygame.draw.rect(self.screen, self.current_color, self.rect, border_radius=8)
        
        # 如果text为空，不绘制任何文本
        if not self.text:
            return
            
        # 检查是否需要绿色高亮按键
        if any(key in self.text for key in ['P键', 'Esc键', '空格键', '1', '2', '3', '4', '5', '6', '7']):
            self.render_text_with_green_keys(self.text, self.font, self.screen, self.rect.center)
        else:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.screen.blit(text_surface, text_rect)