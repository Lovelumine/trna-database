import os
import re

# 设置文件夹路径
folder_path = './'  # 替换为你的文件夹路径

# 定义正则表达式模式匹配以ttd开头并且包含数字的文件
pattern = re.compile(r'^(ttd\d+).*\.pdb$')

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith('.pdb'):
        match = pattern.match(filename)
        if match:
            # 获取ttd和数字部分
            base_name = match.group(1)
            new_name = base_name + '.pdb'  # 新的文件名
            
            # 获取文件的完整路径
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_name)
            
            # 重命名文件
            os.rename(old_file_path, new_file_path)
            print(f'Renamed: {old_file_path} to {new_file_path}')
