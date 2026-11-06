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
