# solve lattice model with n rows and m columns
# the 'oxygen' molecules are locate at {1 3..2m-1}x{1 3..2n-1}

import sys
import numpy as np
import typing
from typing import List
# for printing with colors
from sty import fg, bg, ef, rs
# for deep copy of lists
import copy

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


def encode_locally(state, pos):
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
                code = encode_locally(state, center_pos)
                if code not in puzzle_pieces:
                    broken = True
                    break
    return not broken


def print_help():
    print("Run `python mn.py m n' to solve model with m columns and n rows.")


if __name__ == '__main__':
    # m cols, n rows
    if not len(sys.argv) == 3:
        print_help()
        raise RuntimeError("Wrong number of command line arguments.")

    try:
        M = int(sys.argv[1])
        N = int(sys.argv[2])
    except ValueError:
        print_help()
        raise RuntimeError("Invalid command line arguments.")

    if M < 1 or N < 1:
        raise RuntimeError("Invalid col/row numbers.")

    # TODO: declare puzzle pieces
    puzzle_pieces = [[2, 2, 2, 2], [1, 1, 1, 1], [1, 2, 2, 1], [2, 1, 1, 2],
                     [2, 1, 2, 1], [1, 2, 1, 2]]
    state = fill_boundary_condition(gen_empty_state(M, N), M, N)

    print('\nInitial state:\n')
    render(state, M, N)
    print('')

    print(fg.da_magenta + 'Solving with brute force 😠' + fg.rs)
    sol_brute_force(copy.deepcopy(state), M, N, puzzle_pieces,
                    unfilled_positions(state, M, N))

    print(fg.green + '\nFound {} solutions:'.format(len(solutions)) + fg.rs +
          '\n')

    for sol in solutions:
        render(sol, M, N)
        print(' ')
