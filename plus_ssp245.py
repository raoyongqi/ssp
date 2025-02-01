import os
import shutil
import rasterio
import numpy as np

# 指定文件夹路径
source_folder = 'cropped'  # 原始 TIFF 文件所在文件夹
destination_folder = 'result'  # 目标文件夹
os.makedirs(destination_folder, exist_ok=True)
folder_path = 'cropped_data/ssp126/tiff'

for filename in os.listdir(folder_path):
    if filename.endswith('.tif') or filename.endswith('.tiff'):
        # 如果文件名包含 'cropped_wc2.1_5m_'
        if filename.startswith('wc2.1_5m_'):
            new_filename = filename.replace('wc2.1_5m_', '')
            # 构造完整的旧文件路径和新文件路径
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            # 重命名文件
            os.rename(old_file_path, new_file_path)
for filename in os.listdir(folder_path):
    if filename.endswith('.tif') or filename.endswith('.tiff'):
        # 如果文件名包含 'cropped_wc2.1_5m_'
        if filename.startswith('wc2.1_2.5m_'):
            new_filename = filename.replace('wc2.1_2.5m_', '')
            # 构造完整的旧文件路径和新文件路径
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            # 重命名文件
            os.rename(old_file_path, new_file_path)
# 确保目标文件夹存在
for filename in os.listdir(folder_path):
    if filename.endswith('.tif') or filename.endswith('.tiff'):
        # 如果文件名包含 'resampled'
        if 'resampled' in filename:
            new_filename = filename.replace('_resampled', '')
            # 构造完整的旧文件路径和新文件路径
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            # 重命名文件
            os.rename(old_file_path, new_file_path)


for filename in os.listdir(folder_path):
    if filename.endswith('.tif') or filename.endswith('.tiff'):
        # 如果文件名包含 'cropped_wc2.1_5m_'
        if filename.startswith('cropped_'):
            new_filename = filename.replace('cropped_', '')
            # 构造完整的旧文件路径和新文件路径
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            # 重命名文件
            os.rename(old_file_path, new_file_path)
for filename in os.listdir(folder_path):
    if filename.endswith('.tif') or filename.endswith('.tiff'):
        name_without_extension, extension = os.path.splitext(filename)
        
        # 如果文件名包含下划线
        if '_' in name_without_extension:
            parts = name_without_extension.split('_')  # 用下划线拆分文件名
            new_filename = ""

            if len(parts) > 1 and parts[0] == parts[-1]:  # 如果前后部分相同
                new_filename = '_'.join(parts[:1])  # 取前一个部分作为文件名
            elif len(parts) > 2 and parts[1] == parts[-1]:  # 如果第二部分和最后部分相同
                new_filename = '_'.join(parts[:2])  # 取前两个部分作为文件名
            elif len(parts) > 3 and parts[2] == parts[-1]:  # 如果第三部分和最后部分相同
                new_filename = '_'.join(parts[:3])  # 取前三个部分作为文件名
            else:
                new_filename = name_without_extension # 否则保留原文件名

            # 重新构造完整的文件名
            new_filename += extension
            

            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            
            # 重命名文件
            if old_file_path != new_file_path:  # 确保新文件名和旧文件名不同
                shutil.copy(old_file_path, new_file_path)
                print(f'Renamed: {filename} -> {new_filename}')


def process_tif_files(folder_path, output_file_path, prefix, operation="sum"):
    # 获取符合前缀条件的 TIFF 文件
    tif_files = [f for f in os.listdir(folder_path) if f.endswith(('.tif', '.tiff')) and f.startswith(prefix)]
    
    if not tif_files:
        print(f"No TIFF files with the prefix '{prefix}' found.")
        return
    
    # 读取第一个 TIFF 文件，作为参考
    first_tif_path = os.path.join(folder_path, tif_files[0])
    with rasterio.open(first_tif_path) as src:
        meta = src.meta
        # 使用 float64 类型进行累加
        result_array = src.read(1).astype(np.float64)
    
    # 对剩下的 TIFF 文件进行操作
    for tif in tif_files[1:]:
        tif_path = os.path.join(folder_path, tif)
        with rasterio.open(tif_path) as src:
            data = src.read(1).astype(np.float64)
            result_array += data  # 累加操作
    
    # 如果操作是求平均
    if operation == "mean":
        result_array /= len(tif_files)
    
    # 更新元数据（保持 dtype 为 float64）
    meta.update(dtype=rasterio.float64, count=1)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    # 保存结果为新的 TIFF 文件
    with rasterio.open(output_file_path, 'w', **meta) as dst:
        dst.write(result_array, 1)
    
    print(f"Result saved as: {output_file_path}")

# 调用函数处理不同变量
process_tif_files('cropped_data/ssp126/tiff', 'plus/126/MAP.tif', 'prec', operation="sum")
process_tif_files('cropped_data/ssp126/tiff', 'plus/126/TMAX.tif', 'tmax', operation="mean")
process_tif_files('cropped_data/ssp126/tiff', 'plus/126/TMIN.tif', 'tmin', operation="mean")
process_tif_files('cropped_data/ssp126/tiff', 'plus/126/TAVG.tif', 'tavg', operation="mean")
process_tif_files('cropped_data/ssp126/tiff', 'plus/126/SRAD.tif', 'srad', operation="mean")
process_tif_files('cropped_data/ssp126/tiff', 'plus/126/WIND.tif', 'wind', operation="mean")
process_tif_files('cropped_data/ssp126/tiff', 'plus/126/VAPR.tif', 'vapr', operation="mean")
