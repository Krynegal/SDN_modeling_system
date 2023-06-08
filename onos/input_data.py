import sys


def read_bw_matrix():
    with open("bandwidth_matrix.txt", "r") as f:
        bw_matrix = [list(map(int, row.strip().split(", "))) for row in f.readlines()]
    return bw_matrix


def print_matrix(matrix):
    for i in matrix:
        print(i)
    print()


def matrix_correctness(matrix):
    row_num = len(matrix)
    for row in matrix:
        if len(row) != row_num:
            return False
    return True


def main():
    bw_matrix = read_bw_matrix()
    if not matrix_correctness(bw_matrix):
        sys.exit("Not square matrix")
    print_matrix(bw_matrix)
    return bw_matrix

if __name__ == '__main__':
    main()
