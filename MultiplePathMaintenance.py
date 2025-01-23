# Multiple Path Maintenance Test
# This topology creates a mesh where multiple valid paths must be maintained
# The key is that some nodes must maintain multiple active links even when
# they're not strictly parent/child relationships
#
#    1 --- 2
#    | \ / |
#    |  3  |
#    | / \ |
#    4 --- 5
#    | \ / |
#    |  6  |
#    | / \ |
#    7     8

topo = {
    1: [2, 3, 4],
    2: [1, 3, 5],
    3: [1, 2, 4, 5],
    4: [1, 3, 5, 6, 7],
    5: [2, 3, 4, 6, 8],
    6: [4, 5, 7, 8],
    7: [4, 6],
    8: [5, 6]
}
ttl_limit = 4
drops = [3]  # Dropping 3 forces recomputation of multiple paths