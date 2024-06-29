#include "bits/stdc++.h"
using namespace std;
#define fi first
#define se second

const int N = 1e5 + 5;
const int INF = 1e9;

// Khai báo đồ thị. g[u] chứa các cạnh nối với đỉnh u. Các cạnh sẽ được lưu dưới dạng pair<v,c>
int n, m;
vector<pair<int, int>> g[N];

int dis[N]; // Mảng d lưu khoảng cách của toàn bộ đỉnh
int parent[N]; // Mảng lưu cha của mỗi đỉnh trong cây khung

void prim(int s) { // Thuật toán Prim bắt đầu chạy từ đỉnh nguồn s
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> q;

    // Khởi tạo khoảng cách của các đỉnh là vô cùng lớn
    for (int i = 1; i <= n; i++) {
        dis[i] = INF;
        parent[i] = -1;
    }

    // Khởi tạo đỉnh nguồn có khoảng cách là 0 và push đỉnh này vào
    dis[s] = 0;
    q.push({0, s});

    while (!q.empty()) {
        auto top = q.top(); q.pop();
        int curDis = top.fi; int u = top.se;

        if (curDis != dis[u]) continue;

        // Kết nạp đỉnh u vào cây khung
        dis[u] = -INF;

        // Cập nhật khoảng cách cho các đỉnh kề u
        for (auto &e : g[u]) {
            int v = e.fi; int c = e.se;
            if (dis[v] > c) {
                dis[v] = c;
                parent[v] = u;
                q.push({dis[v], v});
            }
        }
    }
}

int main() {
    // Số đỉnh và số cạnh
    n = 4;
    m = 5;

    // Dữ liệu các cạnh
    vector<tuple<int, int, int>> inputEdges = {
        {1, 2, 1},
        {1, 3, 3},
        {1, 4, 4},
        {2, 3, 2},
        {3, 4, 5}
    };

    // Đọc các cạnh từ dữ liệu có sẵn và lưu vào vector g
    for (const auto& [u, v, c] : inputEdges) {
        g[u].push_back({v, c});
        g[v].push_back({u, c});
    }

    prim(1);

    cout << "Cac canh cua Cay bao trum nho nhat:\n";
    for (int v = 2; v <= n; v++) { // Bắt đầu từ 2 vì 1 là đỉnh gốc
        if (parent[v] != -1) {
            cout << parent[v] << " - " << v << " : ";
            for (auto &edge : g[v]) {
                if (edge.fi == parent[v]) {
                    cout << edge.se << endl;
                    break;
                }
            }
        }
    }

    return 0;
}
