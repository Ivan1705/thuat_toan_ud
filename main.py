import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances_argmin_min
from clustering import mst_clustering
from mpl_toolkits.mplot3d import Axes3D

# Tải dữ liệu Iris
iris = load_iris()
data = iris.data

# Giảm số chiều xuống 3 để dễ dàng hiển thị trong không gian 3D
pca = PCA(n_components=3)
data_3d = pca.fit_transform(data)

# Hiển thị dữ liệu ban đầu trong không gian 3D
fig = plt.figure(figsize=(12, 6))
ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(data_3d[:, 0], data_3d[:, 1], data_3d[:, 2], c='blue')
ax1.set_title("Dữ liệu ban đầu")

num_clusters = 3
clusters = mst_clustering(data_3d, num_clusters)

# Hiển thị dữ liệu sau khi phân cụm trong không gian 3D
ax2 = fig.add_subplot(122, projection='3d')
colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
for i, cluster in enumerate(clusters):
    cluster_data = data_3d[list(cluster)]
    ax2.scatter(cluster_data[:, 0], cluster_data[:, 1], cluster_data[:, 2], c=colors[i % len(colors)])
ax2.set_title("Dữ liệu sau khi phân cụm thành 3 cụm")

# Tính toán và hiển thị error
error = 0
for i, cluster in enumerate(clusters):
    cluster_data = data_3d[list(cluster)]
    center = np.mean(cluster_data, axis=0)
    distances = np.linalg.norm(cluster_data - center, axis=1)
    cluster_error = np.sum(distances)
    error += cluster_error
    ax2.text(center[0], center[1], center[2], f'Error: {cluster_error:.2f}', color='black', fontsize=12, bbox=dict(facecolor='white', alpha=0.7))

ax2.text2D(0.5, 0.95, f'Tổng Error: {error:.2f}', transform=ax2.transAxes, ha='center', fontsize=14)

plt.show()
