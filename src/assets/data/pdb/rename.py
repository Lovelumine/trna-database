import os
import re

# 设置文件夹路径
folder_path = 'src/assets/data/pdb'  # 替换为你的文件夹路径

# 定义正则表达式模式匹配以 ttd 开头并且包含数字的文件
pattern = r"ttd(\d+)"  # 匹配 ttd 后跟数字的模式

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    print(f"正在处理文件：{filename}")  # 输出当前正在处理的文件名

    # 使用正则表达式查找匹配的文件
    match = re.match(pattern, filename)
    
    if match:
        # 提取数字部分
        number = match.group(1)
        # 构造新的文件名，替换 ttd 为 ensure-数字
        new_filename = f"ensure-{number}.pdb" if filename.endswith(".pdb") else f"ensure-{number}{os.path.splitext(filename)[1]}"
        
        # 输出新的文件名
        print(f"匹配成功！新文件名：{new_filename}")

        # 构造旧文件和新文件的完整路径
        old_filepath = os.path.join(folder_path, filename)
        new_filepath = os.path.join(folder_path, new_filename)
        
        # 重命名文件
        os.rename(old_filepath, new_filepath)
        print(f"文件 {filename} 已重命名为 {new_filename}")
    else:
        # 输出未匹配到的文件
        print(f"文件 {filename} 不符合匹配模式，跳过。")
