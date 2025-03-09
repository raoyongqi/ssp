import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeatur
import os
from matplotlib.colors import LinearSegmentedColormap

# 配置字体
config = {
    "font.family": 'Arial',
    'font.size': 24,
    "mathtext.fontset": 'stix',
    "font.serif": ['SimSun'],
    'font.weight': 'bold'
}
mpl.rcParams.update(config)
mpl.rcParams['axes.unicode_minus'] = False

# 读取 SHP 作为底图
bound_file = gpd.read_file('GS(2020)4619/GS(2020)4619.shp')

# 使用 geopandas 直接读取 shapefile 文件
map_china_path = r'GS(2020)4619\\GS(2020)4619_4326_map.shp'
map_china_gdf = gpd.read_file(map_china_path)

# 打印出 GeoDataFrame 的前几行
print(map_china_gdf.head())

# 用于绘制每个子图的函数
def point_plot(fig, ax, tif_file: str, pre_title: str, i: int):
    # Set the extent of the map (China region)
    ax.set_extent([73.2, 135, 17, 55], crs=ccrs.PlateCarree())  # 设置地图的范围

    # Add features to the map
    ax.add_feature(cfeatur.OCEAN.with_scale('10m'), zorder=2)
    ax.add_feature(cfeatur.LAKES.with_scale('10m'), zorder=2)

    # Plot the boundary file (adjust for CRS)
    bound_file.to_crs("EPSG:4326").plot(ax=ax, color='none', edgecolor='black', linewidth=0.8)

    # Plot China boundaries if available
    if map_china_gdf is not None:
        map_china_gdf.to_crs("EPSG:4326").plot(ax=ax, color='none', edgecolor='blue', linewidth=1)

    # Open the raster file and read the data
    with rasterio.open(tif_file) as src:
        data = src.read(1)
        no_data_value = src.nodata

        # Handle no-data values
        if no_data_value is not None:
            data = np.where(data == no_data_value, np.nan, data)

        # Compute the bounds for the raster
        transform = src.transform
        bounds = [transform * (0, 0), transform * (src.width, src.height)]
        extent = [bounds[0][0], bounds[1][0], bounds[1][1], bounds[0][1]]

        # Get the color range
        vmin, vmax = np.nanmin(data), np.nanmax(data)
        print(f"TIFF 文件 {tif_file} 的最小值: {vmin}, 最大值: {vmax}")

        # Create a custom colormap
        clist = ['blue', 'limegreen', 'orange', 'red']
        newcmap = LinearSegmentedColormap.from_list('mycolmap', clist, N=1024)

        # Plot the raster data with custom colormap
        im = ax.imshow(data, cmap='seismic', interpolation='none', extent=extent, transform=ccrs.PlateCarree(), alpha=1)

        # Create and position the color bar
        cax = fig.add_axes([ax.get_position().x0, ax.get_position().y0 - 0.07, ax.get_position().width, 0.02])
        plt.colorbar(im, cax=cax, orientation='horizontal')

    # Set the main title
    ax.text(0.05, 0.95, f"{chr(97 + i)}", transform=ax.transAxes, fontsize=20, fontweight='bold', color='black', ha='center', va='center')

    # Create the inset map (ax2) within each subplot
    ax2 = fig.add_axes([ax.get_position().x0 + 0.23, ax.get_position().y0, 0.1, 0.1], projection=ccrs.PlateCarree())
    ax2.imshow(data, cmap='seismic', interpolation='none', extent=extent, transform=ccrs.PlateCarree(), alpha=1)

    ax2.set_extent([104.5, 124, 0, 26], crs=ccrs.PlateCarree())
    ax2.add_feature(cfeatur.OCEAN.with_scale('10m'), zorder=2)
    bound_file.to_crs("EPSG:4326").plot(ax=ax2, color='none', edgecolor='black', linewidth=0.8)
    if map_china_gdf is not None:
        map_china_gdf.to_crs("EPSG:4326").plot(ax=ax2, color='none', edgecolor='blue', linewidth=0.8)
    ax2.gridlines(draw_labels=False, linestyle='--', lw=0.3)
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# Create subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 12), subplot_kw={'projection': ccrs.PlateCarree()})

# Adjust spacing between subplots
plt.subplots_adjust(wspace=0.5, hspace=0.3)

# Iterate over axes, tif_files, and titles
tif_files = [
    'cropped_result/tiff/sub_126_rf.tif',
    'cropped_result/tiff/sub_245_rf.tif',
    'cropped_result/tiff/sub_370_rf.tif',
    'cropped_result/tiff/sub_585_rf.tif',
]

for i, (ax, tif_file) in enumerate(zip(axes.flatten(), tif_files), 1):
    point_plot(fig, ax, tif_file, f"Title {i}", i)  # Adjust the title if needed
    
output_dir = 'photo'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, 'multiple_scenario_sub.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()