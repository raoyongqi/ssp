import os
import rasterio
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from boruta import BorutaPy

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
file_path = 'data/climate_soil.xlsx'  # 替换为你的文件路径
data = pd.read_excel(file_path)
# data.drop(columns=['Province', 'City', 'District'], inplace=True)

data.columns = data.columns.str.lower()

# 找出所有列名中包含下划线的列，并检查前后部分是否相同
data.columns = [col.replace('_resampled', '') if '_resampled' in col else col for col in data.columns]
data.columns = [col.replace('wc2.1_5m_', '') if col.startswith('wc2.1_5m_') else col for col in data.columns]
new_columns = []
for col in data.columns:
    if '_' in col:  # 如果列名中有下划线
        parts = col.split('_')  # 用下划线拆分列名
        if len(parts) > 1 and parts[0] == parts[-1]:  # 如果前后部分相同
            # 将拆分后的第一部分和最后一部分合并
            new_columns.append('_'.join(parts[:1]))  # 取前两个部分作为列名
        elif len(parts) > 2 and parts[1] == parts[-1]:  # 如果前后部分相同
            # 将拆分后的第一部分和最后一部分合并
            new_columns.append('_'.join(parts[:2]))  # 取前两个部分作为列名
        elif len(parts) > 3 and parts[2] == parts[-1]:  # 如果前后部分相同
            # 将拆分后的第一部分和最后一部分合并
            new_columns.append('_'.join(parts[:3]))  # 取前两个部分作为列名
        else:
            new_columns.append(col)  # 否则保留原列名
    else:
        new_columns.append(col)  # 如果没有下划线，直接保留原列名

# 更新 DataFrame 的列名
data.columns = new_columns
# 2. 筛选特征列

# 将所有 'prec_*' 列加总为 MAP
data['MAP'] = data.filter(like='prec_').sum(axis=1)
data['WIND'] = data.filter(like='wind_').mean(axis=1)
data['TMAX'] = data.filter(like='tmax_').mean(axis=1)
data['TMIN'] = data.filter(like='tmin_').mean(axis=1)
data['TAVG'] = data.filter(like='tavg_').mean(axis=1)

data['SRAD'] = data.filter(like='srad_').mean(axis=1)
data['VAPR'] = data.filter(like='vapr_').mean(axis=1)

# 删除 'prec_*' 列
data = data.drop(columns=data.filter(like='prec_').columns)
data = data.drop(columns=data.filter(like='srad_').columns)
data = data.drop(columns=data.filter(like='tmax_').columns)
data = data.drop(columns=data.filter(like='tmin_').columns)
data = data.drop(columns=data.filter(like='tavg_').columns)
data = data.drop(columns=data.filter(like='vapr_').columns)

data = data.drop(columns=data.filter(like='wind_').columns)
data = data.drop(columns=data.filter(like='bio_').columns)
data.columns = data.columns.str.upper()
data = data.drop(columns=['REF_DEPTH', 'LANDMASK', 'ROOTS', 'ISSOIL'])
feature_columns = [col for col in data.columns if col != 'RATIO']


X = data[feature_columns]
y = data['RATIO']  # 目标变量


# 4. 分割数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 5. 初始化并训练随机森林回归模型
rf = RandomForestRegressor(n_estimators=100, random_state=42)

# 6. 使用 Boruta 进行特征选择
feat_selector = BorutaPy(rf, n_estimators='auto',max_iter=10, alpha=0.05, random_state=42, verbose=0)
# # 7. 获取重要特征并选择前17个

feat_selector.fit(X_train.values, y_train.values)
# 按照ranking_的顺序排序特征名
sorted_features = [feature for _, feature in sorted(zip(feat_selector.ranking_, feature_columns))]


X = data[[*sorted_features[:17]]]
y =  data['RATIO']  # 目标变量  # 替换为你的目标变量



# 4. 分割数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. 初始化并训练随机森林回归模型
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# 6. 预测并评估模型
y_pred = rf.predict(X_test)

# 7. 评估模型性能
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)


ssp_scenario = '585'  

tif_folder1 =  os.path.join( 'plus', ssp_scenario)
tif_files = []

tif_files += [os.path.join(tif_folder1, f) for f in os.listdir(tif_folder1) if f.endswith('.tif')]



output_folder = 'result/ssp585'  # 替换为实际输出文件夹路径

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


sorted_features[:17] = [feature.upper() for feature in sorted_features[:17]]
df.columns = df.columns.str.upper()

df = df[[*sorted_features[:17]]]
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
