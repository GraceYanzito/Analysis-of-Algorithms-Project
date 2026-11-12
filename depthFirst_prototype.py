import argparse
import heapq
import time
from collections import Counter
from itertools import count

from testDictionary import trail_data


# ----------------------------------------------------------------------
# Graph & Matrix Helpers
# ----------------------------------------------------------------------
def build_matrix_from_dict(data):
    """Builds an adjacency matrix and ID maps from the trail data dictionary."""
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


def validate_graph(data):
    """Returns a list of human-readable warnings about likely data-entry problems."""
    warnings = []
    for u, props in data.items():
        for v, ep in props.get("connections", {}).items():
            if v == u:
                warnings.append(f"{u} has a self-loop ({ep['distance']} mi).")
            elif v not in data:
                warnings.append(f"{u} -> {v}: '{v}' is not defined, edge is ignored.")
            else:
                back = data[v].get("connections", {}).get(u)
                if back is None:
                    warnings.append(f"{u} -> {v} is one-way (no edge back).")
                elif back["distance"] != ep["distance"] and u < v:
                    warnings.append(
                        f"{u} <-> {v} distances differ "
                        f"({ep['distance']} vs {back['distance']} mi)."
                    )
    return warnings


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


def all_pairs_from(matrix):
    """sp[u][v] = shortest distance from u to v (directed)."""
    matrix_t = [list(r) for r in zip(*matrix)]
    return [dijkstra_to(matrix_t, u) for u in range(len(matrix))]


# ----------------------------------------------------------------------
# Scoring & Search
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
    prune=True,
    max_expansions=None,
    time_limit=None,
):
    """
    DFS over trails within budget, ranked by (new nodes, fresh miles, -repeat miles).

    prune           Branch-and-bound: skip branches that cannot reach as many new
                    nodes as the current k-th best route. Exact (same results).
    max_expansions  Stop after this many DFS calls. Approximate if it triggers.
    time_limit      Stop after this many seconds. Approximate if it triggers.

    Returns (results, stats). stats["truncated"] is True if a cap stopped the search.
    """
    history = set(history or [])
    home = dijkstra_to(matrix, start_node) if return_to_start else None
    sp = all_pairs_from(matrix) if prune else None
    neighbors = [
        [(v, matrix[u][v]) for v in range(num_nodes) if matrix[u][v]]
        for u in range(num_nodes)
    ]

    node_visits = Counter({start_node: 1})
    used_dir_edges = set()
    path = [start_node]
    heap, tie, seen = [], count(), set()
    deadline = time.perf_counter() + time_limit if time_limit else None
    stats = {"calls": 0, "pruned": 0, "truncated": False}

    def record():
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

    def out_of_budget():
        if max_expansions is not None and stats["calls"] > max_expansions:
            return True
        if deadline is not None and stats["calls"] % 1024 == 0:
            return time.perf_counter() > deadline
        return False

    def dfs(curr, dist, new_cnt):
        stats["calls"] += 1
        if stats["truncated"] or out_of_budget():
            stats["truncated"] = True
            return

        if return_to_start:
            if curr == start_node and len(path) > 1:
                record()
                return
        elif len(path) > 1:
            record()

        # Branch-and-bound: best case is every still-reachable unvisited node is new.
        # Strict "<" keeps ties alive, so ranking is unchanged.
        if prune and len(heap) == top_k:
            remaining = max_distance - dist
            reachable = sum(
                1
                for v in range(num_nodes)
                if node_visits[v] == 0
                and v not in history
                and sp[curr][v] + (home[v] if return_to_start else 0) <= remaining
            )
            if new_cnt + reachable < heap[0][0][0]:
                stats["pruned"] += 1
                return

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

            is_new = node_visits[nxt] == 0 and nxt not in history
            used_dir_edges.add((curr, nxt))
            node_visits[nxt] += 1
            path.append(nxt)

            dfs(nxt, dist + w, new_cnt + (1 if is_new else 0))

            path.pop()
            node_visits[nxt] -= 1
            used_dir_edges.discard((curr, nxt))

    dfs(start_node, 0, 0)
    return sorted(heap, reverse=True), stats


