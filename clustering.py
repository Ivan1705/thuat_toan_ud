import numpy as np
from scipy.spatial import distance_matrix
from kruskal import *

def create_clusters(mst, num_clusters):
    mst.sort(key=lambda x: x[2], reverse=True)
    
    for _ in range(num_clusters - 1):
        mst.pop(0)
    
    parent = {}
    rank = {}
    
    for u, v, weight in mst:
        if u not in parent:
            parent[u] = u
            rank[u] = 0
        if v not in parent:
            parent[v] = v
            rank[v] = 0
        union(parent, rank, u, v)
    
    clusters = {}
    for node in parent:
        root = find(parent, node)
        if root not in clusters:
            clusters[root] = []
        clusters[root].append(node)
    
    return clusters.values()

def mst_clustering(data, num_clusters):
    # Tính toán ma trận khoảng cách
    dist_matrix = distance_matrix(data, data)

    # Tạo danh sách cạnh (u, v, weight)
    edges = []
    num_nodes = len(data)
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            edges.append((i, j, dist_matrix[i, j]))

    # Áp dụng thuật toán Kruskal
    mst = kruskal(edges, num_nodes)

    # Chia cụm từ cây khung nhỏ nhất
    clusters = create_clusters(mst, num_clusters)

    return clusters
