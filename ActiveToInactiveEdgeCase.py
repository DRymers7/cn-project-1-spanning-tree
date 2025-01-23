# Active-to-Inactive Switch Test
# Tests switches changing from active to inactive
#    1
#   / \
#  2---3
#  |\ /|
#  | 4 |
#  |/ \|
#  5---6

topo = {
    1: [2, 3],
    2: [1, 3, 4, 5],
    3: [1, 2, 4, 6],
    4: [2, 3, 5, 6],
    5: [2, 4, 6],
    6: [3, 4, 5]
}
ttl_limit = 2
drops = [1, 3]  # Sequential drops to force active-inactive transitions

# Expected outcome:
# Links should properly deactivate as better paths become available
# Multiple switches will need to change active status multiple times