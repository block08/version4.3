import serial
import serial.tools.list_ports


def check_serial_connection(port):
    """
    检查串口连接状态
    对于CH340设备，即使被占用也返回True（显示为绿色）
    """
    try:
        # 首先检查是否是CH340设备
        is_ch340 = False
        try:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if p.device == port:
                    port_description = p.description.upper()
                    if any(keyword in port_description for keyword in ['CH340', 'USB-SERIAL', 'USB SERIAL']):
                        is_ch340 = True
                        break
        except:
            pass

        # 尝试连接串口
        ser = serial.Serial(port, 9600, timeout=0.1)
        ser.close()
        return True

    except serial.SerialException as e:
        # 如果是CH340设备且错误是"拒绝访问"，也返回True
        if is_ch340 and ("拒绝访问" in str(e) or "Access is denied" in str(e) or "PermissionError" in str(e)):
            print(f"CH340设备 {port} 被占用，但仍显示为连接状态")
            return True
        else:
            print(f"串口 {port} 连接失败: {e}")
            return False
    except Exception as e:
        print(f"检查串口 {port} 时发生未知错误: {e}")
        return False