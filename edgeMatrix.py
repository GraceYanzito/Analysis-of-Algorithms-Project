def dictionary_to_matrix(dict_graph):

    node_names = sorted(list(dict_graph.keys()))
    n = len(node_names)
    
    matrix = [[float('inf')] * n for _ in range(n)]

    allowed_starts = []
    
    for i, from_node in enumerate(node_names):
        matrix[i][i] = 0
        
        # 1. Safely grab the connections block, default to empty dict if missing
        node_info = dict_graph.get(from_node, {})

        if node_info.get("is_allowed_start", False):
            allowed_starts.append(i)
          
        connections = node_info.get("connections", {})
        
        # 2. Loop through your routes
        for to_node, route_metadata in connections.items():
            if to_node in node_names:
                j = node_names.index(to_node)
                
                # 3. Pull the specific numeric property out of the metadata dictionary
                distance = route_metadata.get("distance", float('inf'))
                matrix[i][j] = distance
                
    return matrix, node_names, allowed_starts
