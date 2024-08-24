from z3 import *
import logging
import json
import os
import time
from typing import List, Dict, Any
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def solve_mcp_sym_subtour_elim(m: int, n: int, l: List[int], s: List[int], D: List[List[int]], timeout: int = 300000) -> Dict[str, Any]:
    optimizer = Optimize()
    optimizer.set("timeout", timeout)

    x, y, u, distances, max_distance = define_variables(m, n)
    D_func = define_distance_function(optimizer, n, D)

    add_x_constraints(optimizer, m, n, x, l, s)
    add_y_constraints(optimizer, m, n, x, y)
    add_distance_constraints(optimizer, m, n, y, distances, max_distance, D_func)
    add_symmetry_breaking_constraints(optimizer, m, n, l, x)
    add_subtour_elimination_constraints(optimizer, m, n, x, y, u)

    optimizer.minimize(Select(max_distance, 0))

    start_time = time.time()
    if optimizer.check() == sat:
        end_time = time.time()
        runtime = int(end_time - start_time)
        runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
        optimal = runtime < 300  # If runtime is less than 300, it's optimal
        solution = extract_solution(optimizer.model(), m, n, x, y, distances, max_distance)
        solution.update({"time": runtime, "optimal": optimal})
        return solution
    else:
        end_time = time.time()
        runtime = int(end_time - start_time)
        runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
        return {"time": 300, "optimal": False, "obj": False, "sol": False}
    
def solve_mcp_no_sym(m: int, n: int, l: List[int], s: List[int], D: List[List[int]], timeout: int = 300000) -> Dict[str, Any]:
    optimizer = Optimize()
    optimizer.set("timeout", timeout)

    x, y, u, distances, max_distance = define_variables(m, n)
    D_func = define_distance_function(optimizer, n, D)

    add_x_constraints(optimizer, m, n, x, l, s)
    add_y_constraints(optimizer, m, n, x, y)
    add_distance_constraints(optimizer, m, n, y, distances, max_distance, D_func)
    # add_symmetry_breaking_constraints(optimizer, m, n, l, x)
    # add_subtour_elimination_constraints(optimizer, m, n, x, y, u)

    optimizer.minimize(Select(max_distance, 0))

    start_time = time.time()
    if optimizer.check() == sat:
        end_time = time.time()
        runtime = int(end_time - start_time)
        runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
        optimal = runtime < 300  # If runtime is less than 300, it's optimal
        solution = extract_solution(optimizer.model(), m, n, x, y, distances, max_distance)
        solution.update({"time": runtime, "optimal": optimal})
        return solution
    else:
        end_time = time.time()
        runtime = int(end_time - start_time)
        runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
        return {"time": 300, "optimal": False, "obj": False, "sol": False}
        
def solve_mcp_sym(m: int, n: int, l: List[int], s: List[int], D: List[List[int]], timeout: int = 300000) -> Dict[str, Any]:
    optimizer = Optimize()
    optimizer.set("timeout", timeout)

    x, y, u, distances, max_distance = define_variables(m, n)
    D_func = define_distance_function(optimizer, n, D)

    add_x_constraints(optimizer, m, n, x, l, s)
    add_y_constraints(optimizer, m, n, x, y)
    add_distance_constraints(optimizer, m, n, y, distances, max_distance, D_func)
    add_symmetry_breaking_constraints(optimizer, m, n, l, x)
    # add_subtour_elimination_constraints(optimizer, m, n, x, y, u)

    optimizer.minimize(Select(max_distance, 0))

    start_time = time.time()
    if optimizer.check() == sat:
        end_time = time.time()
        runtime = int(end_time - start_time)
        runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
        optimal = runtime < 300  # If runtime is less than 300, it's optimal
        solution = extract_solution(optimizer.model(), m, n, x, y, distances, max_distance)
        solution.update({"time": runtime, "optimal": optimal})
        return solution
    else:
        end_time = time.time()
        runtime = int(end_time - start_time)
        runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
        return {"time": 300, "optimal": False, "obj": False, "sol": False}
        
