#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os
import sys


class SerialConfigManager:
    """串口配置管理器"""

    def __init__(self):
        # --- 修改：使用相对于项目根目录的相对路径 ---
        # 假设脚本总是从项目根目录执行
        self.config_file = os.path.join('src', 'config', 'serial_config.ini')

        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
                # 如果读取后没有 'SERIAL' 部分，也创建默认配置
                if not self.config.has_section('SERIAL'):
                    self.create_default_config()
            else:
                # 如果配置文件不存在，创建默认配置
                self.create_default_config()
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            self.create_default_config()

    def create_default_config(self):
        """创建默认配置"""
        print("创建默认配置文件...")
        self.config['SERIAL'] = {
            'baudrate': '57600',
            'timeout': '1',
            'bytesize': '8',
            'stopbits': '1',
            'parity': 'N'
        }
        self.save_config()

    def save_config(self):
        """保存配置文件"""
        try:
            # --- 修改：在保存前，直接确保目录存在 ---
            # 移除了独立的 ensure_dir_exists 函数，将功能内联
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置文件时出错: {e}")

    def get_baudrate(self):
        """获取波特率"""
        try:
            return self.config.get('SERIAL', 'baudrate', fallback='57600')
        except (ValueError, configparser.NoSectionError):
            return '57600'

    def set_baudrate(self, baudrate):
        """设置波特率"""
        try:
            if not self.config.has_section('SERIAL'):
                self.config.add_section('SERIAL')
            self.config.set('SERIAL', 'baudrate', str(baudrate))
            self.save_config()
        except Exception as e:
            print(f"设置波特率时出错: {e}")

    def get_timeout(self):
        """获取超时时间"""
        try:
            return float(self.config.get('SERIAL', 'timeout', fallback='1'))
        except (ValueError, configparser.NoSectionError):
            return 1.0

    def get_bytesize(self):
        """获取数据位"""
        try:
            return int(self.config.get('SERIAL', 'bytesize', fallback='8'))
        except (ValueError, configparser.NoSectionError):
            return 8

    def get_stopbits(self):
        """获取停止位"""
        try:
            return int(self.config.get('SERIAL', 'stopbits', fallback='1'))
        except (ValueError, configparser.NoSectionError):
            return 1

    def get_parity(self):
        """获取校验位"""
        return self.config.get('SERIAL', 'parity', fallback='N')

    def get_all_settings(self):
        """获取所有串口设置"""
        return {
            'baudrate': self.get_baudrate(),
            'timeout': self.get_timeout(),
            'bytesize': self.get_bytesize(),
            'stopbits': self.get_stopbits(),
            'parity': self.get_parity()
        }


# 全局配置管理器实例
serial_config = SerialConfigManager()

# 测试代码
if __name__ == '__main__':
    print("--- 串口配置测试 ---")
    print(f"当前所有设置: {serial_config.get_all_settings()}")

    # 测试读取波特率
    current_baudrate = serial_config.get_baudrate()
    print(f"当前波特率: {current_baudrate}")

    # 测试设置新波特率
    new_baudrate = '115200'
    print(f"设置新波特率: {new_baudrate}")
    serial_config.set_baudrate(new_baudrate)

    # 验证新波特率
    updated_baudrate = serial_config.get_baudrate()
    print(f"更新后的波特率: {updated_baudrate}")

    # 恢复原设置
    print(f"恢复原波特率: {current_baudrate}")
    serial_config.set_baudrate(current_baudrate)
    print(f"最终波特率: {serial_config.get_baudrate()}")
