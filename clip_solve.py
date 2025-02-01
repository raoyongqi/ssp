import os
import rasterio
from rasterio.mask import mask
import numpy as np
import geopandas as gpd
import platform
import pandas as pd
# 检测操作系统
if platform.system() == "Windows":
    base_path = os.getcwd()  # Windows 环境的文件路径
else:
    base_path = '/home/r/Desktop/ssp'  # Linux 环境的文件路径

# 加载 geojson 和 CSV 文件
geojson_file_path = '中华人民共和国分市.json'  # 请确保这个文件路径正确
gdf_geojson = gpd.read_file(geojson_file_path)

df = pd.read_csv('data/climate_soil_loc.csv')

# 过滤数据
cities_data = df[['City', 'Province', 'District']]
unique_cities = df['City'].unique()
filtered_gdf = gdf_geojson[gdf_geojson['name'].isin(unique_cities)]
filtered_gdf = filtered_gdf[filtered_gdf.is_valid]

merged_df = pd.merge(cities_data, filtered_gdf, left_on='City', right_on='name', how='inner')

provinces_to_include = ['西藏自治区', '新疆维吾尔自治区', '甘肃省', '青海省', '四川省', '内蒙古自治区']
filtered_merged_df = merged_df[merged_df['Province'].isin(provinces_to_include)]

province_gdf = gpd.read_file('中华人民共和国.json')
excluded_provinces = ['西藏自治区', '新疆维吾尔自治区', '甘肃省', '青海省', '四川省', '内蒙古自治区']
filtered_province_gdf = province_gdf[~province_gdf['name'].isin(excluded_provinces)]

merged_gdf = gpd.GeoDataFrame(pd.concat([filtered_merged_df, filtered_province_gdf], ignore_index=True))

# 指定输入 TIFF 文件夹路径
if platform.system() == "Windows":
    tiff_folders = ['result']
else:
    tiff_folders = ['result']

# 指定输出文件夹路径
geojson_output_folder = os.path.join(base_path, 'cropped_result', 'geojson')
tiff_output_folder = os.path.join(base_path, 'cropped_result', 'tiff')
os.makedirs(geojson_output_folder, exist_ok=True)
os.makedirs(tiff_output_folder, exist_ok=True)

# 遍历每个 TIFF 文件所在的文件夹
for tiff_folder in tiff_folders:
    if not os.path.isdir(tiff_folder):
        print(f"文件夹 {tiff_folder} 不存在！")
        continue

    for tiff_file in os.listdir(tiff_folder):
        tiff_file_path = os.path.join(tiff_folder, tiff_file)

        if tiff_file.endswith(".tif") or tiff_file.endswith(".tiff"):
            # 打开 TIFF 文件并获取其投影
            with rasterio.open(tiff_file_path) as src:
                tiff_crs = src.crs  # 获取 TIFF 文件的 CRS (投影)

            # 确保 GeoDataFrame 使用与 TIFF 相同的投影
            if merged_gdf.crs != tiff_crs:
                merged_gdf = merged_gdf.to_crs(tiff_crs)

            # 提取几何体
            geometries = merged_gdf.geometry.values  # 获取所有几何体（多边形或多重多边形）

            # 使用 rasterio.mask.mask() 执行裁剪操作
            with rasterio.open(tiff_file_path) as src:
                out_image, out_transform = mask(src, geometries, crop=True)  # crop=True 表示裁剪

                # 获取原始数据的 nodata 值
                nodata_value = src.nodata

                # 如果裁剪后的影像包含 NaN 值，替换为 nodata 值
                out_image = np.nan_to_num(out_image, nan=nodata_value)

                # 更新元数据以适应裁剪后的图像
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",  # 设置输出文件格式
                    "height": out_image.shape[1],  # 新的高度
                    "width": out_image.shape[2],   # 新的宽度
                    "transform": out_transform,    # 更新变换矩阵
                    "nodata": nodata_value,        # 设置 nodata 值
                })

                # 保存裁剪后的 TIFF 文件
                output_tiff_path = os.path.join(tiff_output_folder, tiff_file)
                with rasterio.open(output_tiff_path, 'w', **out_meta) as dest:
                    dest.write(out_image)  # 写入裁剪后的数据

                print(f"已裁剪并保存 TIFF 文件: {output_tiff_path}")
