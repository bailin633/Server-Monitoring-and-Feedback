import os


def user_time_sleep():
    while True:
        minutes = input("请输入检测时间间隔(分钟): ")
        # 检测输入是否是数字或者小数点
        if minutes.replace('.', '', 1).isdigit() or '.' in minutes:
            try:
                user_time = float(minutes) * 60  # 转换为秒
                return user_time
            except ValueError:
                print("输入无效，请重新输入。")
        else:
            print("输入无效，请重新输入。")

