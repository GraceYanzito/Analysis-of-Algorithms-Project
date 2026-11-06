from testDictionary import travel_data

import heapq
from collections import Counter
from itertools import count
 
from testDictionary import travel_data

def find_all_trails(num_nodes, distance_matrix, max_distance, start_node=0, return_to_start=False):
    """
    Finds and records ALL valid trail paths within the distance constraint,
    allowing full backtracking and re-visiting locations.
    """
    all_trails = []

    def dfs(curr_node, current_distance, current_path):
        # Scenario A: Loop Hike (Must record only when we successfully make it back to start)
        if return_to_start:
            if curr_node == start_node and len(current_path) > 1:
                all_trails.append((current_distance, list(current_path)))
                return # Stop searching further on this branch once loop closes
        else:
            # Scenario B: Point-to-Point (Every single sub-segment explored is a valid route choice)
            if len(current_path) > 1:
                all_trails.append((current_distance, list(current_path)))

        # Explore all connected trails out of the current location
        for next_node in range(num_nodes):
            edge_weight = distance_matrix[curr_node][next_node]
            if edge_weight == 0:
                continue # No road exists
            
            # Distance Budget Check ###### Djikstra ######
            if current_distance + edge_weight <= max_distance:
                current_path.append(next_node)
                dfs(next_node, current_distance + edge_weight, current_path)
                current_path.pop() # Backtrack step for the search tree

    # Kick off the traversal
    dfs(start_node, 0, [start_node])
    
    # Sort the final list so the absolute longest trails appear right at the top
    all_trails.sort(key=lambda x: x[0], reverse=True)
    return all_trails


def build_matrix_from_dict(data):
    nodes = list(data.keys())
    node_to_idx = {name: idx for idx, name in enumerate(nodes)}
    idx_to_node = {idx: name for idx, name in enumerate(nodes)}
    num_nodes = len(nodes)
    matrix = [[0] * num_nodes for _ in range(num_nodes)]
    
    for u_name, properties in data.items():
        u_idx = node_to_idx[u_name]
        for v_name, edge_properties in properties["connections"].items():
            v_idx = node_to_idx[v_name]
            matrix[u_idx][v_idx] = edge_properties["distance"]
            
    return num_nodes, matrix, node_to_idx, idx_to_node


if __name__ == "__main__":
    num_nodes, distance_matrix, name_to_id, id_to_name = build_matrix_from_dict(travel_data)
    
    # Allotted Distance Limit
    my_budget = 18
    starting_location = "Salem"
    start_id = name_to_id[starting_location]
    
    print("=" * 60)
    print(f"TRAIL MENU GENERATOR (Max Distance: {my_budget} miles)")
    print(f"Origin Point: {starting_location}")
    print("=" * 60)

    # 1. Gather and print Point-to-Point routes
    pt_routes = find_all_trails(num_nodes, distance_matrix, my_budget, start_id, return_to_start=False)
    print(f"\n--- Found {len(pt_routes)} Point-to-Point Trails (Longest first) ---")
    for dist, path in pt_routes[:15]:  # Display top 15 to keep console clean; change slice to see more
        readable = [id_to_name[n] for n in path]
        print(f"[{dist:2} miles]: {' -> '.join(readable)}")
    if len(pt_routes) > 15:
        print(f"... and {len(pt_routes) - 15} shorter trail options.")

    # 2. Gather and print Loop routes
    loop_routes = find_all_trails(num_nodes, distance_matrix, my_budget, start_id, return_to_start=True)
    print(f"\n--- Found {len(loop_routes)} Complete Loop Trails (Longest first) ---")
    for dist, path in loop_routes:
        readable = [id_to_name[n] for n in path]
        print(f"[{dist:2} miles]: {' -> '.join(readable)}")
        
        
        
        import heapq
from collections import Counter
from itertools import count

from testDictionary import travel_data


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def dijkstra_to(matrix, target):
    """Shortest distance from every node TO `target` (handles directed matrices
    by running Dijkstra on the transpose)."""
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


def score_route(path, matrix, start_node, history):
    """
    Returns (key, total, new_nodes, fresh_miles, repeat_miles).
    Higher key = more appealing. Compared left to right:
        1. new_nodes    nodes never seen (in this route OR in the user's history)
        2. fresh_miles  miles on trail walked for the first time in this route
        3. -repeat_miles  fewer re-walked miles is better
    """
    seen_nodes, seen_edges = {start_node}, set()
    new_nodes = fresh = repeat = 0
    for u, v in zip(path, path[1:]):
        w = matrix[u][v]
        if v not in seen_nodes:
            seen_nodes.add(v)
            if v not in history:
                new_nodes += 1
        e = frozenset((u, v))
        # an edge is "fresh" if first time in this route and not between two
        # nodes the user has already been to
        if e not in seen_edges and not (u in history and v in history):
            fresh += w
        else:
            repeat += w
        seen_edges.add(e)
    total = fresh + repeat
    return (new_nodes, fresh, -repeat), total, new_nodes, fresh, repeat


