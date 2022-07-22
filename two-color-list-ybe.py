from sympy import symbols
import csv
import itertools


class Weight:
    """
        Encodes metadata of a puzzle piece.

    Members:
    type: either 'D' or 'V' (diagonal or rectangular)
    sub1, sub2, sup1, sup2: its subscripts and superscripts. in some cases, sub2 or sup2 do not exists and they are stored as 0.

    Methods:
    weight_symbolic(): return the symbol for the weight, using sympy and Joseph's notation
    """

    def __init__(self, pos, piece, colors):

        # first make sure the piece is legal
        assert len(set(piece)) in [1, 2]
        assert is_piece(piece, colors)
        i = piece[0]
        j = piece[1]

        # self.sup1

        if i == j:  # only one color
            self.sup1 = 3
        else:  # two colors
            if piece == [i, j, i, j]:
                self.sup1 = 1
            elif piece == [i, j, j, i]:
                self.sup1 = 2
            else:
                raise RuntimeError("piece {} illegal".format(piece))

        # self.sup2 and self.type

        if pos == "diag":
            self.sup2 = 0
            self.type = 'D'
        elif pos == "row1":
            self.sup2 = 1
            self.type = 'V'
        elif pos == "row2":
            self.sup2 = 2
            self.type = 'V'
        else:
            raise RuntimeError(
                "Illegal position info in piece. Only diag, row1 or row2 are supported."
            )

        # self.sub1

        if i == j:
            self.sub1 = i
            self.sub2 = 0
        else:
            self.sub1 = i
            self.sub2 = j

    def weight_symbolic(self):
        scripts = [
            str(s) if s != 0 else ''
            for s in [self.sub1, self.sub2, self.sup1, self.sup2]
        ]
        return symbols("{}_{{{}{}}}^{{{}{}}}".format(self.type, scripts[0],
                                                     scripts[1], scripts[2],
                                                     scripts[3]))


Z = {
    3: [1, 1, 2, 1, 2, 1],
    4: [1, 1, 2, 2, 1, 1],
    5: [1, 2, 1, 1, 1, 2],
    6: [1, 2, 1, 1, 2, 1],
    7: [1, 2, 1, 2, 1, 1],
    9: [1, 2, 2, 2, 1, 2],
    10: [1, 2, 2, 2, 2, 1],
    12: [1, 2, 3, 1, 3, 2],
    13: [1, 2, 3, 2, 1, 3],
    14: [1, 2, 3, 3, 1, 2],
    15: [1, 2, 3, 2, 3, 1],
    16: [1, 2, 3, 3, 2, 1]
}


def card_2_subsets(s):
    """
    Return subsets of s of cardinality 2.
    """
    return [set(i) for i in itertools.combinations(s, 2)]


def gen_bds():
    """
    Returns all boundary conditions of the 72 nontrivial YBEs.
    """
    bds = []
    for i in [3, 4, 5, 6, 7, 9, 10]:
        for a, b in itertools.permutations({1, 2, 3}, r=2):
            bds.append([a if j == 1 else b for j in Z[i]])
    for i in [12, 13, 14, 15, 16]:
        for a, b, c in itertools.permutations({1, 2, 3}):
            bds.append([a if j == 1 else b if j == 2 else c for j in Z[i]])
    return bds


def is_piece(piece, colors):
    """
    @param piece:
    Here piece should be a length-4 list encoding a puzzle piece, which is either rectangular or diagonal.
    If the piece is rectangular, the list should start from the left and go clockwise.
    If the piece is diagonal, the list should start from the bottom left and go clockwise.
    @param colors:
    Should be a set of colors.
    """
    for i, j in card_2_subsets(colors):
        legal = [[j, j, j, j], [i, i, i, i], [j, i, j, i], [i, j, i, j],
                 [i, j, j, i], [j, i, i, j]]
        if piece in legal:
            return True
    return False


def is_state_legal(state, colors):
    """
    Returns if a state is legal given the colors.
    @param state: a dictionary with keys "diag", "row1", "row2"
    @param colors: a set containing the colors
    """
    return all([is_piece(p, colors) for p in state.values()])


def legal_state_to_Z(state, colors):
    """
    Returns the partition function of a legal state.
    The parameters are the same as those of `is_state_legal`
    """
    assert is_state_legal(state, colors)
    Z = 1
    for pos in state:
        Z = Z * Weight(pos, state[pos], colors).weight_symbolic()
    return Z


def solve_left_from_bd(is_left, bd, colors):
    """
    Returns the partition function from a boundary condition. For the result we use Joseph's notation, which is implemented in the `Weight` class.
    @param is_left: True if we're to solve the left model, else False.
    @param bd: a list of length six encoding the boundary condition. It has the form [alpha, beta, gamma, delta, epsilon, eta], following the notation of Andy's worksheets.
    @param colors: a set of allowed colors.
    """
    alpha, beta, gamma, delta, epsilon, eta = bd
    Z = 0
    for i in colors:
        for j in colors:
            for k in colors:
                state = {}
                if is_left:
                    state = {
                        "diag": [alpha, beta, i, j],
                        "row1": [i, gamma, delta, k],
                        "row2": [j, k, epsilon, eta]
                    }
                else:
                    state = {
                        "diag": [i, j, delta, epsilon],
                        "row1": [alpha, k, i, eta],
                        "row2": [beta, gamma, j, k]
                    }
                if is_state_legal(state, colors):
                    Z = Z + legal_state_to_Z(state, colors)
    return Z


def import_hash_csv():
    """
    Read hash of rectangular from hash.csv.
    Returns a dictionary where an item looks like '1211': 50.21507752.
    """
    v_weight_hash = {}
    with open('hash.csv', mode='r') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            scripts = ''.join([z for z in line[0] if z.isdigit()])
            assert len(scripts) == 4
            hash_value = float(line[1])
            v_weight_hash[scripts] = hash_value
    return v_weight_hash


def gen_eqs():
    colors = {1, 2, 3}
    for bd in gen_bds():
        Zl = solve_left_from_bd(True, bd, colors)
        Zr = solve_left_from_bd(False, bd, colors)
        print("bd: {} :> {} = {}".format(bd, Zl, Zr))
