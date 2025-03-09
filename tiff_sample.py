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
fig, axes = plt.subplots(2, 2, figsize=(14, 12), subplot_kw={'projection': albers_proj},wspace=0.5, hspace=0.3)
axes = axes.flatten()  
for i, tif_file in enumerate(tif_files):
    ax = axes[i]

    file_name = os.path.basename(tif_file)
    title = os.path.splitext(file_name)[0]

    gdf_geojson.plot(ax=ax, edgecolor='black', facecolor='white', alpha=0.5)

    with rasterio.open(tif_file) as src:
        data = src.read(1)
        no_data_value = src.nodata

        # 将无效值（no_data_value）设置为 NaN
        if no_data_value is not None:
            data = np.where(data == no_data_value, np.nan, data)

        transform = src.transform
        bounds = [transform * (0, 0), transform * (src.width, src.height)]
        extent = [bounds[0][0], bounds[1][0], bounds[1][1], bounds[0][1]]

        vmin, vmax = np.nanmin(data), np.nanmax(data)

        cmap = plt.get_cmap('viridis').reversed()

        im = ax.imshow(data, cmap=cmap, interpolation='none', extent=extent, transform=ccrs.PlateCarree(), alpha=1)


    gridlines = ax.gridlines(draw_labels=False, color='gray', linestyle='--', alpha=0.5)
    gridlines.top_labels = False
    gridlines.right_labels = False

    ax.text(0.05, 0.95, f"{chr(97 + i)}", transform=ax.transAxes, fontsize=20, fontweight='bold', color='black', ha='center', va='center')

    cbar = fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.02, aspect=20,fraction=0.04)  # 控制颜色条的宽高比

plt.tight_layout()

output_dir = 'pic'
output_file_path = f'{output_dir}/all_scenarios_rf.png'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

plt.savefig(output_file_path, dpi=300, bbox_inches='tight')

plt.show()
