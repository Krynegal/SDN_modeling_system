def print_matrix(matrix):
    for row in matrix:
        print(row)


def get_matrix(links, devices_num):
    matrix = [[0] * devices_num for _ in range(devices_num)]
    for link in links:
        src = int(link["src"]["device"][3:], 16)
        dst = int(link["dst"]["device"][3:], 16)
        matrix[dst - 1][src - 1] = 1
    return matrix
