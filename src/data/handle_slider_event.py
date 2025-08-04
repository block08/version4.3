from src.config.config_manager import get_id_file_path
import pygame


def handle_button_event(event, minus_button_rect, plus_button_rect, speed_min, speed_max, speed_value, speed_step, button_states=None):
    """处理+/-按钮事件，支持长按连续调整"""
    mouse_pos = pygame.mouse.get_pos()
    
    # 如果没有传入按钮状态字典，创建一个默认的
    if button_states is None:
        button_states = {'minus_pressed': False, 'plus_pressed': False, 'last_change_time': 0}

    current_time = pygame.time.get_ticks()
    original_speed_value = speed_value
    
    # 检测鼠标按下
    if event and event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # 左键点击
            if minus_button_rect.collidepoint(mouse_pos):
                button_states['minus_pressed'] = True
                button_states['last_change_time'] = current_time
                print(f"[按钮] 减速按钮按下，状态设置为True")
                # 立即执行一次调整
                if speed_value > speed_min:
                    speed_value -= speed_step
                    speed_value = max(speed_min, speed_value)
                    print(f"[按钮] 立即减速到: {speed_value}")
            elif plus_button_rect.collidepoint(mouse_pos):
                button_states['plus_pressed'] = True
                button_states['last_change_time'] = current_time
                print(f"[按钮] 加速按钮按下，状态设置为True")
                # 立即执行一次调整
                if speed_value < speed_max:
                    speed_value += speed_step
                    speed_value = min(speed_max, speed_value)
                    print(f"[按钮] 立即加速到: {speed_value}")

    # 检测鼠标释放
    elif event and event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            if button_states['minus_pressed'] or button_states['plus_pressed']:
                print(f"[按钮] 鼠标释放，停止长按")
            button_states['minus_pressed'] = False
            button_states['plus_pressed'] = False
    
    # 长按连续调整（如果没有事件也会被调用）
    if button_states['minus_pressed'] or button_states['plus_pressed']:
        # 每150毫秒调整一次
        if current_time - button_states['last_change_time'] >= 150:
            if button_states['minus_pressed'] and speed_value > speed_min:
                speed_value -= speed_step
                speed_value = max(speed_min, speed_value)
                button_states['last_change_time'] = current_time
                print(f"[长按] 减速到: {speed_value}")
            elif button_states['plus_pressed'] and speed_value < speed_max:
                speed_value += speed_step
                speed_value = min(speed_max, speed_value)
                button_states['last_change_time'] = current_time
                print(f"[长按] 加速到: {speed_value}")
    
    # 只在速度值改变时才保存到文件
    if speed_value != original_speed_value:
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