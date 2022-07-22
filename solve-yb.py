from sympy import symbols
from mn import piece_to_key, debug_output
from sty import fg, rs
# 1: +

# rectangular
rectangular = {
    "1111": [1, 1, 1, 1],
    "0000": [0, 0, 0, 0],
    "0101": [0, 1, 0, 1],
    "1010": [1, 0, 1, 0],
    "0110": [0, 1, 1, 0],
    "1001": [1, 0, 0, 1]
}

rec_weights = {
    "1111": "a1",
    "0000": "a2",
    "0101": "b1",
    "1010": "b2",
    "0110": "c1",
    "1001": "c2"
}

diagonal = {
    "1111": [1, 1, 1, 1],
    "0000": [0, 0, 0, 0],
    "1010": [1, 0, 1, 0],
    "0101": [0, 1, 0, 1],
    "0011": [0, 0, 1, 1],
    "1100": [1, 1, 0, 0]
}

diag_weights = {
    "1111": "A1",
    "0000": "A2",
    "1010": "B1",
    "0101": "B2",
    "0011": "C1",
    "1100": "C2"
}

def piece_to_weight(piece, row, diagonal = False, assume_symmetry = True):
    if not diagonal:
        # debug_output("key: {}".format(piece_to_key(piece)))
        weight_symbol_str = rec_weights[piece_to_key(piece)]
        match weight_symbol_str:
            case "a1":
                return symbols("a") if row == 1 else symbols("d")
            case "a2":
                return symbols("a") if row == 1 else symbols("d")
            case "b1":
                return symbols("b") if row == 1 else symbols("e")
            case "b2":
                return symbols("b") if row == 1 else symbols("e")
            case "c1":
                return symbols("c") if row == 1 else symbols("f")
            case "c2":
                return symbols("c") if row == 1 else symbols("f")
        raise RuntimeError("Unrecognized weight.")
    else:
        weight_symbol_str = diag_weights[piece_to_key(piece)]
        match weight_symbol_str:
            case "A1":
                return symbols("A") # if assume_symmetry else symbols("A1")
            case "A2":
                return symbols("A")
            case "B1":
                return symbols("B")
            case "B2":
                return symbols("B")
            case "C1":
                return symbols("C")
            case "C2":
                return symbols("C")
        raise RuntimeError("Unrecognized weight.")
            

rec_pieces = [rectangular[i] for i in rectangular]
diag_pieces = [diagonal[i] for i in diagonal]

def check_left(alpha, beta, gamma, delta, epsilon, eta, i, j, k):
    b1 = [k, delta, gamma, i] in rec_pieces
    b2 = [eta, epsilon, k, j] in rec_pieces
    b3 = [alpha, j, i, beta] in diag_pieces
    return b1 and b2 and b3


def check_right(alpha, beta, gamma, delta, epsilon, eta, i, j, k):
    b1 = [j, i, gamma, beta] in rec_pieces
    b2 = [eta, k, j, alpha] in rec_pieces
    b3 = [k, epsilon, delta, i] in diag_pieces
    return b1 and b2 and b3


def z_left(alpha, beta, gamma, delta, epsilon, eta, i, j, k):
    w1 = piece_to_weight([alpha, j, i, beta], 0, diagonal = True, assume_symmetry = True)
    w2 = piece_to_weight([k, delta, gamma, i], 1, diagonal = False, assume_symmetry = True)
    w3 = piece_to_weight([eta, epsilon, k, j], 2, diagonal = False, assume_symmetry = True)
    return w1 * w2 * w3

def z_right(alpha, beta, gamma, delta, epsilon, eta, i, j, k):
    w1 = piece_to_weight([k, epsilon, delta, i], 0, diagonal = True, assume_symmetry = True)
    w2 = piece_to_weight([eta, k, j, alpha], 1, diagonal = False, assume_symmetry = True)
    w3 = piece_to_weight([j, i, gamma, beta], 2, diagonal = False, assume_symmetry = True)
    return w1 * w2 * w3


def solve_right(alpha, beta, gamma, delta, epsilon, eta):
    solutions = []
    Z = 0
    for i in [0, 1]:
        for j in [0, 1]:
            for k in [0, 1]:
                if check_right(alpha, beta, gamma, delta, epsilon, eta, i, j, k):
                    solutions.append([i, j, k])
                    Z = Z + z_right(alpha, beta, gamma, delta, epsilon, eta, i, j, k)
    # print("solutions: ", solutions)
    # print("Z = ", Z)
    return Z

def solve_left(alpha, beta, gamma, delta, epsilon, eta):
    solutions = []
    Z = 0
    for i in [0, 1]:
        for j in [0, 1]:
            for k in [0, 1]:
                if check_left(alpha, beta, gamma, delta, epsilon, eta, i, j, k):
                    solutions.append([i, j, k])
                    Z = Z + z_left(alpha, beta, gamma, delta, epsilon, eta, i, j, k)
    return Z
    # print("solutions: ", solutions)
    # print("Z = ", Z)    

if __name__ == '__main__':
    alpha = 1
    excluded = []
    for beta in [0, 1]:
        for gamma in [0, 1]:
            for delta in [0, 1]:
                for epsilon in [0, 1]:
                    for eta in [0, 1]:
                        if [alpha, beta, gamma, delta, epsilon, eta].count(1) % 2 == 0:
                            pm_str = ''.join(['+' if x == 1 else '-' for x in [alpha, beta, gamma, delta, epsilon, eta]])
                            zl = solve_left(alpha, beta, gamma, delta, epsilon, eta)
                            zr = solve_right(alpha, beta, gamma, delta, epsilon, eta)
                            if not (zl == 0 and zr == 0):
                                print((fg.green + "{}" + fg.rs + ": {} = {}").format(pm_str, zl, zr))
                            else:
                                print(fg.red + "excluded" + fg.rs + ": {}".format(pm_str))
