# Tie-Breaking Edge Case Test
# Creates multiple equal-distance paths to root
#    1
#   / \
#  2   3
#  |   |
#  4---5
#  |   |
#  6   7

topo = {
    1: [2, 3],
    2: [1, 4],
    3: [1, 5],
    4: [2, 5, 6],
    5: [3, 4, 7],
    6: [4],
    7: [5]
}
ttl_limit = 4
drops = []  # No drops needed for this test

# Expected outcome:
# Switches should always choose path through lowest ID
# when distances are equal