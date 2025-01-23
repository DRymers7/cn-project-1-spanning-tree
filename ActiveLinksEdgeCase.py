# Active Links Update Edge Case Test
# Tests rapid changes in active links
#   1---2---3
#   |\ / \ /|
#   | 4   5 |
#   |/ \ / \|
#   6---7---8

topo = {
    1: [2, 4, 6],
    2: [1, 3, 4, 5],
    3: [2, 5, 8],
    4: [1, 2, 6, 7],
    5: [2, 3, 7, 8],
    6: [1, 4, 7],
    7: [4, 5, 6, 8],
    8: [3, 5, 7]
}
ttl_limit = 3
drops = [2]  # Dropping 2 forces rapid active link changes

# Expected outcome:
# Initially paths go through 1 and 2
# After drop, must quickly reorganize active links