#include <bits/stdc++.h>
using namespace std;

// Cấu trúc để lưu các cạnh đồ thị
struct Edge {
    int u, v, c; //biến u, v lưu đỉnh đầu và đỉnh cuối của cạnh, c lưu trọng số của cạnh
    Edge(int _u, int _v, int _c): u(_u), v(_v), c(_c) {}; //constructor
};

// Disjoint Set
struct Dsu {
    vector<int> par;

    void init(int n) {
        par.resize(n + 1);
        iota(par.begin(), par.end(), 0); // Khởi tạo par[i] = i(khởi tọa mỗi phần tử là cha của chính nó)
    }

    int find(int u) {
        if (par[u] != u)
            par[u] = find(par[u]); // Path compression
        return par[u];
    }

    bool join(int u, int v) {
        u = find(u); v = find(v);
        if (u == v) return false;
        par[v] = u;
        return true;
    }
};

// n và m là số đỉnh và số cạnh
// totalWeight là tổng trọng số các cạnh trong cây khung nhỏ nhất
int n, m, totalWeight = 0;
vector<Edge> edges;

int main() {
    // Số đỉnh và số cạnh
    n = 6;
    m = 8;

    // Dữ liệu các cạnh
    vector<tuple<int, int, int>> inputEdges = {
        {0, 1, 5},
        {0, 2, 6},
        {1, 2, 1},
        {1, 3, 3},
        {1, 4, 1},
        {2, 3, 2},
        {3, 4, 7},
        {4, 5, 2}
    };

    // Đọc các cạnh từ dữ liệu có sẵn và lưu vào vector edges
    for (const auto& [u, v, c] : inputEdges) {
        edges.push_back(Edge(u, v, c));
    }

    // Khởi tạo Disjoint Set Union (DSU)
    Dsu dsu;
    dsu.init(n);

    // Sắp xếp lại các cạnh theo trọng số tăng dần
    sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
        return a.c < b.c;
    });

    // Vector lưu trữ các cạnh của cây bao trùm nhỏ nhất
    vector<Edge> minSpanningTree;

    // Duyệt qua các cạnh theo thứ tự đã sắp xếp
    for (const Edge& e : edges) {
        // Nếu không hợp nhất được 2 đỉnh u và v thì bỏ qua
        if (dsu.join(e.u, e.v)) {
            // Thêm cạnh này vào cây bao trùm nhỏ nhất
            minSpanningTree.push_back(e);
            // Cập nhật tổng trọng số của cây bao trùm nhỏ nhất
            totalWeight += e.c;
        }
    }

    // In ra các cạnh của cây bao trùm nhỏ nhất
    cout << "Cac canh cua Cay bao trum nho nhat:\n";
    for (const Edge& e : minSpanningTree) {
        cout << e.u << " - " << e.v << " : " << e.c << "\n";
    }

    return 0;
}