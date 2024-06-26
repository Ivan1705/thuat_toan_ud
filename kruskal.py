# parent[i] là cha của i
def find(parent, i): 
    if parent[i] == i:
        return i
    else: 
        parent[i] = find(parent, parent[i])
        return parent[i]

def union(parent, rank, x, y):
    root_x = find(parent, x)
    root_y = find(parent, y)

    if root_x != root_y:
        if rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        elif rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        else:
            parent[root_y] = root_x
            rank[root_x] += 1
        return True
    return False

def kruskal(edges, num_nodes):
    edges.sort(key=lambda x: x[2])

    parent = [i for i in range(num_nodes)]
    rank = [0] * num_nodes

    mst = []

    # print(rank)

    for edge in edges:
        u, v, weight = edge
        if union(parent, rank, u, v):
            mst.append(edge)
    
    return mst

edges = [
    (0, 1, 12),
    (0, 2, 4),
    (1, 2, 1),
    (1, 3, 5),
    (1, 4, 3),
    (2, 4, 2),
    (3, 4, 3),
    (3, 5, 10),
    (4, 5, 8)
]

num_nodes = 6
mst = kruskal(edges, num_nodes)

for edge in mst:
    u, v, weight = edge
    print(f"({u}, {v}) voi trong so {weight}")