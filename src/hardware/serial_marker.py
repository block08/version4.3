import serial
from src.config import config_manager
from src.utils import shared_data
import time
import serial.tools.list_ports

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
        ser = serial.Serial(
            shared_data.global_port,
            shared_data.global_baudrate,
            serial.EIGHTBITS,
            serial.PARITY_NONE,
            serial.STOPBITS_ONE,
            timeout=shared_data.global_response_delay,
            rtscts=False,
            dsrdtr=False
        )
        return True
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
        bytes_written = ser.write(data_to_send)
        print(f"Bytes written: {bytes_written}")
        time.sleep(shared_data.global_response_delay)

        clear_zero = bytes([0x00])
        time.sleep(shared_data.global_clear_delay)
        ser.write(clear_zero)
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