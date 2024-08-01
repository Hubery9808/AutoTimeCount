import re
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def select_file():
    # 创建 Tkinter 根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏根窗口
    
    # 弹出文件选择对话框
    file_path = filedialog.askopenfilename(
        title="选择要处理的文件",
        filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
    )
    
    if not file_path:
        messagebox.showwarning("警告", "未选择文件！")
        return None
    
    return file_path

def select_save_directory():
    # 创建 Tkinter 根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏根窗口

    # 弹出选择文件夹对话框
    save_dir = filedialog.askdirectory(
        title="选择保存生成文件的文件夹"
    )

    if not save_dir:
        messagebox.showwarning("警告", "未选择保存文件夹！")
        return None
    
    return save_dir

def parse_file(file_path):
    # 使用 UTF-8 编码读取文件
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 正则表达式用于匹配时间戳和数据段
    timestamp_pattern = re.compile(r'\[(.*?)\]')
    data_pattern = re.compile(r'00 00 07 00')

    timestamps = []
    positions = []

    # 查找所有时间戳
    timestamps = timestamp_pattern.findall(content)
    
    # 查找所有“00 00 07 00”数据段的起始位置
    for match in data_pattern.finditer(content):
        positions.append(match.start())

    return timestamps, positions

def calculate_time_intervals(timestamps, positions):
    intervals = []
    matching_indices = []
    non_matching_indices = []

    if len(positions) < 2:
        return intervals, matching_indices, non_matching_indices

    for i in range(len(positions) - 1):
        start_time_str = timestamps[i]
        end_time_str = timestamps[i + 1]
        
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S.%f')
        
        # 计算时间间隔，并转换为毫秒
        interval_ms = (end_time - start_time).total_seconds() * 1000
        intervals.append(interval_ms)

        # 检查时间间隔是否在指定范围内
        if (450 <= interval_ms <= 550) or (4500 <= interval_ms <= 5500):
            matching_indices.append(i)  # 记录符合条件的间隔的索引
        else:
            non_matching_indices.append(i)  # 记录不符合条件的间隔的索引

    return intervals, matching_indices, non_matching_indices

def save_results_to_file(timestamps, matching_indices, non_matching_indices, save_dir):
    # 生成文件名
    timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    matching_file_name = os.path.join(save_dir, f"{timestamp_str}_07指令间隔_符合条件.txt")
    
    with open(matching_file_name, 'w', encoding='utf-8') as matching_file:
        if matching_indices:
            matching_file.write("符合条件的时间间隔对应的上下两段时间戳：\n")
            for index in matching_indices:
                if index > 0 and index < len(timestamps) - 1:
                    start_time_str = timestamps[index]
                    end_time_str = timestamps[index + 1]
                    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f')
                    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S.%f')
                    interval_ms = (end_time - start_time).total_seconds() * 1000
                    
                    matching_file.write(f"第 {index + 1} 段时间戳：\n")
                    matching_file.write(f"开始时间：{start_time_str}\n")
                    matching_file.write(f"结束时间：{end_time_str}\n")
                    matching_file.write(f"时间间隔：{interval_ms:.3f} 毫秒\n")
                    matching_file.write("-" * 50 + "\n")

    # 根据是否存在不符合条件的间隔决定是否生成不符合条件的文件
    if non_matching_indices:
        non_matching_file_name = os.path.join(save_dir, f"{timestamp_str}_07指令间隔_不符合条件.txt")
        with open(non_matching_file_name, 'w', encoding='utf-8') as non_matching_file:
            non_matching_file.write("不符合条件的时间间隔对应的上下两段时间戳：\n")
            for index in non_matching_indices:
                if index > 0 and index < len(timestamps) - 1:
                    start_time_str = timestamps[index]
                    end_time_str = timestamps[index + 1]
                    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f')
                    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S.%f')
                    interval_ms = (end_time - start_time).total_seconds() * 1000
                    
                    non_matching_file.write(f"第 {index + 1} 段时间戳：\n")
                    non_matching_file.write(f"开始时间：{start_time_str}\n")
                    non_matching_file.write(f"结束时间：{end_time_str}\n")
                    non_matching_file.write(f"时间间隔：{interval_ms:.3f} 毫秒\n")
                    non_matching_file.write("-" * 50 + "\n")
        
        # 弹出提示框，通知用户存在不符合条件的间隔
        messagebox.showinfo("信息", "本次测试有07间隔不符合条件，详情请看生成的文件。")
    else:
        # 弹出提示框，通知用户所有间隔都符合条件
        messagebox.showinfo("信息", "本次测试07间隔均符合条件。")

def print_to_terminal(timestamps, matching_indices, non_matching_indices):
    if matching_indices:
        print("符合条件的时间间隔对应的上下两段时间戳：")
        for index in matching_indices:
            if index > 0 and index < len(timestamps) - 1:
                start_time_str = timestamps[index]
                end_time_str = timestamps[index + 1]
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f')
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S.%f')
                interval_ms = (end_time - start_time).total_seconds() * 1000
                
                print(f"第 {index + 1} 段时间戳：")
                print(f"开始时间：{start_time_str}")
                print(f"结束时间：{end_time_str}")
                print(f"时间间隔：{interval_ms:.3f} 毫秒")
                print("-" * 50)

    if non_matching_indices:
        print("不符合条件的时间间隔对应的上下两段时间戳：")
        for index in non_matching_indices:
            if index > 0 and index < len(timestamps) - 1:
                start_time_str = timestamps[index]
                end_time_str = timestamps[index + 1]
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f')
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S.%f')
                interval_ms = (end_time - start_time).total_seconds() * 1000
                
                print(f"第 {index + 1} 段时间戳：")
                print(f"开始时间：{start_time_str}")
                print(f"结束时间：{end_time_str}")
                print(f"时间间隔：{interval_ms:.3f} 毫秒")
                print("-" * 50)

def main():
    file_path = select_file()
    if file_path:
        save_dir = select_save_directory()
        if save_dir:
            timestamps, positions = parse_file(file_path)
            intervals, matching_indices, non_matching_indices = calculate_time_intervals(timestamps, positions)
            print_to_terminal(timestamps, matching_indices, non_matching_indices)
            save_results_to_file(timestamps, matching_indices, non_matching_indices, save_dir)

if __name__ == "__main__":
    main()