def show(title, results, id_to_name, stats=None, limit=10):
    print(f"\n--- {title} ---")
    if not results:
        print("No trails found within budget.")
    for key, total, _, path, nn, fresh, rep in results[:limit]:
        names = " -> ".join(id_to_name[n] for n in path)
        print(
            f"[{total:>5.1f} mi | new nodes {nn} | fresh {fresh:>5.1f} | repeat {rep:>5.1f}] {names}"
        )
    if stats:
        note = "  ** search hit its cap; results may be incomplete **" if stats["truncated"] else ""
        print(f"(search: {stats['calls']:,} calls, {stats['pruned']:,} branches pruned){note}")


# ----------------------------------------------------------------------
# Command-line entry point
# ----------------------------------------------------------------------
def parse_args():
    ap = argparse.ArgumentParser(description="Rank trail routes within a mileage budget.")
    ap.add_argument("--origin", default="Trail_5", help="Start node (must be is_allowed_start).")
    ap.add_argument("--budget", type=float, default=25, help="Max miles for a route.")
    ap.add_argument("--visited", nargs="*", default=[], help="Nodes already visited before.")
    ap.add_argument("--top", type=int, default=10, help="Routes to display per report.")
    ap.add_argument("--max-visits", type=int, default=2, help="Max visits per node.")
    ap.add_argument("--max-expansions", type=int, default=200_000,
                    help="Safety cap on DFS calls (0 = no cap).")
    ap.add_argument("--time-limit", type=float, default=10.0,
                    help="Safety cap in seconds (0 = no cap).")
    ap.add_argument("--no-prune", action="store_true", help="Disable branch-and-bound pruning.")
    ap.add_argument("--skip-validation", action="store_true", help="Hide data warnings.")
    return ap.parse_args()


def main():
    args = parse_args()
    n, matrix, name_to_id, id_to_name = build_matrix_from_dict(trail_data)

    if not args.skip_validation:
        for w in validate_graph(trail_data):
            print(f"[data warning] {w}")

    if args.origin not in name_to_id:
        raise SystemExit(f"Origin '{args.origin}' not found in trail data.")
    if not trail_data[args.origin].get("is_allowed_start"):
        valid = [k for k, v in trail_data.items() if v.get("is_allowed_start")]
        raise SystemExit(f"'{args.origin}' is not a valid start. Valid starts: {', '.join(valid)}")

    unknown = [v for v in args.visited if v not in name_to_id]
    if unknown:
        print(f"[warning] ignoring unknown visited nodes: {', '.join(unknown)}")
    been_there = {name_to_id[v] for v in args.visited if v in name_to_id}

    start = name_to_id[args.origin]
    common = dict(
        max_node_visits=args.max_visits,
        prune=not args.no_prune,
        max_expansions=args.max_expansions or None,
        time_limit=args.time_limit or None,
    )

    print("=" * 60)
    print(f"TRAIL MENU (budget {args.budget:g} mi, origin {args.origin})")
    print("=" * 60)

    t0 = time.perf_counter()

    loops, st = find_ranked_trails(n, matrix, args.budget, start, True, **common)
    show("Loop trails, best first", loops, id_to_name, st, args.top)

    if been_there:
        loops2, st = find_ranked_trails(
            n, matrix, args.budget, start, True, history=been_there, **common
        )
        show(f"Loop trails, after visiting {', '.join(args.visited)} before",
             loops2, id_to_name, st, args.top)

    p2p, st = find_ranked_trails(n, matrix, args.budget, start, False, **common)
    show("Point-to-point trails, best first", p2p, id_to_name, st, args.top)

    print(f"\nTotal search time: {time.perf_counter() - t0:.4f} seconds")


if __name__ == "__main__":
    main()
