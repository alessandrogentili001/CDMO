import json, os, time, math
from MIP_model import create_model, compute_routes, compute_items_carried, compute_total_distance
import gurobipy as gp
from gurobipy import GRB, quicksum

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

params = {
    "WLSACCESSID": '68ba24c3-8a34-4802-99d9-24d15bc93843',
    "WLSSECRET": '6bba51b0-93a7-4823-9d8f-f1dbafea48a2',
    "LICENSEID": 2532591,
}
env = gp.Env(params=params)

for i in range(1, 22):
    instance = f"{i:02d}"
    file_name = f"Instances/inst{instance}.dat"

    with open(file_name, "r") as f:
        m = int(f.readline())
        n = int(f.readline())
        l = [int(x) for x in f.readline().split()]
        si = [int(x) for x in f.readline().split()]
        D = [[int(x) for x in f.readline().split()] for _ in range(n+1)]

    instance_data = (m, n, l, si, D)
    model, x, u = create_model(instance_data, env)

    model.setParam(GRB.Param.TimeLimit, 300)

    start_time = time.time()
    model.optimize()
    elapsed_time = time.time() - start_time

    json_file_path = f"res/MIP/{instance}.json"
    opt = model.status == GRB.OPTIMAL

    if opt:
        routes = compute_routes(x)
        sol = [[routes[k][i][0] for i in range(1, len(routes[k]))] for k in sorted(routes.keys())]

        items_carried = compute_items_carried(x, n)
        for k, items in items_carried.items():
            items.remove(0)

        total_distance = compute_total_distance(x, D)

        make_json(json_file_path, ["Gurobi"], [elapsed_time], [model.objVal], [sol], [opt])
    else:
        make_json(json_file_path, ["Gurobi"], [300], [math.inf], [], [opt])
