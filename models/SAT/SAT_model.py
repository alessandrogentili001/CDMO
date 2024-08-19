from SAT_utils import *
import time
import sys

def solve_mcp(m, n, l, s, D, num_bits, enc, solver):
    
    print("trying encoding:", enc, "with solver:", solver)
    
    ''' CHOOSE ENCODINGS '''
    if enc=="heule":
        at_least_one=at_least_one_he
        at_most_one=at_most_one_he
        exactly_one=exactly_one_he
    elif enc=="bitwise":
        at_least_one=at_least_one_bw
        at_most_one=at_most_one_bw
        exactly_one=exactly_one_bw
    elif enc=="sequential":
        at_least_one=at_least_one_seq
        at_most_one=at_most_one_seq
        exactly_one=exactly_one_seq
        at_least_k=at_least_k_seq
        at_most_k=at_most_k_seq
        exactly_k=exactly_k_seq
        
    ''' INITIALIZE SOLVER '''
    S=Solver()
    start_time = time.time()
        
    ''' DECISION VARIABLES '''
    # Decision variables
    y = [[[Bool(f'y_{k}_{i}_{j}') for j in range(n+1)] for i in range(n+1)] for k in range(m)] # y[k][i][j] = 1 iff courier k travel from node i to node j
    u = [[Bool(f'u_{i}_{b}') for b in range(num_bits)] for i in range(n+1)] # subtour elimination variable
    
    ''' ADD CONSTRAINTS on y '''
    for k in range(m):
        pseudo_bool_vars = [If(y[k][i][j], s[j], 0) for i in range(n+1) for j in range(n)]
        S.add(Sum(pseudo_bool_vars) <= l[k])

    # Each item must be delivered exactly once
    for i in range(n):
        S.add(And(
            exactly_one([y[k][j][i] for k in range(m) for j in range(n+1)], name = f"delivery_to_{i}"),
            exactly_one([y[k][i][j] for k in range(m) for j in range(n+1)], name = f"delivery_from_{i}")
        ))

    # Start and end at depot
    depot = n
    for k in range(m):
        S.add(
            exactly_one([y[k][depot][i] for i in range(n)], name = f"from_depot_{k}")
        )
        S.add(
            exactly_one([y[k][i][depot] for i in range(n)], name = f"to_depot_{k}")
        )

    # Can't stay in the same node
    for k in range(m):
        for i in range(n+1):
            S.add(Not(y[k][i][i]))

    # Flow conservation
    for k in range(m):
        for i in range(n):
            bool_vars_from = [y[k][j][i] for j in range(n+1)]
            bool_vars_to = [y[k][i][j] for j in range(n+1)]
            S.add(Implies(exactly_one(bool_vars_from, name = f"flow_from_{k}_{i}"), exactly_one(bool_vars_to, name = f"flow_to_{k}_{i}")))
            
    ''' ADD SUB-TOUR ELIMINATION CONSTRAINT with boolean encoding '''
    # MTZ constraints with boolean encoding
    for k in range(m):
        # Constraint for the depot (node 0)
        for b in range(num_bits):
            S.add(u[depot][b] == False)  # Set depot position to 1

        for i in range(n):
            # Ensure position is between 2 and n+1 for non-depot nodes
            S.add(Sum([If(u[i][b], 1, 0) * 2**b for b in range(num_bits)]) >= 1)
            S.add(Sum([If(u[i][b], 1, 0) * 2**b for b in range(num_bits)]) <= n)
            
            for j in range(n):
                if i != j:
                    #S.add(Implies(y[k][i][j], lex_lesseq([u[k][i][b] for b in range(num_bits)], [u[k][j][b] for b in range(num_bits)])))
                    bool_vars_i = [If(u[i][b], 2**b, 0) for b in range(num_bits)]
                    bool_vars_j = [If(u[j][b], 2**b, 0) for b in range(num_bits)]
                    S.add(Implies(y[k][i][j], Sum(bool_vars_i) <= Sum(bool_vars_j)))
    
    print("Total umber of assertions in the model: ", len(S.assertions()))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Time to generate constraints: %.4f" % elapsed_time)
    print("-"*30, "\n")
        
    ''' SOLVE AND PRINT SOLUTION '''
    timeout=300000 #timeout of 5 minutes = 300 seconds = 300000 milliseconds
    remaining_time=timeout

    print("\nSOLVING WITH", str.upper(solver), "SOLVER,", "using", enc, "encoding\n")
    if solver!="cdcl":
        S.set(local_search=True, local_search_mode=solver, local_search_threads=12) # wsat and qsat are both variants of local search
    else:
        S.set(threads=12)
    #initialization
    total_tries = 0
    start_time = time.time()
    max_bad_tries = 250
    num_bad_tries = 0
    elapsed_time = 0
    best_sol = sys.maxsize
    is_timeout = False
    is_sat = False
    is_optimal = False
    full_exploration = False
    S.push()
    # run untill we reach time limit  
    while elapsed_time<300:
        remaining_time=(timeout/1000)-elapsed_time 
        S.set("timeout", int(remaining_time)*1000)
            
        ''' CHECK SOLVER '''
        print("we are checking the solver...")
        if S.check() == sat:
            print('sat')
            end_time = time.time()
            is_sat = True # if any solution has been found
                
            # update time 
            elapsed_time = end_time - start_time
            remaining_time = timeout - elapsed_time
            
            # extract a model from the solver 
            model = S.model()
            total_tries += 1
            
            ''' EXTRACT SOLUTION '''
                        
            # Initialize the y_matrix
            y_matrix = [[[False for _ in range(n+1)] for _ in range(n+1)] for _ in range(m)]

            # Extract y values from the model
            for k in range(m):
                for i in range(n+1):
                    for j in range(n+1):
                        if model[y[k][i][j]]:
                            y_matrix[k][i][j] = True
            
            input("press enter to continue")  
            print("y: ", y_matrix)
            input("press enter to continue")
            
            y_is_wrong = False

            # convert y_matrix to a list of routes for each courier, compute distances in the meantime
            routes = []
            distances = []
            for k in range(m):
                route = []
                distance = 0
                current = depot
                max_iterations = n + 1  # Maximum possible number of nodes to visit
                for _ in range(max_iterations):
                    next_node = next((j for j in range(n+1) if y_matrix[k][current][j]), None)
                    if next_node is None:
                        print("y is wrong!!!")
                        y_is_wrong = True
                        break
                    if next_node == depot:
                        distance += D[current][depot]
                        break
                    else:
                        distance += D[current][next_node]
                        route.append(next_node)  # Keep 0-indexing, adjust later if needed
                        current = next_node
                
                routes.append(route)
                distances.append(distance)
            
            ''' CHECK THE CORRECTNESS OF THE SOLUTION '''
            # check the length of the total route
            tot_length = sum([len(route) for route in routes])
            if tot_length < n:
                print("y is wrong!!!")
                y_is_wrong = True

            # Adjust node indexing
            routes = [[node + 1 for node in route] for route in routes]

            solution = routes                
            print("distances: ", distances)
            print("solution: ", solution)

            ''' CHECK OPTIMAL SOLUTION '''
            max_distance = max(distances)
            print("max distance: ", max_distance)
            if max_distance < best_sol and not(y_is_wrong): #"good try" case
                # save best performing model when found
                best_sol = max_distance
                opt_sol_vect = solution
                num_bad_tries = 0
            else: #"bad try" case
                num_bad_tries += 1
                
            if num_bad_tries >= max_bad_tries:
                print("ending search: no improvement in", max_bad_tries, "tries. total tries = ", total_tries, " best = ", best_sol)
                is_optimal = True # assuming this means it's optimal
                break

            # Add constraint to avoid the current solution --> if all the assignment are the same, then the order of deliveries must change 
            block_solution = Or([y[k][i][j] != model[y[k][i][j]] for i in range(n+1) for j in range(n+1) for k in range(m)])

            S.add(block_solution)
        
            print(f"tries: {num_bad_tries}/{max_bad_tries}. best = {best_sol}", end = "")
            print("\r", end = "")
                
        else:
            print('unsat')
            if is_sat: # if all solutions have been explored, the best one is surely optimal
                print("premature exit (all solutions explored). total tries = ", total_tries, "best = ", best_sol)
                full_exploration=True
                is_optimal=True
                break
            if not is_sat: # if no solution has been found in the time limit, the output is empty
                print("timeout")
                end_time = time.time()
                elapsed_time = end_time - start_time
                is_timeout = True
                opt_sol_vect = None                    
                best_sol = None
                is_optimal = False
                break
    
    result = {
        "time": math.ceil(elapsed_time),
        "optimal": is_optimal,
        "obj": best_sol,
        "sol": opt_sol_vect
    }
    return result 

    
    