'''
def solve_mcp_dfs(m: int, n: int, l: List[int], s: List[int], D: List[List[int]], timeout: int = 300000) -> Dict[str, Any]:
    optimizer = Optimize()
    optimizer.set("timeout", timeout)

    # Define variables
    x, y, u, distances, max_distance = define_variables(m, n)
    D_func = define_distance_function(optimizer, n, D)

    # Add constraints
    add_x_constraints(optimizer, m, n, x, l, s)
    add_y_constraints(optimizer, m, n, x, y)
    add_distance_constraints(optimizer, m, n, y, distances, max_distance, D_func)
    add_symmetry_breaking_constraints(optimizer, m, n, l, x)
    add_subtour_elimination_constraints(optimizer, m, n, x, y, u)

    # Auxiliary objective variable
    #objective = Int('objective')

    # Define and add minimization constraint
    max_distance_expr = Select(max_distance, 0)
    max_distance_handle = optimizer.minimize(max_distance_expr)
    print('max distance handle: ', max_distance_handle)

    # Custom search strategy (depth-first with dom_w_deg heuristic)
    optimizer.set("priority", "dfs")

    # Geometric restart strategy
    restart_count = 0
    max_restarts = 500
    restart_increment_factor = 2

    start_time = time.time()
    while True:
        if optimizer.check() == sat:
            end_time = time.time()
            runtime = int(end_time - start_time)
            runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
            optimal = runtime < 300  # If runtime is less than 300, it's optimal
            solution = extract_solution(optimizer.model(), m, n, x, y, distances, max_distance)
            solution.update({"time": runtime, "optimal": optimal})
            return solution
        else:
            # Check if we have exceeded the maximum restarts
            if restart_count >= max_restarts:
                break

            restart_count += 1
            current_best = Int('current_best')
            optimizer.add(current_best == max_distance_expr)
            optimizer.add(max_distance_handle <= current_best - 1)

            # Increase the restart limit geometrically
            optimizer.set("restart_incremental", restart_increment_factor)

    # If no solution found within timeout or maximum restarts
    end_time = time.time()
    runtime = int(end_time - start_time)
    runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
    return {"time": runtime, "optimal": False, "obj": -1, "sol": [[] for _ in range(m)]}

def solve_mcp_bfs(m: int, n: int, l: List[int], s: List[int], D: List[List[int]], timeout: int = 300000) -> Dict[str, Any]:
    optimizer = Optimize()
    optimizer.set("timeout", timeout)

    # Define variables
    x, y, u, distances, max_distance = define_variables(m, n)
    D_func = define_distance_function(optimizer, n, D)

    # Add constraints
    add_x_constraints(optimizer, m, n, x, l, s)
    add_y_constraints(optimizer, m, n, x, y)
    add_distance_constraints(optimizer, m, n, y, distances, max_distance, D_func)
    add_symmetry_breaking_constraints(optimizer, m, n, l, x)
    add_subtour_elimination_constraints(optimizer, m, n, x, y, u)

    # Auxiliary objective variable
    objective = Int('objective')

    # Define and add minimization constraint
    max_distance_expr = Select(max_distance, 0)
    optimizer.add(objective == max_distance_expr)
    optimizer.minimize(objective)

    # Custom search strategy (depth-first with dom_w_deg heuristic)
    optimizer.set("priority", "bfs")

    # Geometric restart strategy
    restart_count = 0
    max_restarts = 500
    restart_increment_factor = 2

    start_time = time.time()
    while True:
        if optimizer.check() == sat:
            end_time = time.time()
            runtime = int(end_time - start_time)
            runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
            optimal = runtime < 300  # If runtime is less than 300, it's optimal
            solution = extract_solution(optimizer.model(), m, n, x, y, distances, max_distance)
            solution.update({"time": runtime, "optimal": optimal})
            return solution
        else:
            # Check if we have exceeded the maximum restarts
            if restart_count >= max_restarts:
                break

            restart_count += 1
            optimizer.add_soft(max_distance_expr <= optimizer.lower(max_distance_expr) - 1)

            # Increase the restart limit geometrically
            optimizer.set("restart_incremental", restart_increment_factor)

    # If no solution found within timeout or maximum restarts
    end_time = time.time()
    runtime = int(end_time - start_time)
    runtime = min(runtime, 300)  # Ensure runtime does not exceed 300
    return {"time": runtime, "optimal": False, "obj": -1, "sol": [[] for _ in range(m)]}
'''

def define_variables(m: int, n: int) -> tuple:
    x = [Array(f'x_{k}', IntSort(), IntSort()) for k in range(m)]
    y = [Array(f'y_{k}', IntSort(), IntSort()) for k in range(m)]
    u = [Array(f'u_{k}', IntSort(), IntSort()) for k in range(m)]
    distances = Array(f'distances', IntSort(), IntSort())
    max_distance = Array('max_distance', IntSort(), IntSort())
    return x, y, u, distances, max_distance

def define_distance_function(optimizer: Optimize, n: int, D: List[List[int]]) -> FuncDeclRef:
    D_func = Function('D_func', IntSort(), IntSort(), IntSort())
    for i in range(n+1):
        for j in range(n+1):
            optimizer.add(D_func(i, j) == D[i][j])
    return D_func

