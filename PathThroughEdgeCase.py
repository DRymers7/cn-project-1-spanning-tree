# PathThrough Edge Case Test
# Tests a scenario where pathThrough needs to change multiple times
# 1 --- 2 --- 3
# |           |
# 4 --- 5 --- 6
# Initially path will be through lowest IDs, then 3 becomes root

topo = {
    1: [2, 4],
    2: [1, 3],
    3: [2, 6],
    4: [1, 5],
    5: [4, 6],
    6: [3, 5]
}
ttl_limit = 3
drops = [1]  # Dropping 1 will force pathThrough changes

# Expected outcome:
# Before drop: paths go through 1
# After drop: paths should reorganize through 2 and 3