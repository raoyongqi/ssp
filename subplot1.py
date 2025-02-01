import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

# 创建一个 figure 对象
fig = plt.figure(figsize=(8, 6))

# 使用 GridSpec 创建 2x2 网格布局
gs = gridspec.GridSpec(2, 2, figure=fig)

# 创建子图 1, 将其占据第一行第一列
ax1 = fig.add_subplot(gs[0, 0])  # gs[row, col]
data1 = np.random.rand(10, 10)
cax1 = ax1.imshow(data1, cmap='viridis')
ax1.set_title('Subplot 1')

# 创建子图 2, 将其占据第一行第二列
ax2 = fig.add_subplot(gs[0, 1])
data2 = np.random.rand(10, 10)
cax2 = ax2.imshow(data2, cmap='viridis')
ax2.set_title('Subplot 2')

# 创建子图 3, 将其占据第二行第一列
ax3 = fig.add_subplot(gs[1, 0])
data3 = np.random.rand(10, 10)
cax3 = ax3.imshow(data3, cmap='viridis')
ax3.set_title('Subplot 3')

# 为每个子图添加颜色条
fig.colorbar(cax1, ax=ax1, orientation='horizontal', pad=0.05)
fig.colorbar(cax2, ax=ax2, orientation='horizontal', pad=0.05)
fig.colorbar(cax3, ax=ax3, orientation='horizontal', pad=0.05)

# 调整布局
plt.tight_layout()
plt.show()