def add_x_constraints(optimizer: Optimize, m: int, n: int, x: List[ArrayRef], l: List[int], s: List[int]):
    for k in range(m):
        for i in range(n):
            optimizer.add(And(Select(x[k], i) <= 1, Select(x[k], i) >= 0)) # range
        optimizer.add(Sum([If(Select(x[k], i) == 1, s[i], 0) for i in range(n)]) <= l[k]) # capacity
        optimizer.add(Sum([If(Select(x[k], i) == 1, 1, 0) for i in range(n)]) > 0) # min delivery

    for i in range(n):
        optimizer.add(Sum([If(Select(x[k], i) == 1, 1, 0) for k in range(m)]) == 1) # each item must be delivered exactly once 

    for k1 in range(m-1):
        for k2 in range(k1+1, m):
            if l[k1] <= l[k2]:
                optimizer.add(Sum([If(Select(x[k1], i) == 1, s[i], 0) for i in range(n)]) <= 
                              Sum([If(Select(x[k2], i) == 1, s[i], 0) for i in range(n)]))
            else:
                optimizer.add(Sum([If(Select(x[k1], i) == 1, s[i], 0) for i in range(n)]) >= 
                              Sum([If(Select(x[k2], i) == 1, s[i], 0) for i in range(n)]))

def add_y_constraints(optimizer: Optimize, m: int, n: int, x: List[ArrayRef], y: List[ArrayRef]):
    for k in range(m):
        for t in range(n+2):
            optimizer.add(And(Select(y[k], t) >= 0, Select(y[k], t) <= n)) # range
        optimizer.add(And(Select(y[k], 0) == n, Select(y[k], n+1) == n)) # start and end
        # connecting x and y 
        for i in range(n):
            optimizer.add(Or(Sum([If(Select(y[k], t) == i, 1, 0) for t in range(1, n+1)]) == 1, Not(Select(x[k], i) == 1))) 
        for t in range(1, n+1):
            optimizer.add(Implies(Select(y[k], t) == n, Select(y[k], t+1) == n))
    # avoid repetitions in tours 
    for i in range(n):
        optimizer.add(Sum([If(Select(y[k], t) == i, 1, 0) for k in range(m) for t in range(1, n+1)]) == 1)

def add_distance_constraints(optimizer: Optimize, m: int, n: int, y: List[ArrayRef], distances: ArrayRef, max_distance: ArrayRef, D_func: FuncDeclRef):
    for k in range(m):
        optimizer.add(Select(distances, k) == Sum([D_func(Select(y[k], t), Select(y[k], t+1)) for t in range(n+1)]))
        optimizer.add(Select(max_distance, 0) >= Select(distances, k))
    optimizer.add(Or([Select(max_distance, 0) == Select(distances, k) for k in range(m)]))

def add_symmetry_breaking_constraints(optimizer: Optimize, m: int, n: int, l: List[int], x: List[ArrayRef]):
    for k1 in range(m-1):
        for k2 in range(k1 + 1, m):
            if l[k1] == l[k2]: # implement lexicographic ordering for couriers with the same load capacity  
                for i in range(n):
                    optimizer.add(Implies(And([Select(x[k2], j) == Select(x[k1], j) for j in range(i)]), x[k1][i] <= x[k2][i])) 

def add_subtour_elimination_constraints(optimizer: Optimize, m: int, n: int, x: List[ArrayRef], y: List[ArrayRef], u: List[ArrayRef]):
    for k in range(m):
        # Set the range for u variables
        for i in range(n + 1):  # Include depot node n
            optimizer.add(0 <= Select(u[k], i))
            optimizer.add(Select(u[k], i) <= n)

        # MTZ constraints
        for i in range(n):
            for j in range(n):
                if i != j:
                    optimizer.add(Implies(Select(y[k], i) == j,
                                  Select(u[k], i) - Select(u[k], j) + (n+1)*Select(x[k], i) <= n))

        # Ensure the depot (node n) is visited first
        optimizer.add(Select(u[k], n) == 0)

        # Ensure other nodes are visited after the depot
        for i in range(n):  # Exclude depot node n
            optimizer.add(Implies(Select(x[k], i) > 0, Select(u[k], i) >= 1))

        # Ensure u values are distinct for visited nodes
        optimizer.add(Distinct([If(Select(x[k], i) > 0, Select(u[k], i), - i) for i in range(n+1)]))

def extract_solution(model: ModelRef, m: int, n: int, x: List[ArrayRef], y: List[ArrayRef], distances: ArrayRef, max_distance: ArrayRef) -> Dict[str, Any]:
    result = {
        "time": -1,
        "optimal": True,
        "obj": int(model.evaluate(Select(max_distance, 0)).as_string()),
        "sol": [], 
            }
    
    for k in range(m):
        delivery_sequence = []
        for t in range(1, n+1):
            delivery_point = model.evaluate(y[k][t]).as_long()
            if delivery_point < n:  # Ignore depot which is represented as n
                delivery_sequence.append(delivery_point + 1)  # Adjust index to 1-based
        result["sol"].append(delivery_sequence)
    return result
