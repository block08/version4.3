import sys
import pygame
from src.core.level import Level, TOP_MARGIN
import time
import os
import random
import math
from src.config.config_manager import get_id_file_path

# 初始化常量
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LINEWIDTH = 2
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 900
MARGIN = 50  # 边界安全距离
# 实际可绘制区域
DRAW_START_X = MARGIN
DRAW_END_X = WINDOW_WIDTH - MARGIN
DRAW_START_Y = MARGIN
DRAW_END_Y = WINDOW_HEIGHT - MARGIN
DRAW_WIDTH = DRAW_END_X - DRAW_START_X
DRAW_HEIGHT = DRAW_END_Y - DRAW_START_Y


class GameDrawing:
    def __init__(self):
        self.t = 0
        self.timestamp = ''
        self.line_generator = LineGenerator()

    def draw_dashed_lines(self, surface, color, points, width, dash_length=20, gap_length=10):
        """绘制虚线"""
        if len(points) < 2:
            return
            
        total_length = 0
        segment_lengths = []
        
        # 计算每段的长度
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            segment_lengths.append(length)
            total_length += length
        
        current_pos = 0
        draw_dash = True
        
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            if segment_lengths[i] == 0:
                continue
                
            # 在这一段线段上绘制虚线
            segment_start = 0
            while segment_start < segment_lengths[i]:
                if draw_dash:
                    dash_end = min(segment_start + dash_length, segment_lengths[i])
                else:
                    dash_end = min(segment_start + gap_length, segment_lengths[i])
                
                if draw_dash:
                    # 计算虚线段的起点和终点
                    start_ratio = segment_start / segment_lengths[i]
                    end_ratio = dash_end / segment_lengths[i]
                    
                    start_x = x1 + (x2 - x1) * start_ratio
                    start_y = y1 + (y2 - y1) * start_ratio
                    end_x = x1 + (x2 - x1) * end_ratio
                    end_y = y1 + (y2 - y1) * end_ratio
                    
                    pygame.draw.line(surface, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), width)
                
                segment_start = dash_end
                draw_dash = not draw_dash

    def reset_generator(self):
        """重置线条生成器"""
        self.line_generator = LineGenerator()  # 创建新的生成器实例

    def ensure_directory_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_screenshot(self, screen, filepath, gamescore):
        try:
            directory = os.path.dirname(filepath)
            self.ensure_directory_exists(directory)
            pygame.image.save(screen, filepath)
            return True
        except Exception as e:
            print(f"Screenshot save error for score {gamescore}: {str(e)}")
            return False

    def handle_case(self, self_obj, gamescore, case_num, output_dir="output_image", total_pause_time=0):
        """统一处理所有case的通用函数"""
        print(f"=== DEBUG: handle_case called ===")
        print(f"gamescore: {gamescore}")
        print(f"case_num: {case_num}")
        print(f"output_dir: {output_dir}")
        
        self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.t = (pygame.time.get_ticks() - total_pause_time) / 1000

        self.ensure_directory_exists(output_dir)

        # 如果是第一张图（gamescore=0），保存基底post_screenshot-1
        if gamescore == 0:
            post_screenshot = f"./{output_dir}/post_screenshot-1.png"
            self.save_screenshot(self_obj.screen, post_screenshot, -1)

        self_obj.screen.fill('grey')
        line_length = 20  # 十字线的长度
        # 画垂直线
        pygame.draw.line(self_obj.screen, BLACK, (910, 540), (1010, 540), line_length)
        # 画水平线
        pygame.draw.line(self_obj.screen, BLACK, (960, 490), (960, 590), line_length)
        pygame.display.update()
        start_ticks = pygame.time.get_ticks()
        running = True
        countdown_time = 1
        paused = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        # 退出python程序，不捕获异常,不加上这一句也能退出，但是会在中断报错
                        sys.exit()
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            remaining_time = max(0, countdown_time - elapsed_time)
            if remaining_time == 0:
                running = False
                self_obj.screen.fill('grey')
        # 然后再清理和设置新的状态
        try:
            # 清理前一个状态
            self_obj.level.clear()

            # 生成新的曲线 - 使用case_num确保不同序号使用不同生成器
            # 根据输出目录确定模式偏移
            mode_offset = 0  # 默认subA
            if "subAB" in output_dir:
                mode_offset = 1
            elif "subAC" in output_dir:
                mode_offset = 2
            
            random.seed(case_num * 1000 + gamescore)  # 使用固定种子
            points, line_type = self.line_generator.generate_random_line_advanced(case_num, mode_offset)
            random.seed()  # 恢复随机种子

            # 绘制新曲线（实线）
            if len(points) > 1:
                pygame.draw.lines(self_obj.level.drawing_surface, BLACK, False, points, LINEWIDTH)

            # 存储线的端点
            self_obj.level.store_line_points(case_num, [points[0], points[-1]])

            # 更新屏幕显示新曲线
            self_obj.screen.blit(self_obj.level.drawing_surface, (0, TOP_MARGIN))
            pygame.display.flip()

            # 保存新曲线的截图
            pre_screenshot = f"./{output_dir}/pre_screenshot{gamescore}.png"
            self.save_screenshot(self_obj.screen, pre_screenshot, gamescore)

            # 设置新状态的起点和终点
            if points:
                start_point = points[0]
                end_point = points[-1]
                setup_method_name = f"setup{case_num - 1}"
                setup_endpoint_method_name = f"setup_endpoint{case_num - 1}"
                print(f"调用方法: {setup_method_name}, 起点: {start_point}")
                print(f"调用方法: {setup_endpoint_method_name}, 终点: {end_point}")
                
                setup_func = getattr(self_obj.level, setup_method_name)
                setup_endpoint_func = getattr(self_obj.level, setup_endpoint_method_name)
                setup_func(start_point[0], start_point[1])
                setup_endpoint_func(end_point[0], end_point[1])
                print(f"setup函数调用完成")
        except Exception as e:
            print(f"Error in handle_case for score {gamescore}, case {case_num}: {str(e)}")

        return self.t, self.timestamp

    def update_current_timestamp(self, total_pause_time=0):
        """更新当前时间戳，用于处理最小化等暂停事件后的时间校正"""
        self.t = (pygame.time.get_ticks() - total_pause_time) / 1000
        return self.t

    def random_painting(self, number, self_obj, gamescore, total_pause_time=0):
        try:
            print(f"=== DEBUG: random_painting called ===")
            print(f"number (case_num): {number}")
            print(f"gamescore: {gamescore}")
            
            if gamescore == 22:  # 被试B和被试A+B开始时
                self.reset_generator()
            with open(get_id_file_path(), "r") as file:
                id = file.read()
            if 0 <= gamescore <= 8:
                print(f"执行被试A分支, 调用handle_case(gamescore={gamescore}, case_num={number})")
                return self.handle_case(self_obj, gamescore, number,
                                        f"./Behavioral_data/{id}/subA/output_image", total_pause_time)
            elif 11 <= gamescore <= 18:
                adjusted_score = gamescore - 11
                print(f"执行被试B分支, 调用handle_case(gamescore={adjusted_score}, case_num={number})")
                return self.handle_case(self_obj, adjusted_score, number,
                                        f"./Behavioral_data/{id}/subAB/output_image", total_pause_time)
            elif 23 <= gamescore <= 30:
                adjusted_score = gamescore - 23
                print(f"执行被试AC分支, 调用handle_case(gamescore={adjusted_score}, case_num={number})")
                return self.handle_case(self_obj, adjusted_score, number,
                                        f"./Behavioral_data/{id}/subAC/output_image", total_pause_time)
        except Exception as e:
            print(f"Error in random_painting for score {gamescore}, number {number}: {str(e)}")
            return self.t, self.timestamp


