import os
import rasterio
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from boruta import BorutaPy
from sklearn.ensemble import GradientBoostingRegressor

# 读取tif文件并提取数据和元数据，包括经纬度信息
def read_tif_with_coords(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1)  # 读取第一波段的数据
        profile = src.profile
        transform = src.transform  # 获取仿射变换信息
        width = src.width
        height = src.height

        # 生成所有像素的行列号
        rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

        # 将行列号转换为地理坐标（经纬度）
        xs, ys = rasterio.transform.xy(transform, rows, cols)


    return data, profile, np.array(xs), np.array(ys)

# 保存预测结果为tif文件

# 获取特征名称
def get_feature_name(file_name):
    base_name = os.path.basename(file_name)
    feature_name = base_name.replace('cropped_', '').replace('.tif', '')
    return feature_name

# 1. 读取Excel文件
file_path = "C:/Users/r/Desktop/bayes/data/selection.csv"  # 替换为你的文件路径


data = pd.read_csv(file_path)

data.rename(columns={'MAX_MAT': 'TMAX', 'MIN_MAT': 'TMIN', 'AVG_MAT': 'TAVG'}, inplace=True)

print(data.columns)

feature_columns = [col for col in data.columns if col != 'RATIO']

X = data[feature_columns]

y = data['RATIO']  # 目标变量

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf = GradientBoostingRegressor(n_estimators=100, random_state=42)
# 4. 分割数据集为训练集和测试集


# 6. 预测并评估模型
y_pred = rf.predict(X_test)

# 7. 评估模型性能
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)


ssp_scenario = '245'  

tif_folder1 =  os.path.join( 'plus', ssp_scenario)

tif_files = []

tif_files += [
    os.path.join(tif_folder1, f) 
    for f in os.listdir(tif_folder1) 
    if f.endswith('.tif') and any(f.startswith(col) for col in data.columns)
]


output_folder = 'result'  # 替换为实际输出文件夹路径

data_list = []
profiles = []

for i, file in enumerate(tif_files):
    data, profile, xs, ys = read_tif_with_coords(file)
    data_list.append(data)
    profiles.append(profile)
    if "elev" in file:  # 根据文件名判断
        print(f"Elev data is from file: {file}")
    if i == 0:  # 只保存第一个tif的经纬度信息
        lons, lats = xs, ys

# 将数据和经纬度转换为二维数组
data_stack = np.stack(data_list, axis=-1)
rows, cols, bands = data_stack.shape
data_2d = data_stack.reshape((rows * cols, bands))

# 添加经纬度信息作为特征
coords_2d = np.stack((lons.flatten(), lats.flatten()), axis=1)
data_with_coords = np.hstack((coords_2d, data_2d))

# 将数据转换为DataFrame
feature_names = ['LON', 'LAT'] + [get_feature_name(f) for f in tif_files]
df = pd.DataFrame(data_with_coords, columns=feature_names)

# 调整数据框的列顺序以匹配模型的特征顺序
model_feature_names = feature_columns

print(df.isin([np.inf, -np.inf]).sum())  # 检查是否有无穷大值
print(df.isna().sum())  # 检查是否有缺失值

df[['MAP']] = df[['MAP']].clip(lower=0)

# 进行预测
y_pred = rf.predict(df)

# 将预测结果转换为二维数组
y_pred_2d = y_pred.reshape((rows, cols))

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)
def save_tif(file_path, data, profile):
    with rasterio.open(file_path, 'w', **profile) as dst:
        dst.write(data, 1)

# 保存预测结果为tif文件
model_name = 'data/pl'  # 模型名称或自定义的名称
output_file = os.path.join(output_folder, f'predicted_{ssp_scenario}_rf.tif')
save_tif(output_file, y_pred_2d, profiles[0])

print(f"预测结果已保存到 {output_file}")
