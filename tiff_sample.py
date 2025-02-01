import matplotlib.pyplot as plt
import numpy as np
import rasterio
import geopandas as gpd
import cartopy.crs as ccrs
import os

# 定义 Albers 投影坐标系
albers_proj = ccrs.AlbersEqualArea(
    central_longitude=105,
    central_latitude=35,
    standard_parallels=(25, 47)
)

# 读取 GeoJSON 数据
geojson_file_path = '中华人民共和国.json'
gdf_geojson = gpd.read_file(geojson_file_path)

# 转换 GeoJSON 数据的坐标系到自定义投影坐标系
if gdf_geojson.crs != albers_proj:
    gdf_geojson = gdf_geojson.to_crs(albers_proj)

# 定义要绘制的 TIFF 文件路径
tif_files = [
    'cropped_result/tiff/predicted_126_rf.tif',
    'cropped_result/tiff/predicted_245_rf.tif',
    'cropped_result/tiff/predicted_370_rf.tif',
    'cropped_result/tiff/predicted_585_rf.tif'
]
# 创建绘图对象和子图
fig, axes = plt.subplots(2, 2, figsize=(14, 12), subplot_kw={'projection': albers_proj},wspace=0.5, hspace=0.3)
axes = axes.flatten()  # 将 2x2 的子图数组展平为 1D 数组

for i, tif_file in enumerate(tif_files):
    ax = axes[i]

    # 提取文件名作为标题
    file_name = os.path.basename(tif_file)
    title = os.path.splitext(file_name)[0]

    # 绘制 GeoJSON 数据
    gdf_geojson.plot(ax=ax, edgecolor='black', facecolor='white', alpha=0.5)

    # 读取并绘制 TIFF 数据
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
        cmap = plt.get_cmap('viridis').reversed()

        # 绘制栅格数据
        im = ax.imshow(data, cmap=cmap, interpolation='none', extent=extent, transform=ccrs.PlateCarree(), alpha=1)

    # 添加标题

    # 添加经纬度网格线
    gridlines = ax.gridlines(draw_labels=False, color='gray', linestyle='--', alpha=0.5)
    gridlines.top_labels = False
    gridlines.right_labels = False

    # 在左上角添加 "a", "b", "c", "d"
    ax.text(0.05, 0.95, f"{chr(97 + i)}", transform=ax.transAxes, fontsize=20, fontweight='bold', color='black', ha='center', va='center')

    # 添加每个子图的颜色条
    cbar = fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.02, aspect=20,fraction=0.04)  # 控制颜色条的宽高比

# 调整整体布局
plt.tight_layout()

# 保存图形到文件
output_dir = 'pic'
output_file_path = f'{output_dir}/all_scenarios_rf.png'

# 检查目录是否存在，如果不存在则创建
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

plt.savefig(output_file_path, dpi=300, bbox_inches='tight')

# 显示图形
plt.show()
