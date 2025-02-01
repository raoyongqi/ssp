import rasterio
import numpy as np

ssp_scenario = '370'
tiff_file1 = f'result/predicted_{ssp_scenario}_rf.tif'
tiff_file2 = 'pl/predicted_rf.tif'
output_file = f'result/sub_{ssp_scenario}_rf.tif'

# 读取文件
with rasterio.open(tiff_file1) as src1, rasterio.open(tiff_file2) as src2:
    data1 = src1.read(1).astype(np.float64)
    data2 = src2.read(1).astype(np.float64)
    profile = src1.profile

    # 处理 nodata 值
    if src1.nodata is not None:
        data1[data1 == src1.nodata] = np.nan
    if src2.nodata is not None:
        data2[data2 == src2.nodata] = np.nan

    # 确保形状一致
    if data1.shape != data2.shape:
        raise ValueError("The shapes of the two TIFF files do not match.")

    # 相减运算，忽略 nodata
    result_data = np.where(~np.isnan(data1) & ~np.isnan(data2), data1 - data2, np.nan)

# 更新 profile 并保存
profile.update({
    'dtype': 'float64',
    'count': 1,
    'nodata': np.nan
})

with rasterio.open(output_file, 'w', **profile) as dst:
    dst.write(result_data, 1)

print(f"Output TIFF file has been created at: {output_file}")
