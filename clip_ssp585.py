import os
import rasterio
from rasterio.mask import mask
import numpy as np
import geopandas as gpd

# 1. 加载 GeoJSON 文件
# grasslands_geojson_file = '/home/r/Desktop/r-climate/data/clipped_data.geojson'
grasslands_geojson_file = 'data/clipped_data.geojson'

grasslands_gdf = gpd.read_file(grasslands_geojson_file)

# 2. 筛选出值等于 10 的 Grasslands (草地)
grasslands_gdf_filtered = grasslands_gdf[grasslands_gdf['value'] == 10]

# 输入文件夹列表
tiff_folders = [
    'CMIP6/ACCESS-CM2/ssp585/2021-2040s/',
    'data/HWSD_1247/tif/'

]

# 指定输出文件夹路径
geojson_output_folder = 'cropped_data/geojson/'
tiff_output_folder = 'cropped_data/tiff/'

# 创建输出文件夹（如果不存在）
os.makedirs(geojson_output_folder, exist_ok=True)
os.makedirs(tiff_output_folder, exist_ok=True)

# 遍历 TIFF 文件夹列表中的每个文件夹
for tiff_folder in tiff_folders:
    if not os.path.isdir(tiff_folder):
        print(f"Folder does not exist: {tiff_folder}")
        continue

    for tiff_file in os.listdir(tiff_folder):
        if tiff_file.endswith('.tif'):
            tiff_path = os.path.join(tiff_folder, tiff_file)
            
            # 构建输出路径
            tiff_output_path = os.path.join(tiff_output_folder, f'cropped_{tiff_file}')
            geojson_output_path = os.path.join(geojson_output_folder, f'cropped_{os.path.splitext(tiff_file)[0]}.geojson')

            # 读取 TIFF 文件
            with rasterio.open(tiff_path) as src:
                # 读取所有波段并转换为浮点型
                image_data = src.read(1).astype(np.float32)

                # 创建一个临时的内存文件来保存转换后的图像
                with rasterio.MemoryFile() as memfile:
                    with memfile.open(
                        driver="GTiff",
                        height=image_data.shape[0],
                        width=image_data.shape[1],
                        count=1,
                        dtype="float32",
                        crs=src.crs,
                        transform=src.transform,
                        nodata=np.nan,
                    ) as dataset:
                        dataset.write(image_data, 1)

                        # 使用 GeoDataFrame 的几何对象进行剪切，并处理缺失值
                        out_image, out_transform = mask(dataset, grasslands_gdf_filtered.geometry, crop=True, nodata=np.nan)

                        # 更新元数据
                        out_meta = dataset.meta.copy()
                        out_meta.update({
                            "driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform,
                            "dtype": "float32",  # 保持数据类型为浮点型
                            "nodata": 0  # 设置 nodata 为 0
                        })

                        # 过滤掉为 NaN 的像素值，将 NaN 值替换为 0
                        out_image = np.where(np.isnan(out_image), 0, out_image)  # 这里将 NaN 替换为 0

                        # 保存剪切后的 TIFF 结果
                        with rasterio.open(tiff_output_path, "w", **out_meta) as dest:
                            # Write the first band only, as we're dealing with single-band images
                            dest.write(out_image[0], 1)  # out_image[0] is a 2D array

            # 将 GeoJSON 中的值更新为裁剪后的 TIFF 中的值
            with rasterio.open(tiff_output_path) as cropped_src:
                for idx, row in grasslands_gdf_filtered.iterrows():
                    geom = row['geometry']
                    if geom.is_empty:
                        continue

                    # 将几何体转换为 TIFF 窗口坐标
                    coords = np.array(geom.exterior.coords)
                    pixel_coords = [cropped_src.index(x, y) for x, y in coords]

                    # 计算区域的像素值
                    pixel_values = []
                    for row, col in pixel_coords:
                        if 0 <= row < cropped_src.height and 0 <= col < cropped_src.width:
                            pixel_value = cropped_src.read(1)[row, col]
                            if not np.isnan(pixel_value):
                                pixel_values.append(pixel_value)

                    if pixel_values:
                        avg_value = np.nanmean(pixel_values)  # 使用平均值来代表区域
                        grasslands_gdf_filtered.at[idx, 'value'] = avg_value
                    else:
                        grasslands_gdf_filtered.at[idx, 'value'] = np.nan

            # 保存更新后的 GeoJSON 文件
            grasslands_gdf_filtered.to_file(geojson_output_path, driver="GeoJSON")
            
            print(f"Clipped TIFF image saved to {tiff_output_path}")
            print(f"Corresponding GeoJSON saved to {geojson_output_path}")
