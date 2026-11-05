from itertools import combinations

def held_karp(dist):
    """
    Solve the Traveling Salesman Problem using the Held–Karp algorithm.
    dist: a 2D square matrix (list of lists) of pairwise distances.
    Returns (min_cost, tour) where tour is a list of node indices, starting
    and ending at 0.
    """
    n = len(dist) #total number of cities (rows in matrix)
    # Number of subsets: 2^n
    N = 1 << n #total number of possible subsets of cities
    INF = float('inf') #used ot represent mathematical infinity

    # dp[mask][j] = minimum cost to reach subset 'mask' and end at node j
    # mask is integer used to represnet a collection of items using binary bits and compresses collection into single number
    # 1 = city visited and 0 = city not visited
    dp = [[INF] * n for _ in range(N)] #int dynamic programming table and created 2D list of size 2**n * n
    # parent[mask][j] = previous node before j in optimal path for (mask, j)
    parent = [[None] * n for _ in range(N)] # remembers which city you just came from 

    # Base case: start at node 0, mask = 1<<0, binary = 1 (visited), dist = 0
    dp[1][0] = 0

    # Iterate over all subsets that include node 0
    for mask in range(1, N): # loops over every int from 1 to 2^n - 1
        if not (mask & 1): # checks if rightbost bit is 1, it not 1, it skips, meaning: our path must include the starting city
            continue  # we always require the tour to start at node 0
        for j in range(1, n): # loops through all possible ending cities, skipping starting city
            if not (mask & (1 << j)): # is j included in current subset? If bit is 0, j has not been visited yet so it skips to the next city
                continue  # j not in subset
            prev_mask = mask ^ (1 << j) # turns off j-th bit, represents the exact state of the visited cities right before we vist city j
            # Try all possibilities of coming to j from some k in prev_mask
            for k in range(n): # loops through every possible city, k, that could be the immediate predecessor to city j
                if prev_mask & (1 << k): # checks if city k has been visited in previous state (prev_mask). We can only travel from k to j if we have already visited k
                    cost = dp[prev_mask][k] + dist[k][j] # computes cost: optimal cost to visit all cities in 
                    # if new cost is cheaper than the path found, it updates DP with cheapest cost records k as the "parent" (previous) of j
                    if cost < dp[mask][j]:
                        dp[mask][j] = cost
                        parent[mask][j] = k

    # Close the tour: return to node 0
    full_mask = (1 << n) - 1 # all cities have been visited
    min_cost = INF # sets baseline tracking variables to find leg of trip
    last = None

    # loops thouhg every city to evaluate cost of completing full cicrle. Adds cost to distance required to return
    #home from j to 0 (starting node). Tracks absolute min total cost found and remembers which city j was the final stop
    for j in range(1, n):
        cost = dp[full_mask][j] + dist[j][0]
        if cost < min_cost:
            min_cost = cost
            last = j

    # Reconstruct path
    #sets up tracking lists and pointers to re-trace steps backward from final city (last) to visited cities (full_mask)
    path = []
    mask = full_mask
    curr = last

    # steps backward through optimal path. Adds current city to path, looks where it cam from via parent table, strips current city
    #out of bitmask and moves tracking pointer to previous city (prev) and repeats until it hits the base case (None)
    while curr is not None:
        path.append(curr)
        prev = parent[mask][curr]
        mask ^= (1 << curr)
        curr = prev
    path.append(0)            # add the start node
    path.reverse()            # reverse to get 0 -> ... -> last
    path.append(0)            # and return to 0

    return min_cost, path # tuple containing final optimized distance int and ordered list of cities representing the ideal route

if __name__ == "__main__":
    # Example test case: 4 cities, symmetric distances
    # Example: going from city 2 to 0 costs 15, going from 0 to 2 costs 9
    dist_matrix = [
        [0,  2,  9, 10],
        [1,  0,  6,  4],
        [15, 7,  0,  8],
        [6,  3, 12,  0]
    ]

    cost, tour = held_karp(dist_matrix)
    print("Minimum tour cost:", cost)
    print("Tour:", tour)
