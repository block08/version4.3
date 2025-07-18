# EEG绘图实验系统 v4.3

## 项目概述

这是一个基于Python开发的航天员脑电图(EEG)绘图实验系统，专门用于进行航天员绘图任务的心理学实验研究。系统支持个体和协作绘图任务，具备实时数据收集、分析和EEG同步功能。

## 核心功能

### 实验模式
- **个体绘图模式**: 单人航天员完成绘图任务
- **协作绘图模式**: 两人协作完成绘图任务
  - 人员①+②协作模式
  - 人员①+③协作模式

### 界面特色
- **现代化登录界面**: 简洁的航天员身份选择系统
- **实时速度控制**: +/-按钮调节绘图速度（替代传统滑块）
- **智能暂停系统**: P键暂停，精确计时补偿
- **EEG同步标记**: 实时脑电数据标记
- **自动截图保存**: 绘图前后状态自动记录

## 系统架构

### 核心组件

#### 主要模块
- **src/ui/LoginWindow.py**: PyQt5登录界面，航天员身份选择和会话初始化
- **src/core/main.py**: Pygame主游戏引擎，执行绘图实验
- **src/ui/InterfaceWindow.py**: 主实验界面控制器
- **src/core/paint.py**: 核心绘图机制和曲线生成系统

#### 数据管理
- **Behavioral_data/**: 实验会话数据存储（按时间戳和被试组织）
- **output_data/**: 处理后的实验结果和数据库文件
- **user_account/Experimenter.db**: 参与者管理SQLite数据库

#### 核心功能模块
- **src/core/level.py**: 游戏级别管理，Player类光标控制
- **src/core/game_function.py**: 事件处理和游戏状态管理
- **src/config/settings.py**: 屏幕和游戏配置常量
- **src/hardware/serial_marker.py**: EEG标记同步
- **src/data/Calculate_pixel_difference.py**: 图像分析，支持暂停时间补偿的绘图精度计算
- **src/ui/likert_scale.py**: 任务后问卷实现
- **src/data/handle_slider_event.py**: 速度调整事件处理（按钮式）

## 最新更新 (v4.3)

### 界面改进
1. **登录界面优化**:
   - 移除紫色"航天员"图标按钮
   - "佩戴脑电帽的航天员"文字与"任务编号"对齐
   - 更简洁的界面布局

2. **速度控制系统升级**:
   - 将传统滑块改为直观的+/-按钮
   - 点击式速度调整，每次调整25个单位
   - 减速按钮：红色（可用）/灰色（不可用）
   - 加速按钮：绿色（可用）/灰色（不可用）
   - 中央数值显示区域

3. **任务指导界面更新**:
   - 修改任务描述为"被测航天员控制键盘沿黑色轨迹从绿色起点移至红色终点"
   - 放大文字大小提高可读性
   - 整体布局下移，界面更舒适
   - 移除彩色强调，改用黑色下划线

### 技术改进
1. **暂停时间补偿系统**:
   - 精确追踪P键暂停时间
   - 所有时间计算自动排除暂停时间
   - 确保数据测量准确性

2. **协作模式优化**:
   - 修复绘图表面显示问题
   - 统一图像序列逻辑
   - 改进事件处理机制

## 操作指南

### 系统启动
```bash
# 启动登录界面（推荐方式）
python src/ui/LoginWindow.py

# 直接运行主实验（测试用）
python src/core/main.py

# 模拟模式
python src/core/main_simulation.py
```

### 测试命令
```bash
# 不同实验模式测试
python src/tests/Atest.py    # 测试个体A模式
python src/tests/Btest.py    # 测试个体B模式  
python src/tests/ABtest.py   # 测试协作模式

# 检查串口连接
python src/hardware/check_serial_connection.py
```

### 实验控制
- **空格键**: 开始/下一张图片
- **P键**: 暂停/恢复（带时间补偿）
- **ESC键**: 退出实验
- **WASD**: 光标控制（个体A模式）
- **方向键**: 光标控制（个体B模式）
- **+/- 按钮**: 调整绘图速度

### 速度调整系统
- **速度范围**: 50-300
- **调整步长**: 25
- **默认速度**: 50
- **文件保存**: scroll_value.txt

## 数据结构

### 实验数据组织
```
Behavioral_data/
├── {timestamp_id}/
│   ├── subA/                    # 个体A数据
│   │   ├── data/
│   │   │   └── 数据.txt         # 带暂停补偿的时间数据
│   │   ├── likert_scale/
│   │   └── output_image/
│   │       ├── pre_screenshot0-7.png
│   │       ├── post_screenshot-1.png
│   │       └── post_screenshot0-7.png
│   ├── subAB/                   # 人员①+②协作数据
│   │   └── (相同结构)
│   └── subAC/                   # 人员①+③协作数据
│       └── (相同结构)
```

### 配置文件
- **config.txt**: 当前模式指示器（1=个体A, 3=协作）
- **scroll_value.txt**: 实时速度控制参数
- **Behavioral_data/id.txt**: 当前会话标识符

## 项目结构

```
src/
├── config/          # 配置管理
│   ├── config_manager.py
│   └── settings.py
├── core/           # 核心游戏逻辑
│   ├── main.py
│   ├── main_simulation.py
│   ├── game_function.py
│   ├── game_function_simulation.py
│   ├── level.py
│   ├── paint.py
│   └── painting.py
├── data/           # 数据处理
│   ├── Calculate_pixel_difference.py
│   ├── Deviation_area.py
│   ├── export_txt.py
│   ├── handle_slider_event.py
│   └── login_info_handler.py
├── hardware/       # 硬件接口
│   ├── check_serial_connection.py
│   └── serial_marker.py
├── tests/          # 测试模块
│   ├── Atest.py
│   ├── Btest.py
│   ├── ABtest.py
│   ├── ACtest.py
│   └── Ctest.py
├── ui/             # 用户界面
│   ├── LoginWindow.py
│   ├── InterfaceWindow.py
│   ├── InterfaceUI.py
│   ├── Button.py
│   ├── likert_scale.py
│   └── login.py
└── utils/          # 工具函数
    ├── game_stats.py
    ├── resouce_rc.py
    └── shared_data.py
```

## 游戏分数范围

- **个体A模式**: 0-8
- **协作AB模式**: 11-19  
- **协作AC模式**: 23-31

## 三用户登录系统

- **人员①**: 主要被试（蓝色渐变）- 参与所有三个阶段
- **人员②**: 辅助被试②（粉色渐变）- 参与第二阶段协作
- **人员③**: 辅助被试③（橙色渐变）- 参与第三阶段协作

## 屏幕配置

- **目标分辨率**: 1920x1080（全屏）
- **绘图区域**: 排除上下边距（各100px）
- **坐标系统**: (0,0)位于左上角

## 串口通信

- **初始化**: `initialize_serial()`
- **发送标记**: `serial_marker(bytes([marker_code]))`
- **标准标记**: 
  - 0x01 (开始)
  - 0x02-0x07 (阶段)
  - 0x04 (休息)

## 系统依赖

### 核心库
- **pygame**: 主游戏引擎和图形渲染
- **PyQt5**: GUI框架（登录界面）
- **opencv-cv2**: 图像处理和轨迹分析
- **sqlite3**: 数据库操作
- **numpy**: 数值计算
- **pyserial**: EEG标记通信

## 重要提醒

### 代码修改准则
- **保持暂停时间补偿**: 修改时间逻辑时务必保留暂停时间补偿
- **维护游戏分数范围**: 添加新实验阶段时保持分数范围一致
- **全模式测试**: 更改后测试所有三种模式
- **验证数据准确性**: 确认时间相关修改后的数据文件准确性

### 架构模式
- 每个实验阶段有独立的`dataloading()`函数
- 每种模式有对应的`calculate_pixel_difference()`函数
- 所有时间计算必须考虑`total_pause_time`
- 绘图表面条件必须包含所有三种模式

---

**版本**: v4.3  
**更新日期**: 2025-07-09  
**开发环境**: Python 3.8.10 + Pygame + PyQt5