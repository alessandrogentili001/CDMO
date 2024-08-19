import gurobipy as gp
from gurobipy import GRB, quicksum
import os, json, time, math

def make_json(filename, solvers, times, objs, solutions, is_optimal_vec):
    solv = {}
    for solver, time, obj, solution, is_optimal in zip(solvers, times, objs, solutions, is_optimal_vec):
        data = {
            'time': int(time),
            'optimal': is_optimal,
            'obj': obj,
            'sol': solution
        }
        solv[solver] = data
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as outfile:
        json.dump(solv, outfile)
        print(f"\nJSON file {filename} created successfully")

def retrieve_elements(middle, first):
    for i in middle:
        if i[0] == first:
            return i

def compute_routes(x):
    routes = {}
    for (i, j, k), var in x.items():
        if var.x == 1:
            if k not in routes:
                routes[k] = [(i, j)]
            else:
                routes[k].append((i, j))
    for k in routes:
        start = next((t for t in routes[k] if t[0] == 0), None)
        end = next((t for t in routes[k] if t[1] == 0), None)
        if start and end:
            routes[k].remove(start)
            routes[k].remove(end)
            middle = [t for t in routes[k] if t != start and t != end]
            sorted_route = []
            token = start[1]
            for _ in routes[k]:
                element = retrieve_elements(middle, token)
                sorted_route.append(element)
                token = element[1]
            routes[k] = [start] + sorted_route + [end]
    return routes

def compute_items_carried(x, n):
    items_carried = {}
    for (i, j, k), var in x.items():
        if var.x == 1:
            if k not in items_carried:
                items_carried[k] = [i]
            elif i != n+1:
                items_carried[k].append(i)
    return items_carried

def compute_total_distance(x, D):
    total_distance = {}
    for (i, j, k), var in x.items():
        if var.X == 1:
            if k not in total_distance:
                total_distance[k] = D[i-1][j-1]
            else:
                total_distance[k] += D[i-1][j-1]
    return total_distance

params = {
    "WLSACCESSID": '68ba24c3-8a34-4802-99d9-24d15bc93843',
    "WLSSECRET": '6bba51b0-93a7-4823-9d8f-f1dbafea48a2',
    "LICENSEID": 2532591,
}
env = gp.Env(params=params)

for i in range(1, 22):
    instance = f"{i:02d}"
    file_name = f"/project/Instances/inst{instance}.dat"

    with open(file_name, "r") as f:
        m = int(f.readline())
        n = int(f.readline())
        l = [int(x) for x in f.readline().split()]
        si = [int(x) for x in f.readline().split()]
        D = [[int(x) for x in f.readline().split()] for _ in range(n+1)]

    ListCustomers = list(range(1, n+1))
    Deposit = [0] + ListCustomers
    ListCouriers = list(range(1, m+1))

    model = gp.Model("VRP", env=env)
    x = model.addVars(Deposit, Deposit, ListCouriers, vtype=GRB.BINARY, name="x_ijk")
    y = model.addVars(Deposit, ListCouriers, vtype=GRB.BINARY, name="y_ik")
    u = model.addVars(ListCustomers, ListCouriers, vtype=GRB.CONTINUOUS, name="u_ik")
    max_distance = model.addVar(name='max_distance')

    model.setObjective(max_distance, sense=GRB.MINIMIZE)
    
    # Constraint: Maximum distance constraint for each courier
    for k in ListCouriers:
        model.addConstr(quicksum(x[i, j, k] * D[i-1][j-1] for i in Deposit for j in Deposit) <= max_distance)

    # Constraint: Each customer must be visited exactly once by exactly one courier
    for i in ListCustomers:
        model.addConstr(quicksum(y[i, k] for k in ListCouriers) == 1)
        model.addConstr(quicksum(x[i, j, k] for j in Deposit for k in ListCouriers) == 1)
        
    # Constraint: Each courier must start from and return to the depot (node 0)
    for j in ListCustomers:
        model.addConstr(quicksum(x[i, j, k] for i in Deposit for k in ListCouriers) == 1)

    # Constraint: All ListCouriers must start from the depot
    model.addConstr(quicksum(y[0, k] for k in ListCouriers) == m)

    # Constraint: Capacity constraint for each courier
    for k in ListCouriers:
        model.addConstr(quicksum(y[i, k] * si[i-1] for i in ListCustomers) <= l[k-1])
        model.addConstr(quicksum(x[j, j, k] for j in Deposit) == 0)
        model.addConstr(quicksum(x[i, 0, k] for i in Deposit) == 1)

    # Constraint: Flow conservation constraint
    for i in ListCustomers:
        for k in ListCouriers:
            model.addConstr(quicksum(x[i, j, k] for j in Deposit) == quicksum(x[j, i, k] for j in Deposit))
            model.addConstr(quicksum(x[j, i, k] for j in Deposit) == y[i, k])

    # Constraint: Symmetry breaking constraints
    for k in ListCouriers:
        for j in Deposit:
            model.addConstr(quicksum(x[i, j, k] for i in Deposit) == quicksum(x[i, j, k] for i in Deposit))

    # Constraint: Subtour elimination constraints (Miller-Tucker-Zemlin)
    for k in ListCouriers:
        for i in ListCustomers:
            for j in ListCustomers:
                if i != j:
                    model.addConstr(u[i, k] - u[j, k] + n * x[i, j, k] <= n - 1)

    model.setParam(GRB.Param.TimeLimit, 300)

    # Solve the model and measure elapsed time
    start_time = time.time()
    model.optimize()
    elapsed_time = time.time() - start_time 

    # Handle optimization results
    if model.status == GRB.OPTIMAL:
        print("Optimal solution found!")
    elif model.status == GRB.TIME_LIMIT:
        print("Optimization reached the time limit.")
    else:
        print("Optimization did not converge to an optimal solution.")
        
    # Process and output results to JSON 
    # json_file_path = f"/Users/lorenzo/Desktop/project-2/res/MIP/{instance}.json"
    json_file_path = f"/project/res/MIP/{instance}.json"
    opt = model.status == GRB.OPTIMAL

    if opt:
        routes = compute_routes(x)
        for k, route in sorted(routes.items(), key=lambda item: item[0]):
            print(f"Courier {k} route: {route}")

        sol = [[routes[k][i][0] for i in range(1, len(routes[k]))] for k in sorted(routes.keys())]
        print("solution vector:", sol)

        items_carried = compute_items_carried(x, n)
        for k, items in items_carried.items():
            items.remove(0)
            print(f"Courier {k} carries items: {items}")

        total_distance = compute_total_distance(x, D)
        for k, distance in total_distance.items():
            print(f"Total distance traveled by vehicle {k}: {distance}")

        make_json(json_file_path, ["Gurobi"], [elapsed_time], [model.objVal], [sol], [opt])
    else:
        make_json(json_file_path, ["Gurobi"], [300], [math.inf], [], [opt])
