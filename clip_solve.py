import os
import rasterio
from rasterio.mask import mask
import numpy as np
import geopandas as gpd
import platform
if platform.system() == "Windows":
    # Windows 环境的文件路径
    base_path = r'C:\Users\r\Desktop\ssp'
else:
    # Linux 环境的文件路径
    base_path = '/home/r/Desktop/r-climate'
geojson_file_path = '中华人民共和国分市.json'  # 请确保这个文件路径正确
gdf_geojson = gpd.read_file(geojson_file_path)

import pandas as pd

# Read the Excel file
df = pd.read_csv('data/climate_soil_loc.csv')  # Replace with the path to your Excel file

# Get the unique cities from the "City" column
unique_cities = df['City'].unique()

filtered_gdf = gdf_geojson[gdf_geojson['name'].isin(unique_cities)]
print(gdf_geojson['name'])

# from shapely import MultiPolygon

# from shapely.ops import unary_union

# filtered_gdf['geometry'] = filtered_gdf['geometry'].apply(
#     lambda geom: unary_union(geom) if isinstance(geom, MultiPolygon) else geom
# )

# 输入文件夹列表
if platform.system() == "Windows":
    tiff_folders = [
        r'C:\Users\r\Desktop\ssp\result',
    ]
else:
    tiff_folders = [
        '/home/r/Desktop/r-climate/data/result/',
    ]


    
# 指定输出文件夹路径
geojson_output_folder = os.path.join(base_path, 'data', 'cropped_result', 'geojson')
tiff_output_folder = os.path.join(base_path, 'data', 'cropped_result', 'tiff')
# 创建输出文件夹（如果不存在）
os.makedirs(geojson_output_folder, exist_ok=True)
os.makedirs(tiff_output_folder, exist_ok=True)

# 遍历 TIFF 文件夹列表中的每个文件夹
import os
import rasterio
import numpy as np
from rasterio.mask import mask
from shapely.geometry import Polygon, MultiPolygon

# 遍历每个 TIFF 文件所在的文件夹
import os
import rasterio
import numpy as np
from rasterio.mask import mask
from shapely.geometry import Polygon
import geopandas as gpd

# 假设已加载过滤后的GeoDataFrame（filtered_gdf）
# 假设 filtered_gdf 已经被定义，并且其包含了一个 'geometry' 列（每个几何对象为 Polygon 或 MultiPolygon）

# 遍历每个 TIFF 文件所在的文件夹
for tiff_folder in tiff_folders:
    if not os.path.isdir(tiff_folder):
        print(f"Folder does not exist: {tiff_folder}")
        continue

    # 使用 os.walk 遍历子文件夹和文件
    for root, dirs, files in os.walk(tiff_folder):
        for tiff_file in files:
            # 检查文件是否是 .tif 文件，并且文件名包含 'sub'
            if tiff_file.endswith('.tif') and 'sub' in tiff_file:
                tiff_path = os.path.join(root, tiff_file)  # 获取文件的完整路径
                
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
                            out_image, out_transform = mask(dataset, filtered_gdf.geometry, crop=True, nodata=np.nan)

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
                                dest.write(out_image[0], 1)  # out_image[0] 是二维数组

                # 将 GeoJSON 中的值更新为裁剪后的 TIFF 中的值
                with rasterio.open(tiff_output_path) as cropped_src:
                    for idx, row in filtered_gdf.iterrows():
                        geom = row['geometry']
                        if geom.is_empty:
                            continue

                        # 如果是 MultiPolygon，提取其中的每个 Polygon
                        polygons = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)

                        # 存储每个 Polygon 的像素值
                        all_pixel_values = []

                        # 遍历每个 Polygon
                        for poly in polygons:
                            # 提取 Polygon 的外部边界
                            coords = np.array(poly.exterior.coords)

                            # 将几何体转换为 TIFF 窗口坐标
                            pixel_coords = [cropped_src.index(x, y) for x, y in coords]

                            # 计算区域的像素值
                            for row, col in pixel_coords:
                                if 0 <= row < cropped_src.height and 0 <= col < cropped_src.width:
                                    pixel_value = cropped_src.read(1)[row, col]
                                    if not np.isnan(pixel_value):
                                        all_pixel_values.append(pixel_value)

                        # 计算平均值
                        if all_pixel_values:
                            avg_value = np.nanmean(all_pixel_values)  # 使用平均值来代表区域
                            filtered_gdf.at[idx, 'value'] = avg_value
                        else:
                            filtered_gdf.at[idx, 'value'] = np.nan  # 如果没有有效值，则设置为 NaN
