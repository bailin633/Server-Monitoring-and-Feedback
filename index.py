import webbrowser
import os


def open_html():
    file_path = r"C:\Server_Data\index.html"  # 指定要打开的 HTML 文件路径

    # 确保文件存在
    if os.path.isfile(file_path):
        # 使用模块打开
        webbrowser.open(file_path)
    else:
        print("指定的文件不存在，请检查路径。")