# ----------------------------------------------------------------------
# Search
# ----------------------------------------------------------------------
def find_ranked_trails(num_nodes, matrix, max_distance, start_node=0,
                       return_to_start=True, history=None,
                       max_node_visits=2, top_k=25, dedupe_reverse=True):
    """
    DFS over all trails within budget, with three guards against pointless
    wandering, keeping only the top_k most appealing results.

      1. No U-turns (immediately going back where you came from),
         except at a dead end where you have no choice.
      2. Each DIRECTED edge may be walked at most once (an edge can be
         walked once each way, so spurs work but cycling doesn't).
      3. Each node may be visited at most `max_node_visits` times.

    return_to_start=True also prunes with Dijkstra: never step to a node
    if (distance so far + edge + shortest way home) > budget.
    """
    history = set(history or [])
    home = dijkstra_to(matrix, start_node) if return_to_start else None

    neighbors = [[(v, matrix[u][v]) for v in range(num_nodes) if matrix[u][v]]
                 for u in range(num_nodes)]

    node_visits = Counter({start_node: 1})
    used_dir_edges = set()
    path = [start_node]
    heap, tie, seen = [], count(), set()

    def record(dist):
        p = list(path)
        if return_to_start and dedupe_reverse:
            canon = min(tuple(p), tuple(p[::-1]))
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
        dead_end = len(neighbors[curr]) == 1

        # Preferred placement: try never-visited nodes first
        options = sorted(neighbors[curr],
                         key=lambda nw: (node_visits[nw[0]] > 0 or nw[0] in history))

        for nxt, w in options:
            if nxt == prev and not dead_end:
                continue                                  # guard 1
            if (curr, nxt) in used_dir_edges:
                continue                                  # guard 2
            if node_visits[nxt] >= max_node_visits:
                continue                                  # guard 3
            if dist + w > max_distance:
                continue
            if return_to_start and dist + w + home[nxt] > max_distance:
                continue                                  # Dijkstra prune

            used_dir_edges.add((curr, nxt))
            node_visits[nxt] += 1
            path.append(nxt)
            dfs(nxt, dist + w)
            path.pop()
            node_visits[nxt] -= 1
            used_dir_edges.discard((curr, nxt))

    dfs(start_node, 0)
    return sorted(heap, reverse=True)


# ----------------------------------------------------------------------
def build_matrix_from_dict(data):
    nodes = list(data.keys())
    node_to_idx = {name: i for i, name in enumerate(nodes)}
    idx_to_node = {i: name for i, name in enumerate(nodes)}
    n = len(nodes)
    matrix = [[0] * n for _ in range(n)]
    for u_name, props in data.items():
        for v_name, ep in props["connections"].items():
            matrix[node_to_idx[u_name]][node_to_idx[v_name]] = ep["distance"]
    return n, matrix, node_to_idx, idx_to_node


def show(title, results, id_to_name, limit=10):
    print(f"\n--- {title} ---")
    for key, total, _, path, nn, fresh, rep in results[:limit]:
        names = " -> ".join(id_to_name[n] for n in path)
        print(f"[{total:>2} mi | new nodes {nn} | fresh {fresh:>2} | repeat {rep:>2}] {names}")


if __name__ == "__main__":
    n, matrix, name_to_id, id_to_name = build_matrix_from_dict(travel_data)
    budget, origin = 18, "Salem"
    start = name_to_id[origin]

    print("=" * 60)
    print(f"TRAIL MENU (budget {budget} mi, origin {origin})")
    print("=" * 60)

    loops = find_ranked_trails(n, matrix, budget, start, return_to_start=True)
    show("Loop trails, best first", loops, id_to_name)

    # Same search, but the hiker has already been to these places
    been_there = {name_to_id["Overlook"], name_to_id["Falls"]}
    loops2 = find_ranked_trails(n, matrix, budget, start,
                                return_to_start=True, history=been_there)
    show("Loop trails, after visiting Overlook + Falls before", loops2, id_to_name)

    p2p = find_ranked_trails(n, matrix, budget, start, return_to_start=False)
    show("Point-to-point trails, best first", p2p, id_to_name, limit=8)
