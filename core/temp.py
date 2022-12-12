def get_reachability_matrix(traffic):
    reachability_matrix = [[0]*10 for x in range(10)]
    pairs_only = traffic[0][1]
    for pair in pairs_only:
        src = int(pair[0]) - 1
        dst = int(pair[1]) - 1
        reachability_matrix[src][dst] = 1
    for i in reachability_matrix:
        for j in i:
            print(j, end=' ')
        print()
    return reachability_matrix


def get_src_dst_map_reachability_matrix(reachability_matrix, traffic):
    pairs_only = traffic[0][1]
    src_dst_map = {}
    for pair in pairs_only:
        src = int(pair[0]) - 1
        dst = int(pair[1]) - 1
        if reachability_matrix[src][dst] != 1:
            if pair[0] not in src_dst_map:
                src_dst_map[pair[0]] = []
            src_dst_map[pair[0]].append(pair[1])
            # обновляем матрицу достижимости
            reachability_matrix[src][dst] = 1
    print("Reachability matrix:\n")
    for i in reachability_matrix:
        for j in i:
            print(j, end=' ')
        print()
    return src_dst_map


if __name__ == '__main__':
    res = get_reachability_matrix()