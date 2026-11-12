import heapq
from collections import Counter
from itertools import count
from testDictionary import trail_data
import time
start_total = time.perf_counter()


# ----------------------------------------------------------------------
# Graph & Matrix Helpers
# ----------------------------------------------------------------------
def build_matrix_from_dict(data):
    """Builds an adjacency matrix and ID maps from the travel data dictionary."""
    nodes = list(data.keys())
    node_to_idx = {name: i for i, name in enumerate(nodes)}
    idx_to_node = {i: name for i, name in enumerate(nodes)}
    n = len(nodes)
    matrix = [[0] * n for _ in range(n)]

    for u_name, props in data.items():
        for v_name, ep in props.get("connections", {}).items():
            if v_name in node_to_idx:
                matrix[node_to_idx[u_name]][node_to_idx[v_name]] = ep["distance"]

    return n, matrix, node_to_idx, idx_to_node


def dijkstra_to(matrix, target):
    """Shortest distance from every node TO `target` (handles directed matrices)."""
    n = len(matrix)
    rev = list(zip(*matrix))
    dist = [float("inf")] * n
    dist[target] = 0
    pq = [(0, target)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v in range(n):
            w = rev[u][v]
            if w and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))

    return dist


# ----------------------------------------------------------------------
# Scoring & Advanced Search
# ----------------------------------------------------------------------
def score_route(path, matrix, start_node, history):
    """Returns scoring metrics for evaluating the quality of a trail."""
    seen_nodes, seen_edges = {start_node}, set()
    new_nodes = fresh = repeat = 0

    for u, v in zip(path, path[1:]):
        w = matrix[u][v]
        if v not in seen_nodes:
            seen_nodes.add(v)
            if v not in history:
                new_nodes += 1

        e = frozenset((u, v))
        if e not in seen_edges and not (u in history and v in history):
            fresh += w
        else:
            repeat += w
        seen_edges.add(e)

    total = fresh + repeat
    return (new_nodes, fresh, -repeat), total, new_nodes, fresh, repeat


def find_ranked_trails(
    num_nodes,
    matrix,
    max_distance,
    start_node=0,
    return_to_start=True,
    history=None,
    max_node_visits=2,
    top_k=25,
    dedupe_reverse=True,
):
    """DFS over all trails within budget with optimized pruning rules."""
    history = set(history or [])
    home = dijkstra_to(matrix, start_node) if return_to_start else None
    neighbors = [
        [(v, matrix[u][v]) for v in range(num_nodes) if matrix[u][v]]
        for u in range(num_nodes)
    ]

    node_visits = Counter({start_node: 1})
    used_dir_edges = set()
    path = [start_node]
    heap, tie, seen = [], count(), set()

    def record(dist):
        p = list(path)
        if return_to_start and dedupe_reverse:
            rev_p = p[::-1]
            # Only treat reverse as identical if all reverse edges exist with equal weight
            rev_valid = all(
                matrix[u][v] == matrix[v][u] and matrix[u][v] > 0
                for u, v in zip(rev_p, rev_p[1:])
            )
            canon = min(tuple(p), tuple(rev_p)) if rev_valid else tuple(p)
            if canon in seen:
                return
            seen.add(canon)

        key, total, nn, fresh, rep = score_route(p, matrix, start_node, history)
        item = (key, total, next(tie), p, nn, fresh, rep)

        if len(heap) < top_k:
            heapq.heappush(heap, item)
        elif item[:2] > heap[0][:2]:
            heapq.heapreplace(heap, item)

    def dfs(curr, dist):
        if return_to_start:
            if curr == start_node and len(path) > 1:
                record(dist)
                return
        elif len(path) > 1:
            record(dist)

        prev = path[-2] if len(path) > 1 else None
        is_true_dead_end = (
            prev is not None
            and len(neighbors[curr]) == 1
            and neighbors[curr][0][0] == prev
        )

        options = sorted(
            neighbors[curr],
            key=lambda nw: (node_visits[nw[0]] > 0 or nw[0] in history),
        )

        for nxt, w in options:
            if nxt == prev and not is_true_dead_end:
                continue
            if (curr, nxt) in used_dir_edges:
                continue
            if node_visits[nxt] >= max_node_visits:
                continue
            if dist + w > max_distance:
                continue
            if return_to_start and dist + w + home[nxt] > max_distance:
                continue

            used_dir_edges.add((curr, nxt))
            node_visits[nxt] += 1
            path.append(nxt)

            dfs(nxt, dist + w)

            path.pop()
            node_visits[nxt] -= 1
            used_dir_edges.discard((curr, nxt))

    dfs(start_node, 0)
    return sorted(heap, reverse=True)


def show(title, results, id_to_name, limit=10):
    print(f"\n--- {title} ---")
    if not results:
        print("No trails found within budget.")
        return
    for key, total, _, path, nn, fresh, rep in results[:limit]:
        names = " -> ".join(id_to_name[n] for n in path)
        print(
            f"[{total:>5.1f} mi | new nodes {nn} | fresh {fresh:>5.1f} | repeat {rep:>5.1f}] {names}"
        )


# ----------------------------------------------------------------------
# Single Execution Entry Point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    n, matrix, name_to_id, id_to_name = build_matrix_from_dict(trail_data)
    budget, origin = 25, "Trail_5"

    if origin not in name_to_id:
        raise ValueError(f"Origin '{origin}' not found in travel_data.")

    start = name_to_id[origin]

    print("=" * 60)
    print(f"TRAIL MENU (budget {budget} mi, origin {origin})")
    print("=" * 60)

    # 1. Standard Loop Trails
    loops = find_ranked_trails(n, matrix, budget, start, return_to_start=True)
    show("Loop trails, best first", loops, id_to_name)

    # 2. Loop Trails with History
    history_names = ["Overlook", "Falls"]
    been_there = {name_to_id[name] for name in history_names if name in name_to_id}
    loops2 = find_ranked_trails(
        n, matrix, budget, start, return_to_start=True, history=been_there
    )
    show(
        f"Loop trails, after visiting {', '.join(history_names)} before",
        loops2,
        id_to_name,
    )

    # 3. Point-to-Point Trails
    p2p = find_ranked_trails(n, matrix, budget, start, return_to_start=False)
    show("Point-to-point trails, best first", p2p, id_to_name, limit=8)

    end_total = time.perf_counter()
    print(f"\nTotal process time: {end_total - start_total:.4f} seconds")
