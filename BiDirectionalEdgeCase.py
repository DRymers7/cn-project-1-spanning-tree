# Bidirectional Link Test
# This topology specifically tests bidirectional link activation
# The topology forms a "Y" shape where all paths should maintain
# bidirectional connections after switch 1 is dropped
#
#      1
#      |
#      2
#     / \
#    3   4
#   /     \
#  5       6

topo = {
    1: [2],
    2: [1, 3, 4],
    3: [2, 5],
    4: [2, 6],
    5: [3],
    6: [4]
}
ttl_limit = 3
drops = [1]  # Dropping 1 forces a recalculation of the spanning tree

# Expected behavior:
# 1. Initially, all links should point through 1
# 2. After 1 is dropped:
#    - 2 becomes root
#    - All links should be bidirectional through the Y shape
#    - Each node should maintain active links to both its parent and children