import serial
from src.config import config_manager
from src.utils import shared_data
import time
import serial.tools.list_ports
import threading


def sleep_with_check(duration, check_interval=0.1):
    """可中断的延迟函数"""
    elapsed = 0
    while elapsed < duration:
        # 检查是否有停止信号（通过线程local存储）
        current_thread = threading.current_thread()
        if hasattr(current_thread, 'stop_event') and current_thread.stop_event and current_thread.stop_event.is_set():
            break
        
        sleep_time = min(check_interval, duration - elapsed)
        time.sleep(sleep_time)
        elapsed += sleep_time

def find_port_by_device(device_keyword):
    """
    根据设备关键字查找对应的COM口
    device_keyword: 设备描述中的关键字，如 'USB Serial' 或 'Arduino' 等
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # 打印详细信息方便调试
        print(f"检查端口: {port.device}")
        print(f"描述: {port.description}")
        print(f"硬件ID: {port.hwid}")
        print("-" * 50)

        # 在设备描述和硬件ID中搜索关键字
        if (device_keyword.lower() in port.description.lower() or
                device_keyword.lower() in port.hwid.lower()):
            return port.device
    return None


# 全局变量
ser = None

# 程序开始时
def initialize_serial():
    global ser
    try:
        # 如果串口已经打开，先关闭它
        if ser is not None and ser.is_open:
            ser.close()
            time.sleep(0.5)  # 等待端口释放
        
        ser = serial.Serial(
            shared_data.global_port,
            shared_data.global_baudrate,
            serial.EIGHTBITS,
            serial.PARITY_NONE,
            serial.STOPBITS_ONE,
            timeout=shared_data.global_response_delay,
            rtscts=False,
            dsrdtr=False,
            exclusive=True  # 独占模式
        )
        print(f"Serial port {shared_data.global_port} initialized successfully")
        return True
    except serial.SerialException as e:
        if "PermissionError" in str(e) or "拒绝访问" in str(e):
            print(f"端口 {shared_data.global_port} 被其他程序占用。请关闭可能使用该端口的程序：")
            print("- 设备管理器")
            print("- 其他串口监控工具")
            print("- Arduino IDE 或其他开发工具")
            print("- 之前运行的本程序实例")
            print("然后重新检测端口")
        else:
            print(f"Serial initialization failed: {e}")
        ser = None
        return False
    except Exception as e:
        print(f"Serial initialization failed: {e}")
        ser = None
        return False


# 发送标记时
def serial_marker(data_to_send):
    global ser
    if ser is None:
        print("Serial port not initialized, skipping marker")
        return
    
    try:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        # 设置串口超时
        if hasattr(ser, 'timeout'):
            original_timeout = ser.timeout
            ser.timeout = 2.0  # 2秒超时
        
        bytes_written = ser.write(data_to_send)
        print(f"Bytes written: {bytes_written}")
        
        # 使用可中断的延迟
        sleep_with_check(shared_data.global_response_delay)

        clear_zero = bytes([0x00])
        sleep_with_check(shared_data.global_clear_delay)
        ser.write(clear_zero)
        
        # 恢复原始超时设置
        if hasattr(ser, 'timeout'):
            ser.timeout = original_timeout
    except Exception as e:
        print(f"Serial communication error: {e}")


def close_serial():
    """关闭串口连接"""
    global ser
    try:
        if ser is not None and ser.is_open:
            ser.close()
            print("Serial port closed successfully")
        ser = None
    except Exception as e:
        print(f"Error closing serial port: {e}")
        ser = None