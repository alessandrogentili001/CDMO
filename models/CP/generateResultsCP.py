import minizinc
from pathlib import Path
from datetime import timedelta
import os
import json
import math
import time 
import re 

def solve_mcp(model_path, instance_path, time_limit=None):
    try:
        model_file = Path(model_path)
        instance_file = Path(instance_path)

        # Read and print model and data files for debugging
        with open(model_file, 'r') as f:
            model_content = f.read()
        #    print("Model Content:")
        #    print(model_content)

        with open(instance_file, 'r') as f:
            instance_content = f.read()
        #    print("Instance Content:")
        #    print(instance_content)

        # Create a MiniZinc model and load the data
        model = minizinc.Model()
        model.add_string(model_content)
        model.add_string(instance_content)

        # Create a MiniZinc solver instance (using Gecode)
        solver = minizinc.Solver.lookup("gecode")

        # Create an instance of the model for the solver
        instance = minizinc.Instance(solver, model)

        # Convert time_limit to timedelta if it's not None
        timeout = timedelta(seconds=time_limit) if time_limit is not None else None

        # Solve the instance
        start_time = time.time()
        try:
            print("Starting to solve...")
            result = instance.solve(timeout=timeout)
            print("Solve completed")
            solve_time = time.time() - start_time
            print("Solver status:", result.status)
            print("Solver statistics:", result.statistics)
        except minizinc.error.MiniZincError as e:
            print(f"MiniZinc Error: {e}")
            # ... [Keep the existing error handling] ...
            return None

        # Process and return the results
        if result.status in (minizinc.Status.OPTIMAL_SOLUTION, minizinc.Status.SATISFIED):
            # Check if the expected variables are in the result
            solution = result.solution
            print('show solution:')
            print(type(solution))
            print(solution)
            
            # Alternatively, iterate over the attributes to print their names and values
            for attr_name in dir(solution):
                if not attr_name.startswith('_'):  # Skip private attributes
                    attr_value = getattr(solution, attr_name)
                    print(f"{attr_name}: {attr_value}")

            if hasattr(solution, "objective") and hasattr(solution, "x") and hasattr(solution, "y"):
                # read attributes from the solution
                obj = result["objective"]
                assignments = result["x"]
                tour = result["y"]
                
                print(f'assignments: {assignments}')
                print(f'tour: {tour}')
                
                # write sol in the correct format for the result 
                sol = [[] for _ in range(len(tour))]
                origin = tour[0][0]
                for i, path in enumerate(tour):
                    for node in path:
                        if node != origin:  # Exclude origin node
                            sol[i].append(node)
                
                print(f'sol: {sol}')
                
                time_taken = math.floor(solve_time)
                optimal = result.status == minizinc.Status.OPTIMAL_SOLUTION

                return time_taken, optimal, obj, sol
            else:
                print("Missing expected variables in the result")
        else:
            print(f"Solving process ended with status: {result.status}")
            return 300, False, None, None

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return 300, False, None, None

def run_mcp_solver(input_folder, output_folder, approaches):
    # be sure that the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # loop over the files in the input folder
    for instance_file in sorted(os.listdir(input_folder)):
        if instance_file.startswith('.'):
            # skip hidden files
            continue
        
        instance_num = re.search(r'\d+', instance_file).group() 
        instance_path = os.path.join(input_folder, instance_file)
        results = {}
        
        for approach, model_path in approaches.items():
            print('-' * 50)
            print(f"run {approach} on instance {instance_num}")
            print('-' * 50)
            result = solve_mcp(model_path, instance_path, time_limit=300)
            
            # build json files 
            if result: # solution found 
                time_taken, optimal, obj, sol = result
                results[approach] = {
                    "time": time_taken,
                    "optimal": optimal,
                    "obj": obj,
                    "sol": sol
                }
            else: # no solution found 
                results[approach] = {
                    "time": 300,
                    "optimal": False,
                    "obj": None,
                    "sol": None
                }
        
        # complete outpute file for each instance
        file_path = os.path.join(output_folder, "CP")
        file_path = os.path.join(file_path, f"{instance_num}.json")
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2)

approaches = {
    "no_sym": r"./models/CP/CP_models/model0.mzn", # without simmetry breacking 
    "sym": r"./models/CP/CP_models/model1.mzn", # with simmetry breacking
    "sym_subtour_elim": r"./models/CP/CP_models/model2.mzn", # simmetry breacking + subtour elimination
    "sym_subtour_elim_heur": r"./models/CP/CP_models/model3.mzn", # simmetry breacking + subtour elimination + search heuristic
}

input_folder = r"./models/CP/InstancesDZN"
output_folder = r"./res"

# generate results 
run_mcp_solver(input_folder, output_folder, approaches)