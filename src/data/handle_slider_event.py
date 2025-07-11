import pygame


def handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max, speed_value, speed_step):
    """处理+/-按钮事件"""
    mouse_pos = pygame.mouse.get_pos()

    # 检测鼠标按下
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # 左键点击
            if minus_button_rect.collidepoint(mouse_pos):
                # 点击减速按钮
                if speed_value > speed_min:
                    speed_value -= speed_step
                    speed_value = max(speed_min, speed_value)  # 确保不低于最小值
            elif plus_button_rect.collidepoint(mouse_pos):
                # 点击加速按钮
                if speed_value < speed_max:
                    speed_value += speed_step
                    speed_value = min(speed_max, speed_value)  # 确保不超过最大值
    
    # 保存速度值到文件
    with open('scroll_value.txt', 'w') as f:
        f.truncate(0)
        f.write(f'{speed_value}')
    
    return speed_value


def handle_slider_event(event, slider_rect, knob_rect, slider_min, slider_max, slider_value, dragging):
    """处理滑块事件（保留用于兼容性）"""
    mouse_pos = pygame.mouse.get_pos()

    # 检测鼠标按下
    if event.type == pygame.MOUSEBUTTONDOWN:
        if knob_rect.collidepoint(mouse_pos):
            dragging = True

    # 检测鼠标释放
    elif event.type == pygame.MOUSEBUTTONUP:
        dragging = False

    # 处理拖动
    elif event.type == pygame.MOUSEMOTION and dragging:
        # 计算滑块新位置
        rel_x = mouse_pos[0] - slider_rect.x
        # 确保滑块在滑道范围内
        rel_x = max(0, min(rel_x, slider_rect.width))

        # 更新滑块位置
        knob_rect.centerx = slider_rect.x + rel_x

        # 计算对应的值
        slider_value = slider_min + (rel_x / slider_rect.width) * (slider_max - slider_min)
        slider_value = round(slider_value)  # 四舍五入到整数
    with open('scroll_value.txt', 'w') as f:
        f.truncate(0)
        f.write(f'{slider_value}')
    return slider_value, dragging