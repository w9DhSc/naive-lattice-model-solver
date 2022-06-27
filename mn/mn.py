# solve lattice model with n rows and m columns
# the 'oxygen' molecules are locate at {1 3..2m-1}x{1 3..2n-1}

# * coordinates

import numpy as np
import typing
from typing import List
from sty import fg, bg, ef, rs

# ** functions


def boundary_positions(m, n):
    down = [(2 * x + 1, 0) for x in range(m)]
    left = [(0, 2 * y + 1) for y in range(n)]
    up = [(2 * x + 1, 2 * n) for x in range(m)]
    right = [(2 * m, 2 * y + 1) for y in range(n)]
    return down + left + up + right


def at_boundary_p(pos, m, n):
    x, y = pos
    return x == 0 or x == 2 * m or y == 0 or y == 2 * n


def count_neighbor_filled(pos, state, m, n):
    x, y = pos
    neighbors = get_neighbors(pos, m, n)
    return len([n for n in neighbors if state[n[0], n[1]] != ''])


def get_neighbor_centers(pos, m, n):
    x, y = pos
    if x == 0:
        return [(x + 1, y)]
    elif x == 2 * m:
        return [(x - 1, y)]
    elif y == 0:
        return [(x, y + 1)]
    elif y == 2 * n:
        return [(x, y - 1)]
    elif y % 2 == 0:
        # on 'vertical lines
        return [(x, y - 1), (x, y + 1)]
    else:
        return [(x - 1, y), (x + 1, y)]


def center_to_vertices(pos):
    x, y = pos
    return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


def get_neighbors(pos, m, n):
    x, y = pos
    if x < 0 or x > 2 * m - 1 or y < 0 or y > 2 * n - 1 or (x + y) % 2 == 0:
        raise RuntimeError(
            "Illegal vertex position ({}, {}). Lattice size: {} rows, {} columns."
            .format(x, y, m, n))
    return [
        z for z in sum(
            map(center_to_vertices, get_neighbor_centers(pos, m, n)), [])
        if (not z == pos)
    ]


# * algorithm
# given boundary conditions:
# - locate_target :: among the vertices with most number of neighbors, choose the *left* most in *down* most one
#     TODO: prove by induction {min max # neighbor = 2}
#   - if it has 3 neighbors, it is automatically determined.
#     goto locate_target
#   - if it has 2 neighbors, split into 2 subroutines


def sol(state, m, n, pieces):
    # TODO
    pass


# * draw


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
            elif state[i, j] == b'+':
                print(positive_str, end="")
            elif state[i, j] == b'-':
                print(negative_str, end="")
            elif state[i, j] == '':
                print(unfilled_str, end="")

            if i == 2 * m:
                print('' + bg.rs)


def test_fn():
    return 2


# * main


def gen_empty_state(m, n):
    tmp_state = np.chararray((2 * m + 1, 2 * n + 1))
    tmp_state[:] = ''
    return tmp_state


def fill_boundary_condition(state, boundary_negatives, M, N):
    for x, y in boundary_positions(M, N):
        state[x, y] = b'+'

    for x, y in boundary_negatives:
        state[x, y] = b'-'

    return state


def default_boundary_negative_positions(m, n):
    return [(1, 2 * n), (2 * m - 1, 0)]


if __name__ == '__main__':
    # n rows and m columns
    N = 5
    M = 7
    state = gen_empty_state(M, N)

    # TODO: specify '-'s to put on the boundary
    boundary_neg = default_boundary_negative_positions(M, N)

    # TODO: declare puzzle pieces
    puzzle_pieces: List[List[str]] = []
    state = fill_boundary_condition(state, boundary_neg, M, N)
    # solutions = sol(state, M, N, puzzle_pieces)

    print('\n' + fg.blue + 'Initial state:' + fg.rs + '\n')
    render(state, M, N)

    pass
