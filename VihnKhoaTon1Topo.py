# submitted by Vihn Khoa Ton, OMSCS Fall 2018

# 1 --- 3 --- 2    | Answer: 1 --- 3 --- 2
#       |     |    |               |     |
#       |     |    |               |     |
#       4 --- 5    |               4     5

topo = { 1 : [3],      # Answer: 1 - 3
        2 : [3, 5],    #         2 - 3, 2 - 5
        3 : [4, 1, 2], #         3 - 1, 3 - 2, 3 - 4
        4 : [5, 3],    #         4 - 3
        5 : [4, 2] }   #         5 - 2
ttl_limit = 2
drops = []
