import os
import shutil

# 指定文件夹路径
folder_path = 'tiff'
destination_folder = 'common'  # 新文件夹的路径

# 需要匹配的关键词列表
keywords = [
    'elev', 'srad_01', 'srad_02', 'srad_03', 'srad_04', 'srad_05', 'srad_06', 'srad_07', 
    'srad_08', 'srad_09', 'srad_10', 'srad_11', 'srad_12', 'tavg_01', 'tavg_02', 'tavg_03', 
    'tavg_04', 'tavg_05', 'tavg_06', 'tavg_07', 'tavg_08', 'tavg_09', 'tavg_10', 'tavg_11', 
    'tavg_12', 'vapr_01', 'vapr_02', 'vapr_03', 'vapr_04', 'vapr_05', 'vapr_06', 'vapr_07', 
    'vapr_08', 'vapr_09', 'vapr_10', 'vapr_11', 'vapr_12', 'wind_01', 'wind_02', 'wind_03', 
    'wind_04', 'wind_05', 'wind_06', 'wind_07', 'wind_08', 'wind_09', 'wind_10', 'wind_11', 
    'wind_12'
]

# 获取文件夹中的文件
files = os.listdir(folder_path)

# 过滤出文件名中包含指定关键词的文件
matching_files = [f for f in files if any(keyword in f for keyword in keywords)]

# 确保目标文件夹存在，如果不存在则创建
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# 移动匹配的文件到新的文件夹
for file in matching_files:
    source_path = os.path.join(folder_path, file)
    destination_path = os.path.join(destination_folder, file)
    
    # 移动文件
    shutil.move(source_path, destination_path)
    print(f"Moved {file} to {destination_folder}")
