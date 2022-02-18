#Look for #IMPLEMENT tags in this file.
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

def binary_ne_grid(fpuzz_grid):
    # domain
    dimension = fpuzz_grid[0][0]
    domain = [i+1 for i in range(dimension)]

    # variables
    variables = [[Variable(str(i*10+j), domain) for i in domain] for j in domain]
    csp_vars = []
    for row in variables:
        for var in row:
            csp_vars.append(var)

    # constraints
    csp = CSP(name=f"{dimension}x{dimension} binary_ne_grid", vars=csp_vars)
    permutations = list(itertools.permutations(domain, 2))

    for i in range(dimension):
        row_var = variables[i]
        for binary in itertools.combinations(row_var, 2):
            C = Constraint(f"R-{binary[0].name}-{binary[1].name}", binary)
            C.add_satisfying_tuples(permutations)
            csp.add_constraint(C)

        col_var = []
        for var in variables:
            col_var.append(var[i])

        for binary in itertools.combinations(col_var, 2):
            C = Constraint(f"C-{binary[0].name}-{binary[1].name}", binary)
            C.add_satisfying_tuples(permutations)
            csp.add_constraint(C)

    return csp, variables

def nary_ad_grid(fpuzz_grid):
    ##IMPLEMENT
    pass


def caged_csp_model(fpuzz_grid):
    ##IMPLEMENT
    pass