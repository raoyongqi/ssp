import rasterio
import numpy as np
ssp_scenario = 'ssp126'
# 输入的两个 TIFF 文件路径
tiff_file1 = f'result/{ssp_scenario}/cropped/cropped_{ssp_scenario}_rf.tif' # 替换为你的第一个 TIFF 文件路径
tiff_file2 = 'pic/cropped_predicted_rf.tif'  # 替换为你的第二个 TIFF 文件路径
output_file = f'result/{ssp_scenario}/sub_{ssp_scenario}_rf.tif'  # 替换为输出文件路径


# 读取第一个 TIFF 文件
with rasterio.open(tiff_file1) as src1:
    data1 = src1.read(1)  # 读取第一波段数据
    profile = src1.profile  # 获取文件的元数据

# 读取第二个 TIFF 文件
with rasterio.open(tiff_file2) as src2:
    data2 = src2.read(1)  # 读取第一波段数据

# 确保两个数组的形状相同
if data1.shape != data2.shape:
    raise ValueError("The shapes of the two TIFF files do not match.")

# 进行相减运算
result_data = data1 - data2

# 更新输出文件的 profile（可以根据需要修改）
profile.update({
    'dtype': 'float32',  # 修改数据类型，如果需要的话
    'count': 1,          # 输出文件只有一个波段
})

# 写入结果到新的 TIFF 文件
with rasterio.open(output_file, 'w', **profile) as dst:
    dst.write(result_data, 1)  # 将结果写入第一波段

print(f"Output TIFF file has been created at: {output_file}")
