# from sympy import symbols
from sympy import *  # bad practice
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

        # self.pos
        self.pos = '(S)' if pos == "row1" else '(T)' if pos == "row2" else ''

        # self.sup1

        if pos == "diag":
            if i == j:  # only one color
                self.type = 'A'
            elif piece == [i, j, i, j]:
                self.type = 'B'
            elif piece == [i, j, j, i]:
                self.type = 'C'
            else:
                raise RuntimeError("piece {} illegal".format(piece))
        else:  # pos = "row1" or "row2"
            if i == j:
                self.type = 'a'
            elif piece == [i, j, i, j]:
                self.type = 'b'
            elif piece == [i, j, j, i]:
                self.type = 'c'
            else:
                raise RuntimeError("piece {} illegal".format(piece))

        # self.sub1, self.sub2

        self.sub1 = i
        self.sub2 = j if i != j else -1

    def weight_symbolic(self):
        subscripts = '_{' + ''.join(
            str(i) if i >= 0 else '' for i in [self.sub1, self.sub2]) + '}'
        # subscripts = ''.join(f"{chr(0x2080+i)}"
        #                      for i in [self.sub1, self.sub2])

        return symbols(self.type + subscripts + self.pos)


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


def gen_bds(colors={0, 1, 2}):
    """
    Returns all boundary conditions of the 72 nontrivial YBEs.
    """
    bds = []
    for i in [3, 4, 5, 6, 7, 9, 10]:
        for a, b in itertools.permutations(colors, r=2):
            bds.append([a if j == 1 else b for j in Z[i]])
    for i in [12, 13, 14, 15, 16]:
        for a, b, c in itertools.permutations(colors):
            bds.append([a if j == 1 else b if j == 2 else c for j in Z[i]])
    return bds


def gen_bd_2():
    bds = []
    for i in [3, 4, 5, 6, 7, 9, 10]:
        bds.append(Z[i])
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
    @param split: if True, split vertical weights and diagonal weights. Instead of a prduct, a pair is returned.
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


def gen_eqs(colors={0, 1, 2}):
    for bd in gen_bds():
        Zl = solve_left_from_bd(True, bd, colors)
        Zr = solve_left_from_bd(False, bd, colors)
        print("{} \\quad & {} = {} \\\\".format(''.join(str(i) for i in bd),
                                                latex(Zl), latex(Zr)))


def gen_eq_2(colors={1, 2}):
    for bd in gen_bd_2():
        Zl = solve_left_from_bd(True, bd, colors)
        Zr = solve_left_from_bd(False, bd, colors)
        print("{} \\quad & {} = {} \\\\".format(''.join(str(i) for i in bd),
                                                latex(Zl), latex(Zr)))


def diag_weights(colors={1, 2, 3}):
    ws = []
    for i in colors:
        ws.append(symbols("D_{{{}}}^{{3}}".format(i)))
    for i, j in itertools.permutations(colors, r=2):
        for sup1 in [1, 2]:
            ws.append(symbols("D_{{{}{}}}^{{{}}}".format(i, j, sup1)))
    return ws


def gen_mat(colors):
    mat = []
    for bd in gen_bds():
        Zl = solve_left_from_bd(True, bd, colors)
        Zr = solve_left_from_bd(False, bd, colors)

        # (symbols("V_1") * symbols("V_2") + symbols("V_3")).coeff(symbols("V_2")))
        row = []
        for dw in diag_weights():
            row.append((Zl - Zr).coeff(dw))
        mat.append(row)
    return mat


def write_mat(colors):
    with open('mat.csv', 'w') as f:
        # create the csv writer
        writer = csv.writer(f)
        for r in gen_mat(colors):
            writer.writerow([str(coeff) for coeff in r])
