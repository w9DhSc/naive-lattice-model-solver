# solve lattice model with n rows and m columns
# the 'oxygen' molecules are locate at {1 3..2m-1}x{1 3..2n-1}

# TODO: specify dependencies
import sys, getopt
import numpy as np
import typing
from typing import List
# for printing with colors
from sty import fg, bg, ef, rs
# for deep copy of lists
import copy
from sympy import symbols

solutions = []


def debug_output(msg):
    print(bg.red + fg.white + 'DEBUG' + bg.rs + fg.rs + ": " + msg)


def boundary_positions(m, n):
    down = [(2 * x + 1, 0) for x in range(m)]
    left = [(0, 2 * y + 1) for y in range(n)]
    up = [(2 * x + 1, 2 * n) for x in range(m)]
    right = [(2 * m, 2 * y + 1) for y in range(n)]
    return down + left + up + right


def unfilled_positions(state, m, n):
    lst = []
    for i in range(2 * m + 1):
        for j in range(2 * n + 1):
            if (i + j) % 2 == 1 and state[i, j] == 0:
                lst.append((i, j))
    return lst


# TODO
def sol_brute_force(state, m, n, pieces, unfilled):
    unfilled = unfilled_positions(state, m, n)
    num = len(unfilled)
    if num == 0:
        if solution_p(state, pieces, m, n):
            print("⋆", end="")
            solutions.append(state)
        else:
            return []
    else:
        state_clone_1 = copy.deepcopy(state)
        state_clone_2 = copy.deepcopy(state)
        x, y = unfilled[0]
        rest = unfilled[1:]
        state_clone_1[x, y] = 1
        state_clone_2[x, y] = 2
        del state
        sol_brute_force(state_clone_1, m, n, pieces, rest)
        sol_brute_force(state_clone_2, m, n, pieces, rest)


def sol(state, m, n, pieces):
    unfilled_ = unfilled_positions(state, m, n)

    if len(unfilled_) == 0:
        return state
    else:
        unfilled = ge(unfilled_, state, m, n)
        pos = get_left_most_in_down_most(unfilled)
        return maybe_fill_new(state, pos, pieces, m, n)


# * render


def render(state, m, n):
    positive_str = fg.red + bg.black + '+' + bg.rs
    negative_str = fg.green + bg.black + '-' + bg.rs
    empty_str = fg.rs + bg.rs + ' '
    oxygen_str = fg.li_grey + bg.black + '+'
    unfilled_str = fg.li_cyan + bg.black + '?'

    for jj in range(2 * n + 1):
        for i in range(2 * m + 1):
            j = 2 * n - jj

            if i % 2 == 0 and j % 2 == 0:
                print(empty_str, end="")
            elif (i % 2 == 1 and j % 2 == 1):
                print(oxygen_str, end="")
            elif state[i, j] == 2:
                print(positive_str, end="")
            elif state[i, j] == 1:
                print(negative_str, end="")
            elif state[i, j] == 0:
                print(unfilled_str, end="")

            if i == 2 * m:
                print('' + bg.rs)


def test_fn():
    return 2


# * initial state


def gen_empty_state(m, n):
    tmp_state = np.zeros((2 * m + 1, 2 * n + 1), dtype=int)
    return tmp_state


def fill_boundary_condition(state, m, n):
    for x, y in boundary_positions(m, n):
        state[x, y] = 2

    for x, y in [(1, 2 * n), (2 * m - 1, 0)]:
        state[x, y] = 1

    return state


def piece_at_point(state, pos):
    x, y = pos
    up = state[x, y + 1]
    left = state[x - 1, y]
    right = state[x + 1, y]
    down = state[x, y - 1]
    return [up, left, right, down]


def solution_p(state, puzzle_pieces, m, n):
    broken = False
    for i in range(m):
        if not broken:
            for j in range(n):
                center_pos = (2 * i + 1, 2 * j + 1)
                code = piece_at_point(state, center_pos)
                if code not in puzzle_pieces:
                    broken = True
                    break
    return not broken


def print_help():
    print("""mn.py [OPTION...]
num_cols and num_rows default to 3 unless specified.
Options:
\t-m, --num_cols\t Number of columns.
\t-n, --num_rows\t Number of rows.
\t-h            \t give this help.
\t-s            \t suppress output of solutions""")


def compute_summand_in_partition_function(state,
                                          m,
                                          n,
                                          weights,
                                          weights_specific,
                                          specific=True):
    summand = 1
    for i in range(m):
        for j in range(n):
            center_pos = (2 * i + 1, 2 * j + 1)
            code = piece_at_point(state, center_pos)
            if code not in puzzle_pieces:
                raise RuntimeError(
                    "Attempt to compute partition function for an illegal state."
                )
            abstract_weight_symbol = weights[piece_to_key(code)]
            if not specific:
                summand = summand * abstract_weight_symbol
            else:
                specific_weight_mediate = weights_specific[
                    abstract_weight_symbol.name]
                specific_weight = specific_weight_mediate if (
                    not specific_weight_mediate
                    == 'z') else symbols('z' + str(j + 1))
                summand = summand * specific_weight
    return summand


def piece_to_key(piece):
    return str(piece[0] * 1000 + piece[1] * 100 + piece[2] * 10 + piece[3])


def key_to_piece(key):
    return [int(digit) for digit in key]


if __name__ == '__main__':
    # m cols, n rows
    M = 3
    N = 3
    supress_solutions_output = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "shm:n:",
                                   ["num_cols=", "num_rows="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-m", "--num_cols"):
            M = int(arg)
        elif opt in ("-n", "--num_rows"):
            N = int(arg)
        elif opt == '-s':
            supress_solutions_output = True

    # sadly lists are unhashable, although in python strings are lists of chars...
    weights = {
        "2222": symbols('a1'),
        "1111": symbols('a2'),
        "1221": symbols('b1'),
        "2112": symbols('b2'),
        "2121": symbols('c1'),
        "1212": symbols('c2')
    }

    weights_specific = {
        'a1': 1,
        'a2': 0,
        'b1': 1,
        'b2': 'z',
        'c1': 'z',
        'c2': 1
    }

    puzzle_pieces = [key_to_piece(key) for key in weights]

    state = fill_boundary_condition(gen_empty_state(M, N), M, N)

    print('\nInitial state:\n')
    render(state, M, N)
    print('')

    print(fg.da_magenta + 'Solving with brute force 😠' + fg.rs)
    sol_brute_force(copy.deepcopy(state), M, N, puzzle_pieces,
                    unfilled_positions(state, M, N))

    print(fg.green + '\nFound {} solutions'.format(len(solutions)) +
          ('.' if supress_solutions_output else ': ') + fg.rs + '\n')

    partition_function = 0
    for sol in solutions:
        if not supress_solutions_output:
            render(sol, M, N)
            print(' ')

        partition_function = partition_function + compute_summand_in_partition_function(
            sol, M, N, weights, weights_specific, specific=True)
    print("\nPartition function: {}".format(partition_function))
