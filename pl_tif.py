import matplotlib.pyplot as plt
import numpy as np
import rasterio
import geopandas as gpd
import cartopy.crs as ccrs
import os
from matplotlib.colors import LinearSegmentedColormap

# 定义 Albers 投影坐标系
albers_proj = ccrs.AlbersEqualArea(
    central_longitude=105,
    central_latitude=35,
    standard_parallels=(25, 47)
)

# 创建绘图对象
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': albers_proj})

# 读取 GeoJSON 数据
geojson_file_path = 'data/中华人民共和国.json'
gdf_geojson = gpd.read_file(geojson_file_path)

# 转换 GeoJSON 数据的坐标系到自定义投影坐标系
if gdf_geojson.crs != albers_proj:
    gdf_geojson = gdf_geojson.to_crs(albers_proj)

# 绘制 GeoJSON 数据
gdf_geojson.plot(ax=ax, edgecolor='black', facecolor='white', alpha=0.5, label='GeoJSON Data')

# 读取并绘制 TIFF 数据
tif_file = 'cropped_data/result/sub_rf.tif'

# 提取文件名作为标题
file_name = os.path.basename(tif_file)
title = os.path.splitext(file_name)[0]

with rasterio.open(tif_file) as src:
    data = src.read(1)
    no_data_value = src.nodata
    
    # 将无效值（no_data_value）设置为 NaN
    if no_data_value is not None:
        data = np.where(data == no_data_value, np.nan, data)
    
    # 计算图像的仿射变换矩阵和坐标
    transform = src.transform
    bounds = [transform * (0, 0), transform * (src.width, src.height)]
    extent = [bounds[0][0], bounds[1][0], bounds[1][1], bounds[0][1]]
    
    # 获取最大值和最小值
    vmin, vmax = np.nanmin(data), np.nanmax(data)
    print(f"TIFF 文件 {tif_file} 的最小值: {vmin}")
    print(f"TIFF 文件 {tif_file} 的最大值: {vmax}")
    
    # 自定义颜色映射：从蓝色到绿色再到红色
    colors = ["blue", "green", "red"]
    cmap = LinearSegmentedColormap.from_list("blue_green_red", colors)

    # 绘制栅格数据
    im = ax.imshow(data, cmap=cmap, interpolation='none', extent=extent, transform=ccrs.PlateCarree(), alpha=1)
    
    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05)
    cbar.set_label('Pixel Value')

# 添加标题
plt.title(f'{title}')

# 设置坐标轴标签
ax.set_xlabel('Easting (meters)')
ax.set_ylabel('Northing (meters)')

# 添加经纬度网格线
gridlines = ax.gridlines(draw_labels=True, color='gray', linestyle='--', alpha=0.5)
gridlines.xlabel_style = {'size': 10}
gridlines.ylabel_style = {'size': 10}
# 隐藏右边和上边的网格线标签
gridlines.top_labels = False
gridlines.right_labels = False

# 保存图形到文件
output_file_path = f'data/{title}.png'
plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
output_file_path = f'data/{title}.png'
plt.savefig(output_file_path, dpi=300, bbox_inches='tight')

# 显示图形
plt.show()
