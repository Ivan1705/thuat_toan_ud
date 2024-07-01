"""
Minimum Spanning Tree Clustering
"""
from __future__ import division

import numpy as np

from scipy import sparse
from scipy.sparse.csgraph import minimum_spanning_tree, connected_components
from scipy.sparse.csgraph._validation import validate_graph
from sklearn.utils import check_array

from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.metrics import pairwise_distances


class MSTClustering(BaseEstimator, ClusterMixin):
    def __init__(self, cutoff=None, cutoff_scale=None, min_cluster_size=1,
                 approximate=True, n_neighbors=20,
                 metric='euclidean', metric_params=None):
        self.cutoff = cutoff
        self.cutoff_scale = cutoff_scale
        self.min_cluster_size = min_cluster_size
        self.metric = metric
        self.metric_params = metric_params
        self.approximate = approximate
        self.n_neighbors = n_neighbors

    def fit(self, X, y=None):
        """Fit the clustering model

        Parameters
        ----------
        X : shape = [n_samples, n_features]
        """
        if self.cutoff is None and self.cutoff_scale is None:
            raise ValueError("Must specify either cutoff or cutoff_frac")

        # Compute the distance-based graph G from the points in X
        if self.metric == 'precomputed':
            # Input is already a graph
            self.X_fit_ = None
            # check xem đồ thị X có hợp lệ không
            G = validate_graph(X, directed=True,
                               csr_output=True, dense_output=False,
                               copy_if_sparse=True, null_value_in=np.inf)
        # Kiểm tra X có phải là array hợp lệ không (ma trận sparse của scipy hoặc mảng numpy)
        elif not self.approximate:
            X = check_array(X)
            self.X_fit_ = X
            kwds = self.metric_params or {}
            G = pairwise_distances(X, metric=self.metric, **kwds)
            G = validate_graph(G, directed=True,
                               csr_output=True, dense_output=False,
                               copy_if_sparse=True, null_value_in=np.inf)
        else:
            # generate a sparse graph using n_neighbors of each point
            X = check_array(X)
            self.X_fit_ = X
            n_neighbors = min(self.n_neighbors, X.shape[0] - 1)
            G = kneighbors_graph(X, n_neighbors=n_neighbors,
                                 mode='distance',
                                 metric=self.metric,
                                 metric_params=self.metric_params)

        """Khi đồ thị có trọng số âm, các trọng số = 0 sẽ bị hiểu lầm trong tính toán vì thực chất nó vẫn có trọng số lớn hơn các cạnh âm khác"""
        zero_fillin = G.data[G.data > 0].min() * 1E-8 # tùn gúa trị nhỏ nhất > 0 sau đó nhân với 1e8
        G.data[G.data == 0] = zero_fillin # thay các giá trị 0 bằng giá trị rất nhỏ

        # Thuật toán Kruskal xây dựng MST của scipy
        self.full_tree_ = minimum_spanning_tree(G, overwrite=True)

        # trả lại các giá tri 0
        self.full_tree_[self.full_tree_ == zero_fillin] = 0

        N = G.shape[0] - 1 # số cạnh trong MST
        if self.cutoff is None: # giữ nguyên
            i_cut = N
        elif 0 <= self.cutoff < 1:
            i_cut = int((1 - self.cutoff) * N)
        elif self.cutoff >= 1:
            i_cut = int(N - self.cutoff)
        else: # cutoff < 0 là không hợp lệ
            raise ValueError('self.cutoff must be positive, not {0}'
                             ''.format(self.cutoff))

        N = len(self.full_tree_.data) # số cạnh trong MST
        if i_cut < 0: # Không cắt cạnh nào
            mask = np.ones(N, dtype=bool) # mask của tất cả các cạnh là True
        elif i_cut >= N: # số cạnh cần cắt lơn hơn hoặc bằng số cạnh MST
            mask = np.zeros(N, dtype=bool) # mask toàn bộ = false
        else:
            mask = np.ones(N, dtype=bool)
            part = np.argpartition(self.full_tree_.data, i_cut) # Lấy i_cut các cạnh nhỏ nhất của cây
            mask[part[:i_cut]] = False # cạnh bị cắt = false

        # Cắt cạnh có trọng số lớn hơn cutoff_scale
        if self.cutoff_scale is not None:
            mask |= (self.full_tree_.data > self.cutoff_scale)

        # Trim the tree
        cluster_graph = self.full_tree_.copy()

        original_data = cluster_graph.data # Lưu trọng số gốc lại
        cluster_graph.data = np.arange(1, len(cluster_graph.data) + 1) # Đổi giá trị trọng số để tính không bị nhầm với giá trị gốc
        cluster_graph.data[mask] = 0 # Các cạnh cần cắt trọng số = 0
        cluster_graph.eliminate_zeros() # Bỏ các cạnh trọng số = 0 đi
        cluster_graph.data = original_data[cluster_graph.data.astype(int) - 1] # Khôi phục trọng số gốc theo index

        # n_components lưu số lượng thành phần liên thông, labels lưu nhãn của từng đỉnh thuộc tplt nào
        n_components, labels = connected_components(cluster_graph,
                                                    directed=False)

        # bỏ các nhóm có kích thước nhỏ hơn min_cluster_size
        counts = np.bincount(labels)
        to_remove = np.where(counts < self.min_cluster_size)[0]

        if len(to_remove) > 0:
            for i in to_remove:
                labels[labels == i] = -1
            _, labels = np.unique(labels, return_inverse=True)
            labels -= 1  # keep -1 labels the same

        # update cluster_graph by eliminating non-clusters
        # operationally, this means zeroing-out rows & columns where
        # the label is negative.
        I = sparse.eye(len(labels))
        I.data[0, labels < 0] = 0

        # we could just do this:
        #   cluster_graph = I * cluster_graph * I
        # but we want to be able to eliminate the zeros, so we use
        # the same indexing trick as above
        original_data = cluster_graph.data
        cluster_graph.data = np.arange(1, len(cluster_graph.data) + 1)
        cluster_graph = I * cluster_graph * I
        cluster_graph.eliminate_zeros()
        cluster_graph.data = original_data[cluster_graph.data.astype(int) - 1]

        self.labels_ = labels
        self.cluster_graph_ = cluster_graph
        return self
    

    def get_graph_segments(self, full_graph=False):
        if not hasattr(self, 'X_fit_'):
            raise ValueError("Must call fit() before get_graph_segments()")
        if self.metric == 'precomputed':
            raise ValueError("Cannot use ``get_graph_segments`` "
                             "with precomputed metric.")

        n_samples, n_features = self.X_fit_.shape

        if full_graph:
            G = sparse.coo_matrix(self.full_tree_)
        else:
            G = sparse.coo_matrix(self.cluster_graph_)

        return tuple(np.vstack(arrs) for arrs in zip(self.X_fit_[G.row].T,
                                                     self.X_fit_[G.col].T))