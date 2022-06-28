def at_boundary_p(pos, m, n):
    x, y = pos
    return x == 0 or x == 2 * m or y == 0 or y == 2 * n


def count_neighbor_filled(pos, state, m, n):
    x, y = pos
    neighbors = get_neighbors(pos, m, n)
    return len([n for n in neighbors if state[n[0], n[1]] != ' '])


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


def get_left_most_in_down_compare_gt(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    if y1 < y2:
        return 1
    elif y1 > y2:
        return -1  # y1 = y2 below
    elif x1 < x2:
        return 1
    elif x1 > x2:
        return -1
    else:
        return 0


def max_elem_with_cmp(lst, gt_fn):
    if len(lst) < 1:
        raise RuntimeError("max_elem_with_cmp: lst shouldn't be empty.")
    elif len(lst) == 1:
        return lst[0]

    max_elem = lst[0]
    for n in range(1, len(lst)):
        if gt_fn(lst[n], max_elem) == 1:
            max_elem = lst[n]

    return max_elem


def get_left_most_in_down_most(lst):
    return max_elem_with_cmp(lst, get_left_most_in_down_compare_gt)


def vertex_p(pos, m, n):
    x, y = pos
    return 0 <= x and x <= 2 * m and 0 <= y and y <= 2 * n and (x + y) % 2 == 1


def filled_p(pos, state, m, n):
    x, y = pos
    if (not (vertex_p(pos, m, n))):
        raise RuntimeError("filled_p: pos isn't a vertex!")

    content = state[x, y]
    return content == 2 or content == 1


def get_unfilled_with_most_filled_neighbors(unfilled, state, m, n):
    num_filled_neighbors_dict = {}
    num_filled_neighbors = []
    for p in unfilled:
        num = len(
            [q for q in get_neighbors(p, m, n) if filled_p(q, state, m, n)])
        num_filled_neighbors_dict[p] = num
        num_filled_neighbors.append(num)

    max_num = max(num_filled_neighbors)
    return [p for p in unfilled if num_filled_neighbors_dict[p] == max_num]


# TODO: implement this
def inspect(state, pos, nc, pieces, m, n):
    """According to given pieces, list all possibilities of filling
    the pieces centered at nc.
    Return dict of {pos, char to fill in there}.
    """
    cx, cy = nc
    unfilled = [
        p for p in [(cx - 1, cy), (cx, cy + 1), (cx, cy - 1), (cx + 1, cy)]
        if (not filled_p(p, state, m, n))
    ]

    unfilled_num = len(unfilled)

    if unfilled_num == 0:
        raise RuntimeError(
            "expecting to fill a pieces, but it has already been filled.")
    elif unfilled_num == 1:
        pass
    else:
        return {}  # give up (unfilled_num > 2:)

    pass


def maybe_fill_new(state, pos, pieces, m, n):
    neighbor_center_one_or_two = get_neighbor_centers(pos, m, n)

    nc_num = len(neighbor_center_one_or_two)
    if nc_num == 1:
        debug_output("pos: {}".format(pos))
        debug_output("m, n: {}, {}".format(m, n))
        raise RuntimeError(
            "Attempt to fill a vertex with only one neighbor center.  Currently no support for incomplete boundary condition."
        )

    # then we assume nc_num = 2, and should look at the two neighboring pieces
    for nc in neighbor_center_one_or_two:
        inspect(state, pos, nc, pieces, m, n)

    pass


def some_test(state, m, n):
    """test unfilled_positions,
    get_unfilled_with_most_filled_neighbors and
    get_left_most_in_down_most.

    """
    state_clone = copy.deepcopy(state)
    unfilled_ = unfilled_positions(stqate_clone, m, n)
    unfilled = get_unfilled_with_most_filled_neighbors(unfilled_, state_clone,
                                                       m, n)
    pos = get_left_most_in_down_most(unfilled)
    print("[debug], pos: {}".format(pos))
    for p in unfilled:
        state_clone[p[0], p[1]] = 2
    render(state_clone, m, n)
