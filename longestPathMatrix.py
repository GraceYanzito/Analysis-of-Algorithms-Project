from edgeMatrix import dictionary_to_matrix # creates matrix based on given edges in our dictionary
from testDictionary import travel_data # dictionary with all of our tail information

def longest_path_matrix(edge_matrix, start_nodes): # in our process, the start nodes are the trail heads that are accessable by parking lot
  
  n = len(edge_matrix)
  NEG_INF = -float('inf')

  # initialize matrix
  longest_matrix = [[NEG_INF] * n for _ in range(n)]

  for node in start_nodes:
    total_subsets = 1 << n

    # creates makes a list (col) the lenght of n and creates len(total_subsets) rows
    subset_table = [[NEG_INF] * n for _ in range(total_subsets)]

    # base case: start at first node, visit only first node
    subset_table[1 << node][node] = 0

    for mask in range(1, total_subsets):
      # checks to see if our start node is part of our current path by comapring binary for starting node and our mask
      if not (mask & (1 << node)):
        continue # if the start node is not in the mask, the program will skip lines below and skip to next item in loop
    
      for j in range(n):
        if not (mask &  (1 << j)):
          continue # j must be in our subset

        if subset_table[mask][j] == NEG_INF:
          continue # ignore the paths that are not possible

        # update longest path matrix with the longest currently found path from node to j
        if subset_table[mask][j] > longest_matrix[node][j]:
          longest_matrix[node][j] = subset_table[mask][j]

        # moving from node j to an unvisited node (to_node)
        for to_node in range(n):
          if not (mask & (1 << to_node)) and edge_matrix[j][to_node] != float('inf'):
            next_mask = mask | (1 << to_node)
            cost = subset_table[mask][j] + edge_matrix[j][to_node]
            if cost > subset_table[next_mask][to_node]:
              subset_table[next_mask][to_node] = cost

    # distance from node to itself is 0
    longest_matrix[node][node] = 0

  return longest_matrix
    
if __name__ == "__main__":
  from testDictionary import travel_data

  graph_matrix, node_names, allowed_starts = dictionary_to_matrix(travel_data)

  longest_path_matrix = longest_path_matrix(graph_matrix, allowed_starts)

  
  print("\n--- The Correct Longest Path Matrix ---")
    
  left_col_width = 17  
  cell_width = 11            
  header_line = f"{'From/To':<{left_col_width}}"
  for name in node_names:
      header_line += f"{name:>{cell_width}}"
  print(header_line)
  
  total_width = left_col_width + (cell_width * len(node_names))
  print("-" * total_width)
  
  for i, row in enumerate(longest_path_matrix):
      from_name = node_names[i]
      row_str = f"{from_name:<{left_col_width}}"
      
      for j, val in enumerate(row):
          if i not in allowed_starts:
              cell_text = "N/A"
          elif val == float('inf'):
              cell_text = "inf"
          else:
              cell_text = str(val)
              
          row_str += f"{cell_text:>{cell_width}}"
          
      print(row_str)