class LineGenerator:
    def __init__(self):
        # 保持原有的初始化代码不变
        self.WINDOW_WIDTH = 1800
        self.WINDOW_HEIGHT = 900
        self.DRAW_START_X = MARGIN
        self.DRAW_END_X = self.WINDOW_WIDTH - MARGIN
        self.DRAW_START_Y = MARGIN
        self.DRAW_END_Y = self.WINDOW_HEIGHT - MARGIN
        self.DRAW_WIDTH = self.DRAW_END_X - self.DRAW_START_X
        self.DRAW_HEIGHT = self.DRAW_END_Y - self.DRAW_START_Y

        # 添加验证方法
        self.max_attempts = 8  # 最大重试次数
        self.min_endpoint_distance = 200  # 起点和终点之间的最小距离

        # 所有可用生成器列表
        self.all_generators = [
            (self.generate_wave, "波浪线"),
            (self.generate_zigzag, "锯齿线"),
            (self.generate_sine_wave, "正弦波"),
            (self.generate_arch, "拱形"),
            (self.generate_spiral_open, "开放螺旋"),
            (self.generate_mountain, "山形线"),
            (self.generate_stair, "阶梯线"),
            (self.generate_heartbeat, "心电图线"),
            (self.generate_step_wave, "方波"),
            (self.generate_sawtooth, "锯齿波"),
            (self.generate_star_partial, "部分星形"),
            (self.generate_helix, "螺旋状曲线"),
            # 新增的曲线类型
            (self.generate_s_curve, "S形曲线"),
            (self.generate_double_wave, "双重波浪")
        ]
        
        # 为本次实验随机选择8个不重复的生成器
        # 使用实验ID作为种子，确保同一实验的三个模式（subA, subAB, subAC）使用相同的8张图
        selection_seed = self._get_experiment_seed()
        temp_random_state = random.getstate()
        random.seed(selection_seed)
        
        # 从14个生成器中随机选择8个
        selected_indices = random.sample(range(len(self.all_generators)), 8)
        self.available_generators = [self.all_generators[i] for i in selected_indices]
        
        print(f"实验会话选择的8个生成器（种子：{selection_seed}）:")
        for i, (func, name) in enumerate(self.available_generators):
            print(f"  生成器{i}: {name}")
        
        random.setstate(temp_random_state)  # 恢复随机状态
    
    def _get_experiment_seed(self):
        """获取实验种子，确保同一实验会话的一致性"""
        try:
            # 尝试读取实验ID作为种子基础
            with open(get_id_file_path(), "r") as file:
                experiment_id = file.read().strip()
                # 将实验ID转换为数字种子
                seed = hash(experiment_id) % 100000
                return abs(seed)  # 确保是正数
        except (FileNotFoundError, ValueError):
            # 如果无法读取实验ID，使用时间戳作为备选
            import time
            return int(time.time()) % 10000

    def validate_points(self, points, name):
        """验证生成的点列表是否有效，包括起点终点距离检查"""
        if not points or len(points) < 3:
            print(f"警告: {name} 生成的点数量不足，只有 {len(points) if points else 0} 个点")
            return False

        # 检查起点和终点距离
        start_point = points[0]
        end_point = points[-1]
        distance = ((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2) ** 0.5

        if distance < self.min_endpoint_distance:
            print(f"警告: {name} 起点和终点距离太近: {distance:.2f} < {self.min_endpoint_distance}")
            return False

        # 计算线段的总长度
        total_length = 0
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            segment_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            total_length += segment_length

        # 验证线段总长度是否符合预期
        min_required_length = 400  # 增加最小线段长度要求
        if total_length < min_required_length:
            print(f"警告: {name} 生成的线段总长度不足，只有 {total_length:.2f}")
            return False

        for point in points:
            if not isinstance(point, tuple) or len(point) != 2:
                print(f"警告: {name} 生成的点格式不正确")
                return False

            x, y = point
            if not (self.DRAW_START_X <= x <= self.DRAW_END_X and
                    self.DRAW_START_Y <= y <= self.DRAW_END_Y):
                print(f"警告: {name} 生成的点超出绘制范围: ({x}, {y})")
                return False
        return True

    def flip_horizontal(self, points):
        """左右反转曲线点"""
        if not points:
            return points
        
        center_x = (self.DRAW_START_X + self.DRAW_END_X) / 2
        flipped_points = []
        
        for x, y in points:
            # 计算点到中心线的距离，然后反转
            new_x = center_x - (x - center_x)
            flipped_points.append(self.constrain_point(new_x, y))
        
        return flipped_points

    def flip_vertical(self, points):
        """上下反转曲线点"""
        if not points:
            return points
        
        center_y = (self.DRAW_START_Y + self.DRAW_END_Y) / 2
        flipped_points = []
        
        for x, y in points:
            # 计算点到中心线的距离，然后反转
            new_y = center_y - (y - center_y)
            flipped_points.append(self.constrain_point(x, new_y))
        
        return flipped_points

    def swap_endpoints(self, points):
        """交换起点和终点"""
        if not points or len(points) < 2:
            return points
        
        # 反转整个点列表，实现起点终点互换
        return list(reversed(points))





    def generate_random_line_advanced(self, case_num=None, mode_offset=0):
        """生成随机线条，支持指定case_num确保不重复的生成器选择
        
        Args:
            case_num: 图片编号 (1-8)
            mode_offset: 模式偏移，用于不同模式使用不同顺序
                        0=subA, 1=subAB, 2=subAC
        """
        if not self.available_generators:
            print("重置所有可用线型")
            self.__init__()

        # 如果指定了case_num，使用固定的生成器选择策略确保不重复
        if case_num is not None:
            # 应用模式偏移，让不同模式使用不同的图片顺序
            # 但仍然使用相同的8个生成器
            adjusted_case = ((case_num - 1) + mode_offset) % len(self.available_generators)
            generator_index = adjusted_case
            generator, name = self.available_generators[generator_index]
            
            mode_names = {0: "subA", 1: "subAB", 2: "subAC"}
            mode_name = mode_names.get(mode_offset, f"mode{mode_offset}")
            print(f"{mode_name} Case {case_num}: 使用生成器 {generator_index} - {name}")
        else:
            # 原有的随机选择逻辑（用于向后兼容）
            generator_index = random.randrange(len(self.available_generators))
            generator, name = self.available_generators[generator_index]

        for attempt in range(self.max_attempts):
            try:
                points = generator()

                # 验证生成的原始点
                if not self.validate_points(points, name):
                    print(f"第 {attempt + 1} 次尝试生成 {name} 失败，重试...")
                    continue

                # 基于case_num应用固定变换（确保相同case_num总是得到相同结果）
                transform_applied = ""
                if case_num is not None:
                    # 使用case_num决定变换类型，确保可重现性
                    transform_seed = case_num * 123  # 固定种子
                    temp_random_state = random.getstate()
                    random.seed(transform_seed)
                    
                    if random.random() < 0.5:  # 50%概率应用变换
                        transform_type = random.choice(['horizontal', 'vertical', 'swap'])
                        
                        if transform_type == 'horizontal':
                            points = self.flip_horizontal(points)
                            transform_applied = " (左右反转)"
                        elif transform_type == 'vertical':
                            points = self.flip_vertical(points)
                            transform_applied = " (上下反转)"
                        elif transform_type == 'swap':
                            points = self.swap_endpoints(points)
                            transform_applied = " (起点终点互换)"
                    
                    random.setstate(temp_random_state)  # 恢复随机状态
                else:
                    # 原有的随机变换逻辑
                    if random.random() < 0.4:
                        transform_type = random.choice(['horizontal', 'vertical', 'swap'])
                        
                        if transform_type == 'horizontal':
                            points = self.flip_horizontal(points)
                            transform_applied = " (左右反转)"
                        elif transform_type == 'vertical':
                            points = self.flip_vertical(points)
                            transform_applied = " (上下反转)"
                        elif transform_type == 'swap':
                            points = self.swap_endpoints(points)
                            transform_applied = " (起点终点互换)"
                
                # 变换后再次验证点的有效性
                if not self.validate_points(points, name + transform_applied):
                    print(f"第 {attempt + 1} 次尝试生成 {name}{transform_applied} 变换后验证失败，重试...")
                    continue

                return points, name + transform_applied

            except Exception as e:
                print(f"生成 {name} 时发生错误: {str(e)}")

        # 如果指定了case_num但生成失败，尝试下一个生成器
        if case_num is not None:
            print(f"Case {case_num}: 无法生成 {name}，尝试下一个生成器")
            backup_index = (generator_index + 1) % len(self.available_generators)
            backup_generator, backup_name = self.available_generators[backup_index]
            print(f"Case {case_num}: 备用生成器 {backup_index} - {backup_name}")
            
            for attempt in range(self.max_attempts):
                try:
                    points = backup_generator()
                    if self.validate_points(points, backup_name):
                        return points, backup_name
                except Exception as e:
                    print(f"备用生成器 {backup_name} 错误: {str(e)}")
        
        # 移除后备方案，直接重新选择一个不同的生成器
        print(f"无法生成 {name}，尝试其他线型")
        if self.available_generators:  # 如果还有其他可用生成器
            return self.generate_random_line_advanced(case_num)
        else:  # 如果没有其他可用生成器，重置并再试一次
            self.__init__()
            return self.generate_random_line_advanced(case_num)

    def constrain_point(self, x, y):
        """确保点在绘制范围内"""
        x = max(self.DRAW_START_X, min(self.DRAW_END_X, x))
        y = max(self.DRAW_START_Y, min(self.DRAW_END_Y, y))
        return (int(x), int(y))

    def generate_random_point(self):
        return (random.randint(self.DRAW_START_X, self.DRAW_END_X),
                random.randint(self.DRAW_START_Y, self.DRAW_END_Y))

    # 保留的原有曲线生成函数
    def generate_wave(self):
        """生成波浪线"""
        points = []
        num_waves = random.randint(2, 4)
        wave_width = DRAW_WIDTH // num_waves
        amplitude = min(150, (DRAW_HEIGHT // 2) - MARGIN)
        start_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for x in range(DRAW_START_X, DRAW_END_X, 20):
            t = (x - DRAW_START_X) * 2 * math.pi / wave_width
            y = start_y + amplitude * math.sin(t)
            points.append(self.constrain_point(x, y))
        return points

    def generate_zigzag(self):
        """生成锯齿线"""
        points = []
        num_points = random.randint(5, 8)
        x_step = DRAW_WIDTH // (num_points - 1)
        y_range = min(400, DRAW_HEIGHT - 2 * MARGIN)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for i in range(num_points):
            x = DRAW_START_X + i * x_step
            if i % 2 == 0:
                y = center_y - y_range // 2
            else:
                y = center_y + y_range // 2
            points.append(self.constrain_point(x, y))
        return points

    def generate_sine_wave(self):
        """生成正弦波"""
        points = []
        frequency = random.uniform(1, 3)
        amplitude = min(200, (DRAW_HEIGHT // 2) - MARGIN)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for x in range(DRAW_START_X, DRAW_END_X, 15):
            t = (x - DRAW_START_X) * frequency * math.pi / DRAW_WIDTH
            y = center_y + amplitude * math.sin(t)
            points.append(self.constrain_point(x, y))
        return points

    def generate_arch(self):
        """生成拱形曲线"""
        points = []
        height = min(400, DRAW_HEIGHT - 2 * MARGIN)
        base_y = DRAW_END_Y - MARGIN

        for x in range(DRAW_START_X, DRAW_END_X, 20):
            t = (x - DRAW_START_X) / DRAW_WIDTH
            y = base_y - height * (4 * t * (1 - t))
            points.append(self.constrain_point(x, y))
        return points

    def generate_spiral_open(self):
        """生成开放螺旋"""
        points = []
        center_x = (DRAW_START_X + DRAW_END_X) // 2
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        # 计算最大安全半径
        max_radius = min(
            center_x - DRAW_START_X,
            DRAW_END_X - center_x,
            center_y - DRAW_START_Y,
            DRAW_END_Y - center_y
        ) - MARGIN

        a = random.randint(35, 45)
        max_angle = random.randint(540, 720)

        for angle in range(0, max_angle, 5):
            t = math.radians(angle)
            r = min(a * t, max_radius)
            x = center_x + r * math.cos(t)
            y = center_y + r * math.sin(t)
            points.append(self.constrain_point(x, y))
            # 如果达到最大半径，停止生成
            if r >= max_radius:
                break
        return points

    def generate_mountain(self):
        """生成山形线"""
        points = []
        num_peaks = random.randint(3, 5)
        width = DRAW_WIDTH // num_peaks
        base_height = DRAW_END_Y - MARGIN * 2

        for i in range(num_peaks + 1):
            x = DRAW_START_X + i * width
            if i % 2 == 0:
                y = base_height
            else:
                y = base_height - random.randint(200, min(400, DRAW_HEIGHT - 2 * MARGIN))
            points.append(self.constrain_point(x, y))

            # 添加中间点使山形更自然
            if i < num_peaks:
                mid_x = x + width // 2
                mid_y = base_height - random.randint(100, min(300, DRAW_HEIGHT - 2 * MARGIN))
                points.append(self.constrain_point(mid_x, mid_y))
        return points

    def generate_stair(self):
        """生成阶梯线"""
        points = []
        num_steps = random.randint(4, 7)
        step_width = DRAW_WIDTH // num_steps
        step_height = DRAW_HEIGHT // (num_steps + 1)

        start_y = random.randint(DRAW_START_Y + step_height, DRAW_END_Y - step_height * num_steps)

        for i in range(num_steps + 1):
            x = DRAW_START_X + i * step_width
            y = start_y + i * step_height
            points.append(self.constrain_point(x, y))
            if i < num_steps:  # 添加水平线段
                points.append(self.constrain_point(x + step_width, y))
        return points

    def generate_heartbeat(self):
        """生成心电图样式线"""
        points = []
        num_beats = random.randint(2, 4)
        segment_width = DRAW_WIDTH // num_beats
        base_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for i in range(num_beats):
            x_start = DRAW_START_X + i * segment_width

            # 基线
            points.append(self.constrain_point(x_start, base_y))

            # 上升
            spike_height = random.randint(100, 200)
            x_spike = x_start + segment_width // 4
            points.append(self.constrain_point(x_spike, base_y - spike_height))

            # 下降
            x_dip = x_start + segment_width // 3
            points.append(self.constrain_point(x_dip, base_y + spike_height // 2))

            # 恢复
            x_recover = x_start + segment_width // 2
            points.append(self.constrain_point(x_recover, base_y))

            # 连接到下一段
            if i < num_beats - 1:
                points.append(self.constrain_point(x_start + segment_width, base_y))
        return points

    def generate_polynomial(self):
        """生成多项式曲线"""
        points = []
        a = random.uniform(-0.000003, 0.000003)
        b = random.uniform(-0.03, 0.03)
        c = random.uniform(-30, 30)
        d = (DRAW_START_Y + DRAW_END_Y) // 2

        for x in range(DRAW_START_X, DRAW_END_X, 20):
            rel_x = x - (DRAW_START_X + DRAW_END_X) // 2
            y = a * rel_x ** 3 + b * rel_x ** 2 + c * rel_x + d
            points.append(self.constrain_point(x, y))
        return points

    def generate_parabola(self):
        """生成抛物线"""
        points = []
        a = random.uniform(-0.002, 0.002)
        h = (DRAW_START_X + DRAW_END_X) // 2
        k = random.randint(DRAW_START_Y + 100, DRAW_END_Y - 100)

        for x in range(DRAW_START_X, DRAW_END_X, 20):
            y = a * (x - h) ** 2 + k
            points.append(self.constrain_point(x, y))
        return points

    def generate_step_wave(self):
        """生成方波"""
        points = []
        num_steps = random.randint(3, 5)
        step_width = DRAW_WIDTH // num_steps
        high_y = (DRAW_START_Y + DRAW_END_Y) // 2 - 150
        low_y = (DRAW_START_Y + DRAW_END_Y) // 2 + 150

        for i in range(num_steps + 1):
            x = DRAW_START_X + i * step_width
            y = high_y if i % 2 == 0 else low_y
            points.append(self.constrain_point(x, y))
            if i < num_steps:  # 添加垂直线段
                points.append(self.constrain_point(x, low_y if i % 2 == 0 else high_y))
        return points

    def generate_sawtooth(self):
        """生成锯齿波"""
        points = []
        num_teeth = random.randint(4, 6)
        tooth_width = DRAW_WIDTH // num_teeth
        tooth_height = 300
        base_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for i in range(num_teeth + 1):
            x = DRAW_START_X + i * tooth_width
            if i % 2 == 0:
                points.append(self.constrain_point(x, base_y - tooth_height // 2))
            else:
                points.append(self.constrain_point(x, base_y + tooth_height // 2))
        return points

    def generate_star_partial(self):
        """生成部分星形（非闭合）"""
        points = []
        try:
            # 星形的中心和大小
            center_x = (DRAW_START_X + DRAW_END_X) // 2
            center_y = (DRAW_START_Y + DRAW_END_Y) // 2
            outer_radius = min(DRAW_WIDTH, DRAW_HEIGHT) // 3
            inner_radius = outer_radius // 2

            # 星形的点数（奇数更好看）
            num_points = random.choice([5, 6])

            # 随机选择起始角度和绘制角度范围（小于360度以确保非闭合）
            start_angle = random.uniform(0, 2 * math.pi)
            sweep_angle = random.uniform(math.pi, 1.5 * math.pi)  # 介于180-270度之间

            # 根据起始角度和扫描角度计算实际点数
            actual_points = max(3, int(num_points * sweep_angle / (2 * math.pi)))
            angle_step = sweep_angle / (actual_points * 2)

            # 生成部分星形的点
            for i in range(actual_points * 2 + 1):
                angle = start_angle + i * angle_step
                # 交替使用内半径和外半径
                if i % 2 == 0:
                    radius = outer_radius
                else:
                    radius = inner_radius

                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append(self.constrain_point(x, y))

        except Exception as e:
            print(f"生成部分星形时出错: {str(e)}")
        return points

    def generate_helix(self):
        """生成螺旋状曲线（像DNA结构）"""
        points = []
        try:
            # 螺旋的主要参数
            amplitude = random.randint(DRAW_HEIGHT // 10, DRAW_HEIGHT // 4)
            frequency = random.uniform(3, 6)  # 完成的圈数
            stretch = random.uniform(0.8, 1.2)  # 拉伸因子

            # 确定螺旋的起点和长度
            start_x = DRAW_START_X + DRAW_WIDTH // 10
            end_x = DRAW_END_X - DRAW_WIDTH // 10
            center_y = (DRAW_START_Y + DRAW_END_Y) // 2

            # 生成螺旋的点
            step = max(5, (end_x - start_x) // 100)  # 确保有足够多的点但不过多
            for x in range(start_x, end_x, step):
                progress = (x - start_x) / (end_x - start_x)
                phase = progress * frequency * 2 * math.pi

                # 使用正弦函数计算y值，并逐渐减小振幅以创建收敛效果
                y = center_y + amplitude * math.sin(phase) * (1 - progress * 0.5)

                # 使用余弦函数添加一些变化和拉伸
                x_offset = amplitude * 0.1 * math.cos(phase * stretch)

                points.append(self.constrain_point(x + x_offset, y))

        except Exception as e:
            print(f"生成螺旋状曲线时出错: {str(e)}")
        return points

    # 新增的曲线生成函数
    def generate_s_curve(self):
        """生成S形曲线"""
        points = []
        amplitude = min(300, DRAW_HEIGHT // 3)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for x in range(DRAW_START_X, DRAW_END_X, 15):
            t = (x - DRAW_START_X) / DRAW_WIDTH * 2 - 1  # 范围[-1, 1]
            # 使用tanh函数创建S形
            y = center_y + amplitude * math.tanh(3 * t)
            points.append(self.constrain_point(x, y))
        return points

    def generate_double_wave(self):
        """生成双重波浪"""
        points = []
        amplitude1 = min(150, DRAW_HEIGHT // 4)
        amplitude2 = min(100, DRAW_HEIGHT // 6)
        frequency1 = random.uniform(2, 4)
        frequency2 = random.uniform(5, 8)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for x in range(DRAW_START_X, DRAW_END_X, 10):
            t = (x - DRAW_START_X) * 2 * math.pi / DRAW_WIDTH
            y1 = amplitude1 * math.sin(frequency1 * t)
            y2 = amplitude2 * math.sin(frequency2 * t)
            y = center_y + y1 + y2
            points.append(self.constrain_point(x, y))
        return points

    def generate_zigzag_smooth(self):
        """生成平滑锯齿"""
        points = []
        num_peaks = random.randint(4, 6)
        peak_width = DRAW_WIDTH // num_peaks
        amplitude = min(250, DRAW_HEIGHT // 3)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for i in range(num_peaks + 1):
            base_x = DRAW_START_X + i * peak_width

            # 为每个峰添加多个点来实现平滑过渡
            for j in range(0, peak_width, 20):
                x = base_x + j
                if x > DRAW_END_X:
                    break

                # 使用正弦函数的一部分来创建平滑的峰
                t = j / peak_width * math.pi
                y = center_y + amplitude * math.sin(t) * (1 if i % 2 == 0 else -1)
                points.append(self.constrain_point(x, y))
        return points

    def generate_circular_arc(self):
        """生成圆弧"""
        points = []
        center_x = (DRAW_START_X + DRAW_END_X) // 2
        center_y = random.randint(DRAW_START_Y - 300, DRAW_END_Y + 300)
        radius = random.randint(400, 700)
        start_angle = random.uniform(0, math.pi)
        end_angle = start_angle + random.uniform(math.pi / 2, math.pi)

        angle_step = (end_angle - start_angle) / 50
        for i in range(51):
            angle = start_angle + i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(self.constrain_point(x, y))
        return points

    def generate_exponential(self):
        """生成指数曲线"""
        points = []
        center_x = (DRAW_START_X + DRAW_END_X) // 2
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2
        scale = random.uniform(0.003, 0.008)

        for x in range(DRAW_START_X, DRAW_END_X, 15):
            rel_x = x - center_x
            y = center_y + 200 * (math.exp(scale * rel_x) - 1)
            points.append(self.constrain_point(x, y))
        return points


    def generate_diamond(self):
        """生成菱形"""
        points = []
        center_x = (DRAW_START_X + DRAW_END_X) // 2
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2
        width = min(600, DRAW_WIDTH // 2)
        height = min(400, DRAW_HEIGHT // 2)

        # 只绘制菱形的一部分（比如3/4）
        angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        partial_end = int(len(angles) * 0.75)

        for i in range(partial_end * 20):
            t = i / (partial_end * 20) * partial_end
            angle_idx = int(t)
            if angle_idx >= partial_end:
                break

            # 在相邻角度之间插值
            if angle_idx < len(angles) - 1:
                angle = angles[angle_idx]
            else:
                angle = angles[angle_idx]

            x = center_x + width / 2 * math.cos(angle)
            y = center_y + height / 2 * math.sin(angle)
            points.append(self.constrain_point(x, y))
        return points

    def generate_triangle_wave(self):
        """生成三角波"""
        points = []
        num_triangles = random.randint(3, 5)
        triangle_width = DRAW_WIDTH // num_triangles
        amplitude = min(200, DRAW_HEIGHT // 3)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for i in range(num_triangles):
            x_start = DRAW_START_X + i * triangle_width
            x_mid = x_start + triangle_width // 2
            x_end = x_start + triangle_width

            # 上升部分
            for x in range(x_start, x_mid, 10):
                progress = (x - x_start) / (triangle_width // 2)
                y = center_y + amplitude * (2 * progress - 1)
                points.append(self.constrain_point(x, y))

            # 下降部分
            for x in range(x_mid, x_end, 10):
                progress = (x - x_mid) / (triangle_width // 2)
                y = center_y + amplitude * (1 - 2 * progress)
                points.append(self.constrain_point(x, y))
        return points

    def generate_pulse_wave(self):
        """生成脉冲波"""
        points = []
        num_pulses = random.randint(4, 6)
        pulse_width = DRAW_WIDTH // num_pulses
        amplitude = min(250, DRAW_HEIGHT // 3)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2
        duty_cycle = random.uniform(0.2, 0.4)  # 脉冲占空比

        for i in range(num_pulses):
            x_start = DRAW_START_X + i * pulse_width
            x_high_end = x_start + int(pulse_width * duty_cycle)
            x_end = x_start + pulse_width

            # 低电平
            points.append(self.constrain_point(x_start, center_y))

            # 上升沿
            points.append(self.constrain_point(x_start, center_y + amplitude))

            # 高电平
            points.append(self.constrain_point(x_high_end, center_y + amplitude))

            # 下降沿
            points.append(self.constrain_point(x_high_end, center_y))

            # 低电平持续
            if i < num_pulses - 1:
                points.append(self.constrain_point(x_end, center_y))
        return points

    def generate_crescendo(self):
        """生成渐强曲线（振幅逐渐增加）"""
        points = []
        frequency = random.uniform(3, 5)
        max_amplitude = min(300, DRAW_HEIGHT // 3)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for x in range(DRAW_START_X, DRAW_END_X, 12):
            progress = (x - DRAW_START_X) / DRAW_WIDTH
            amplitude = max_amplitude * progress  # 振幅逐渐增加

            t = progress * frequency * 2 * math.pi
            y = center_y + amplitude * math.sin(t)
            points.append(self.constrain_point(x, y))
        return points

    def generate_fibonacci_spiral(self):
        """生成斐波那契螺旋的一部分"""
        points = []
        center_x = (DRAW_START_X + DRAW_END_X) // 2
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        # 斐波那契数列的前几项
        fib = [1, 1, 2, 3, 5, 8, 13, 21]
        scale = 15

        angle = 0
        for i in range(len(fib) - 1):
            radius = fib[i] * scale
            quarter_circle_steps = 25

            for step in range(quarter_circle_steps):
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append(self.constrain_point(x, y))
                angle += math.pi / (2 * quarter_circle_steps)

            if len(points) > 100:  # 限制点数
                break
        return points

    def generate_flower_petals(self):
        """生成花瓣形状"""
        points = []
        center_x = (DRAW_START_X + DRAW_END_X) // 2
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2
        base_radius = min(200, min(DRAW_WIDTH, DRAW_HEIGHT) // 4)

        num_petals = random.randint(5, 8)
        max_angle = random.uniform(math.pi, 1.8 * math.pi)  # 不完整的花

        angle_step = max_angle / 100
        for i in range(101):
            angle = i * angle_step
            # 花瓣效果：半径随角度变化
            petal_effect = 1 + 0.5 * math.sin(num_petals * angle)
            radius = base_radius * petal_effect

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(self.constrain_point(x, y))
        return points

    def generate_oscillating_decay(self):
        """生成振荡衰减曲线"""
        points = []
        frequency = random.uniform(4, 7)
        initial_amplitude = min(300, DRAW_HEIGHT // 3)
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2
        decay_rate = random.uniform(2, 4)

        for x in range(DRAW_START_X, DRAW_END_X, 10):
            progress = (x - DRAW_START_X) / DRAW_WIDTH
            amplitude = initial_amplitude * math.exp(-decay_rate * progress)

            t = progress * frequency * 2 * math.pi
            y = center_y + amplitude * math.sin(t)
            points.append(self.constrain_point(x, y))
        return points

    def generate_multi_frequency_wave(self):
        """生成多频率叠加波"""
        points = []
        frequencies = [random.uniform(1, 3), random.uniform(4, 6), random.uniform(7, 10)]
        amplitudes = [100, 60, 30]
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2

        for x in range(DRAW_START_X, DRAW_END_X, 8):
            progress = (x - DRAW_START_X) / DRAW_WIDTH
            y_total = 0

            for freq, amp in zip(frequencies, amplitudes):
                t = progress * freq * 2 * math.pi
                y_total += amp * math.sin(t)

            y = center_y + y_total
            points.append(self.constrain_point(x, y))
        return points

    def generate_parametric_curve(self):
        """生成参数曲线"""
        points = []
        center_x = (DRAW_START_X + DRAW_END_X) // 2
        center_y = (DRAW_START_Y + DRAW_END_Y) // 2
        scale = min(250, min(DRAW_WIDTH, DRAW_HEIGHT) // 4)

        a = random.uniform(2, 4)
        b = random.uniform(3, 5)

        max_t = random.uniform(math.pi, 2 * math.pi)
        t_step = max_t / 80

        for i in range(81):
            t = i * t_step
            x = center_x + scale * math.sin(a * t)
            y = center_y + scale * math.sin(b * t)
            points.append(self.constrain_point(x, y))
        return points

    def generate_random_walk(self):
        """生成随机游走曲线"""
        points = []
        x = DRAW_START_X
        y = (DRAW_START_Y + DRAW_END_Y) // 2
        step_size = 15

        # 添加一些趋势，避免完全随机
        trend_x = random.uniform(-2, 2)
        trend_y = random.uniform(-1, 1)

        while x < DRAW_END_X:
            points.append(self.constrain_point(x, y))

            # 随机步进，但加上趋势
            dx = step_size + random.uniform(-5, 5) + trend_x
            dy = random.uniform(-30, 30) + trend_y

            x += dx
            y += dy

            # 确保y值不会偏离太远
            y = max(DRAW_START_Y + 100, min(DRAW_END_Y - 100, y))

        # 确保有足够的点数
        if len(points) < 20:
            return self.generate_sine_wave()  # 回退到简单曲线

        return points


def draw_dashed_lines_static(surface, color, points, width, dash_length=20, gap_length=10):
    """静态方法：绘制虚线"""
    if len(points) < 2:
        return
        
    total_length = 0
    segment_lengths = []
    
    # 计算每段的长度
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        segment_lengths.append(length)
        total_length += length
    
    current_pos = 0
    draw_dash = True
    
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        
        if segment_lengths[i] == 0:
            continue
            
        # 在这一段线段上绘制虚线
        segment_start = 0
        while segment_start < segment_lengths[i]:
            if draw_dash:
                dash_end = min(segment_start + dash_length, segment_lengths[i])
            else:
                dash_end = min(segment_start + gap_length, segment_lengths[i])
            
            if draw_dash:
                # 计算虚线段的起点和终点
                start_ratio = segment_start / segment_lengths[i]
                end_ratio = dash_end / segment_lengths[i]
                
                start_x = x1 + (x2 - x1) * start_ratio
                start_y = y1 + (y2 - y1) * start_ratio
                end_x = x1 + (x2 - x1) * end_ratio
                end_y = y1 + (y2 - y1) * end_ratio
                
                pygame.draw.line(surface, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), width)
            
            segment_start = dash_end
            draw_dash = not draw_dash


def test_curve_generator():
    """测试曲线生成器，直观显示各种曲线类型"""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("曲线生成器测试")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('simhei', 24)  # 使用中文字体

    # 创建绘图表面
    drawing_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    drawing_surface.fill('grey')

    # 创建LineGenerator实例
    line_generator = LineGenerator()

    # 存储所有曲线类型的名称和对应的生成函数
    all_curves = [(func, name) for func, name in line_generator.available_generators]
    current_curve_index = 0

    # 生成初始曲线
    current_curve_func, current_curve_name = all_curves[current_curve_index]
    points = current_curve_func()

    # 游戏主循环
    running = True
    auto_change = False
    last_change_time = pygame.time.get_ticks()
    change_interval = 2000  # 自动切换间隔(毫秒)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    # 切换到下一条曲线
                    current_curve_index = (current_curve_index + 1) % len(all_curves)
                    current_curve_func, current_curve_name = all_curves[current_curve_index]
                    points = current_curve_func()
                elif event.key == pygame.K_LEFT:
                    # 切换到上一条曲线
                    current_curve_index = (current_curve_index - 1) % len(all_curves)
                    current_curve_func, current_curve_name = all_curves[current_curve_index]
                    points = current_curve_func()
                elif event.key == pygame.K_SPACE:
                    # 重新生成当前类型的曲线
                    points = current_curve_func()
                elif event.key == pygame.K_a:
                    # 切换自动模式
                    auto_change = not auto_change
                    last_change_time = pygame.time.get_ticks()

        # 自动切换曲线
        if auto_change:
            current_time = pygame.time.get_ticks()
            if current_time - last_change_time > change_interval:
                current_curve_index = (current_curve_index + 1) % len(all_curves)
                current_curve_func, current_curve_name = all_curves[current_curve_index]
                points = current_curve_func()
                last_change_time = current_time

        # 绘制背景
        screen.fill('grey')

        # 绘制边界框
        pygame.draw.rect(screen, BLACK, (DRAW_START_X, DRAW_START_Y, DRAW_WIDTH, DRAW_HEIGHT), 1)

        # 绘制曲线（实线）
        if points and len(points) > 1:
            pygame.draw.lines(screen, BLACK, False, points, LINEWIDTH)

            # 标记起点和终点
            pygame.draw.circle(screen, (255, 0, 0), points[0], 8)  # 红色起点
            pygame.draw.circle(screen, (0, 255, 0), points[-1], 8)  # 绿色终点

            # 计算并显示起点终点距离
            start_point = points[0]
            end_point = points[-1]
            distance = ((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2) ** 0.5

            # 显示距离信息
            distance_text = font.render(f"起点终点距离: {distance:.1f}px", True, BLACK)
            screen.blit(distance_text, (20, 60))

        # 显示当前曲线类型名称
        curve_text = font.render(f"曲线类型: {current_curve_name} ({current_curve_index + 1}/{len(all_curves)})", True,
                                 BLACK)
        screen.blit(curve_text, (20, 20))

        # 显示控制说明
        controls_text = font.render("左右箭头切换曲线 | 空格重新生成 | A键自动轮播 | ESC退出", True, BLACK)
        screen.blit(controls_text, (20, WINDOW_HEIGHT - 40))

        # 显示自动模式状态
        auto_text = font.render("自动模式: " + ("开启" if auto_change else "关闭"), True, BLACK)
        screen.blit(auto_text, (WINDOW_WIDTH - 200, 20))

        # 显示曲线统计信息
        if points:
            stats_text = font.render(f"点数: {len(points)} | 最小距离要求: {line_generator.min_endpoint_distance}px",
                                     True, BLACK)
            screen.blit(stats_text, (20, 100))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


# 如果作为主程序运行，则执行测试函数
if __name__ == "__main__":
    test_curve_generator()