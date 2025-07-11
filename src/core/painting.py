import pygame

# 初始化 Pygame
pygame.init()

# 设置画布尺寸
width, height = 1720, 880
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("点击左键绘制绿色直线")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 字体设置
font = pygame.font.SysFont(None, 24)

# 角落坐标文字
def draw_corner_coordinates():
    corners = [
        ("(100, 100)", (0, 0)),
        ("(1820, 0)", (width - 60, 0)),
        ("(0, 980)", (0, height - 20)),
        ("(1820, 980)", (width - 60, height - 20)),
    ]
    for text, pos in corners:
        label = font.render(text, True, WHITE)
        screen.blit(label, pos)

# 主循环变量
running = True
points = []  # 用于存储两点的坐标
lines = []   # 存储所有绘制的线段

while running:
    screen.fill(BLACK)  # 黑色背景

    # 重新绘制所有已存储的线段
    for line in lines:
        pygame.draw.line(screen, GREEN, line[0], line[1], 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 左键点击记录点
            if event.button == 1:
                points.append(event.pos)
                # 每次记录两点后绘制一条直线
                if len(points) == 2:
                    # 绘制线段并添加到列表
                    pygame.draw.line(screen, GREEN, points[0], points[1], 2)
                    lines.append((points[0], points[1]))  # 保存线段
                    points = []  # 重置点列表以便下一条线

    # 获取鼠标坐标
    mouse_pos = pygame.mouse.get_pos()

    # 绘制实时坐标
    coord_text = f"({mouse_pos[0]+100}, {mouse_pos[1]+100})"
    coord_label = font.render(coord_text, True, RED)
    screen.blit(coord_label, (mouse_pos[0] + 10, mouse_pos[1] + 10))

    # 绘制四个角的坐标
    draw_corner_coordinates()

    # 更新显示
    pygame.display.flip()

pygame.quit()
