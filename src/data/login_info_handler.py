# login_info_handler.py
import os
import time
from src.config.config_manager import get_id_file_path


class LoginInfoHandler:
    def __init__(self):
        self.subject1_info = None
        self.subject2_info = None
        self.subject3_info = None
        self.login_time = None
        self.task_code = None

    def set_subject1_info(self, id, gender, hand_preference, mark):
        """设置被试1的信息"""
        self.subject1_info = {
            'id': id,
            'gender': gender,
            'hand_preference': hand_preference,
            'mark': mark
        }

    def set_subject2_info(self, id, gender, hand_preference, mark):
        """设置被试2的信息"""
        self.subject2_info = {
            'id': id,
            'gender': gender,
            'hand_preference': hand_preference,
            'mark': mark
        }

    def set_subject3_info(self, id, gender, hand_preference, mark):
        """设置被试3的信息"""
        self.subject3_info = {
            'id': id,
            'gender': gender,
            'hand_preference': hand_preference,
            'mark': mark
        }

    def set_login_time(self, login_time):
        """设置登录时间"""
        self.login_time = login_time

    def set_task_code(self, task_code):
        """设置任务代号"""
        self.task_code = task_code

    def create_experiment_folder(self):
        """创建实验文件夹"""
        if not (self.subject1_info and self.subject2_info and self.subject3_info):
            raise ValueError("被试信息不完整，无法创建文件夹")
        
        if not self.task_code:
            raise ValueError("任务代号不能为空，无法创建文件夹")

        # 创建文件夹名称：时间_任务代号_三个受试者代号
        time_str = time.strftime("%m_%d_%H_%M")
        # 将受试者ID格式化为两位数字
        sub1_id = f"{int(self.subject1_info['id']):02d}"
        sub2_id = f"{int(self.subject2_info['id']):02d}"
        sub3_id = f"{int(self.subject3_info['id']):02d}"
        folder_name = f"{time_str}_{self.task_code}_{sub1_id}_{sub2_id}_{sub3_id}"

        # 在 Behavioral_data 下创建主文件夹
        base_path = "./Behavioral_data"
        full_path = os.path.join(base_path, folder_name)

        # 创建子文件夹结构
        sub1_path = os.path.join(full_path, "subA")
        sub2_path = os.path.join(full_path, "subAB")
        sub3_path = os.path.join(full_path, "subAC")

        # 创建所有必要的子目录
        for path in [sub1_path, sub2_path, sub3_path]:
            os.makedirs(os.path.join(path, "likert_scale"), exist_ok=True)
            os.makedirs(os.path.join(path, "output_image"), exist_ok=True)
            os.makedirs(os.path.join(path, "data"), exist_ok=True)

        # 创建信息文件
        info_file_path = os.path.join(full_path, "subject_info.txt")
        with open(info_file_path, "w", encoding="utf-8") as f:
            f.write(f"登录时间: {self.login_time}\n\n")
            f.write("主受试者信息:\n")
            f.write(f"ID: {self.subject1_info['id']}\n")
            f.write(f"性别: {self.subject1_info['gender']}\n")
            f.write(f"惯用手: {self.subject1_info['hand_preference']}\n"
                    f"标识: {self.subject1_info['mark']}\n\n")
            f.write("协助受试者②信息:\n")
            f.write(f"ID: {self.subject2_info['id']}\n")
            f.write(f"性别: {self.subject2_info['gender']}\n")
            f.write(f"惯用手: {self.subject2_info['hand_preference']}\n"
                    f"标识: {self.subject2_info['mark']}\n\n")
            f.write("协助受试者③信息:\n")
            f.write(f"ID: {self.subject3_info['id']}\n")
            f.write(f"性别: {self.subject3_info['gender']}\n")
            f.write(f"惯用手: {self.subject3_info['hand_preference']}\n"
                    f"标识: {self.subject3_info['mark']}\n")

        # 更新id.txt文件
        with open(get_id_file_path(), "w") as f:
            f.write(folder_name)

        return full_path


def create_experiment_structure(task_code, subject1_id, subject2_id, subject1_gender, subject2_gender,
                                subject1_hand, subject2_hand, subject1_mark, subject2_mark, login_time,
                                subject3_id=None, subject3_gender=None, subject3_hand=None, subject3_mark=None):
    """创建实验目录结构的便捷函数"""
    handler = LoginInfoHandler()
    handler.set_task_code(task_code)
    handler.set_subject1_info(subject1_id, subject1_gender, subject1_hand, subject1_mark)
    handler.set_subject2_info(subject2_id, subject2_gender, subject2_hand, subject2_mark)
    if subject3_id is not None:
        handler.set_subject3_info(subject3_id, subject3_gender, subject3_hand, subject3_mark)
    handler.set_login_time(login_time)
    return handler.create_experiment_folder()