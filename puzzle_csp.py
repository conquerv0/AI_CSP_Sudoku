# Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = caged_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the FunPuzz puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a FunPuzz grid (without cage constraints) built using only
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a FunPuzz grid (without cage constraints) built using only n-ary
      all-different constraints for both the row and column constraints.

3. caged_csp_model (worth 25/100 marks)
    - A model built using your choice of (1) binary binary not-equal, or (2)
      n-ary all-different constraints for the grid.
    - Together with FunPuzz cage constraints.

'''
from cspbase import *
import itertools
from itertools import combinations
import operator


# HELPER Method
def build_base_grid(fpuzz_grid):
    """
    A helper function that construct the common variables needed in both csp grid.
    :param fpuzz_grid:
    :return: dimension, domain, variables, csp_vars
    """
    dimension = fpuzz_grid[0][0]
    domain = [i + 1 for i in range(dimension)]

    # variables
    variables = []
    for row in domain:
        row_var = []
        for col in domain:
            row_var.append(Variable(f"{row * 10 + col}", domain))
        variables.append(row_var)

    csp_vars = []
    for row in variables:
        for var in row:
            csp_vars.append(var)

    return dimension, domain, variables, csp_vars


def find_cage_satisfy(cage_target, cage_operator, cage_size, domain):
    """
    :param cage_target:
    :param cage_operator:
    :param cage_size:
    :param domain:
    :return:
    """
    # combinations = list(itertools.combinations_with_replacement(range(1,n+1), len(cage)))
    candidates = set()
    combinations = list(itertools.product(domain, repeat=cage_size))

    for combination in combinations:
        cur_target = combination[0]
        for var in combination[1:]:
            cur_target = cage_operator(cur_target, var)
        if cur_target == cage_target:
            candidates.add(combination)

    satisfying = set()
    for candidate in candidates:
        satisfying.update(list(itertools.permutations(candidate)))
    satisfying = list(satisfying)

    return list(satisfying)


# CSP Build Method
def binary_ne_grid(fpuzz_grid):
    """
    Implement a model built using the binary not equal constraints.
    :param fpuzz_grid:
    :return: csp model, variables
    """
    # build base grid
    dimension, domain, variables, csp_vars = build_base_grid(fpuzz_grid)

    # constraints
    csp = CSP(name=f"{dimension}x{dimension} binary_ne_grid", vars=csp_vars)
    permutations = list(itertools.permutations(domain, 2))

    for i in range(dimension):
        # row constraint
        row_var = variables[i]
        row_con = combinations(row_var, 2)
        for binary in row_con:
            C = Constraint(f"binary_pair-{binary[0].name}-{binary[1].name}", binary)
            C.add_satisfying_tuples(permutations)
            csp.add_constraint(C)

        # col constraints
        col_var = []
        for var in variables:
            col_var.append(var[i])
        col_con = combinations(col_var, 2)
        for binary in col_con:
            C = Constraint(f"binary_pair-{binary[0].name}-{binary[1].name}", binary)
            C.add_satisfying_tuples(permutations)
            csp.add_constraint(C)

    return csp, variables


def nary_ad_grid(fpuzz_grid):
    """Implement a model built using the n-ary all different constraints.
    :param fpuzz_grid:
    :return: csp model, variables
    """
    # build base grid
    dimension, domain, variables, csp_vars = build_base_grid(fpuzz_grid)

    # constraints
    csp = CSP(name=f"{dimension}x{dimension} n-ary_ad_grid", vars=csp_vars)
    permutations = list(itertools.permutations(domain))

    for i in range(dimension):
        row, col = i // dimension, i % dimension
        # note we should add 1 for 1-indexing as cell starts from row 1, col 1.
        row_C = Constraint(f"row_ad-{row + 1}", variables[i])
        row_C.add_satisfying_tuples(permutations)
        csp.add_constraint(row_C)

        col_var = []
        for var in variables:
            col_var.append(var[i])
        col_C = Constraint(f"col_ad-{col + 1}", col_var)
        col_C.add_satisfying_tuples(permutations)
        csp.add_constraint(col_C)

    return csp, variables


def caged_csp_model(fpuzz_grid):
    """Implement a model built with binary non-equal and cage constraint.
    :param fpuzz_grid:
    :return: csp model, variables
    """
    # build base board
    csp, variables = nary_ad_grid(fpuzz_grid)
    dimension = fpuzz_grid[0][0]
    domain = [i + 1 for i in range(dimension)]
    csp.name = f"{dimension}x{dimension} caged_nary_ad_grid"

    # iterate through every cage of the fpuzz board
    for i, cage in enumerate(fpuzz_grid[1:]):
        # Base case: (value, target value)
        if len(cage) == 2:
            row, col = cage[0] // 10 - 1, cage[0] % 10 - 1
            cage_target = cage[1]
            # construct constraint and the satisfying tuples
            C = Constraint(f"cage-{i}-target-{cage_target}", [variables[row][col]])
            S = [(cage_target,)]

        # Complex case
        else:
            # construct cage constraint.
            cage_operator = cage.pop(-1)
            cage_target = cage.pop(-1)
            cage_variables = []
            for cell in cage:
                row, col = cell // 10 - 1, cell % 10 - 1
                cage_variables.append(variables[row][col])
            C = Constraint(f"cage-{i}-operator-{cage_operator}-target-{cage_target}", cage_variables)

            # find all satisfying tuples for the cage constraint.
            candidates = []
            combinations = list(itertools.product(domain, repeat=len(cage)))

            for combination in combinations:
                cur_result = combination[0]
                for var in combination[1:]:
                    match cage_operator:
                        case 0:
                            cur_result = operator.add(cur_result, var)
                        case 1:
                            cur_result = operator.sub(cur_result, var)
                        case 2:
                            cur_result = operator.floordiv(cur_result, var)
                        case 3:
                            cur_result = operator.mul(cur_result, var)

                if cur_result == cage_target:
                    candidates.append(combination)

            S = set()
            candidates = set(candidates)
            for candidate in candidates:
                permutations = itertools.permutations(candidate)
                S.update(list(permutations))
            S = list(S)

            # S = find_cage_satisfy(cage_target, cage_operator, len(cage), domain)

        C.add_satisfying_tuples(S)
        csp.add_constraint(C)

    return csp, variables
