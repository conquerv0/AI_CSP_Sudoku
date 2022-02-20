#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.

'''This file will contain different constraint propagators to be used within 
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method). 
      bt_search NEEDS to know this in order to correctly restore these 
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been 
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated 
        constraints) 
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope 
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
   '''


def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no 
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def fc_check(C, x, pruned):
    """
    Perform forward checking on constraint C with all its variables already assigned,
    except for variable x.
    :param C: a constraint variable
    :param x: variable x
    :param pruned: pruned values
    :return: True if no DWO occurs, False otherwise; along with a list of pruned values.
    """
    cur_dom = x.cur_domain()
    for d in cur_dom:
        # loop over members of domain, assign d to x
        x.assign(d)
        variables = C.get_scope()
        values = []
        for var in variables:
            var_val = var.get_assigned_value()
            values.append(var_val)
        # check if values falsifies C, prune d
        if not C.check(values):
            x.prune_value(d)
            pruned.append((x, d))
        x.unassign()
    # DWO if domain size is 0, return False
    if x.cur_domain_size() == 0:
        return False, pruned
    return True, pruned


def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return '''
    if not newVar:
        cons = csp.get_all_cons()
    else:
        cons = csp.get_cons_with_var(newVar)

    pruned = []
    for C in cons:
        # C only has one unassigned var x in scope
        if C.get_n_unasgn() == 1:
            x = C.get_unasgn_vars()[0]
            fc_check_ok, pruned = fc_check(C, x, pruned)
            if not fc_check_ok:
                return False, pruned
    # All constraints were ok
    return True, pruned


def gac_enforce(GAC_queue, nGAC_queue, pruned):
    """
    :param GAC_queue:
    :param nGAC_queue:
    :return: True if no DWO occurs, False otherwise; along with a list of pruned values.
    """
    while GAC_queue:
        C = GAC_queue.pop(0)
        nGAC_queue.append(C)
        for var in C.get_scope():
            for d in var.cur_domain():
                # Find an assignment A for all other var in scope(c) s.t. C(AUV=d) is True
                if not C.has_support(var, d):
                    var.prune_value(d)
                    pruned.append((var, d))

                    # DWO occurs, exit immediately
                    if var.cur_domain_size() == 0:
                        GAC_queue.clear()
                        return False, pruned
                    else:
                        # push all constraint C' s.t. var in scope(C') and C' not in GAC_queue
                        for c_prime in nGAC_queue:
                            if var in c_prime.get_scope():
                                GAC_queue.append(c_prime)
                                nGAC_queue.remove(c_prime)

    # While loop exited without DWO
    return True, pruned


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    if not newVar:
        GAC_queue = csp.get_all_cons()
        nGAC_queue = []
    else:
        GAC_queue = csp.get_cons_with_var(newVar)
        nGAC_queue = [c for c in csp.get_all_cons() if c not in GAC_queue]

    pruned = []
    GAC_enforce_ok, pruned = gac_enforce(GAC_queue, nGAC_queue, pruned)
    if not GAC_enforce_ok:
        return False, pruned
    return True, pruned
