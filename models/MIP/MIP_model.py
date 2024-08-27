import gurobipy as gp
from gurobipy import GRB, quicksum

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

def create_model(instance_data, env):
    m, n, l, si, D = instance_data

    ListCustomers = list(range(1, n+1))
    Deposit = [0] + ListCustomers
    ListCouriers = list(range(1, m+1))

    model = gp.Model("VRP", env=env)
    x = model.addVars(Deposit, Deposit, ListCouriers, vtype=GRB.BINARY, name="x_ijk")
    y = model.addVars(Deposit, ListCouriers, vtype=GRB.BINARY, name="y_ik")
    u = model.addVars(ListCustomers, ListCouriers, vtype=GRB.CONTINUOUS, name="u_ik")
    max_distance = model.addVar(name='max_distance')

    model.setObjective(max_distance, sense=GRB.MINIMIZE)

    # Constraints
    for k in ListCouriers:
        model.addConstr(quicksum(x[i, j, k] * D[i-1][j-1] for i in Deposit for j in Deposit) <= max_distance)

    for i in ListCustomers:
        model.addConstr(quicksum(y[i, k] for k in ListCouriers) == 1)
        model.addConstr(quicksum(x[i, j, k] for j in Deposit for k in ListCouriers) == 1)

    for j in ListCustomers:
        model.addConstr(quicksum(x[i, j, k] for i in Deposit for k in ListCouriers) == 1)

    model.addConstr(quicksum(y[0, k] for k in ListCouriers) == m)

    for k in ListCouriers:
        model.addConstr(quicksum(y[i, k] * si[i-1] for i in ListCustomers) <= l[k-1])
        model.addConstr(quicksum(x[j, j, k] for j in Deposit) == 0)
        model.addConstr(quicksum(x[i, 0, k] for i in Deposit) == 1)

    for i in ListCustomers:
        for k in ListCouriers:
            model.addConstr(quicksum(x[i, j, k] for j in Deposit) == quicksum(x[j, i, k] for j in Deposit))
            model.addConstr(quicksum(x[j, i, k] for j in Deposit) == y[i, k])

    for k in ListCouriers:
        for j in Deposit:
            model.addConstr(quicksum(x[i, j, k] for i in Deposit) == quicksum(x[i, j, k] for i in Deposit))

    for k in ListCouriers:
        for i in ListCustomers:
            for j in ListCustomers:
                if i != j:
                    model.addConstr(u[i, k] - u[j, k] + n * x[i, j, k] <= n - 1)

    return model, x, u
