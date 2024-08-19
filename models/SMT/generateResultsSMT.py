import re
import os
from SMT_models import *
import json 

def parse_dzn_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    
    # Extracting m and n
    m = int(re.search(r'm = (\d+);', content).group(1))
    n = int(re.search(r'n = (\d+);', content).group(1))
    
    # Extracting l
    l = list(map(int, re.search(r'l = \[(.+?)\];', content).group(1).split(',')))
    
    # Extracting s
    s = list(map(int, re.search(r's = \[(.+?)\];', content).group(1).split(',')))
    
    # Extracting D
    D_match = re.search(r'D = \[\|(.+?)\|\];', content, re.DOTALL).group(1)
    D_lines = D_match.strip().split('\n')
    D = [list(map(int, re.split(r'\s*,\s*', line.strip().strip('|').strip()))) for line in D_lines]
    
    return m, n, l, s, D

def main(input_folder: str, output_folder: str, approach: str):
    output_approach_folder = os.path.join(output_folder, approach)
    os.makedirs(output_approach_folder, exist_ok=True)
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".dzn"):
            file_path = os.path.join(input_folder, file_name)
            m, n, l, s, D = parse_dzn_file(file_path)
            
            results = {}
            
            # Solve using solve_mcp
            result_mcp = solve_mcp_no_sym(m, n, l, s, D)
            if result_mcp:
                results["no_ysm"] = result_mcp
            
            # Solve using solve_mcp_dfs
            result_dfs = solve_mcp_sym(m, n, l, s, D)
            if result_dfs:
                results["sym"] = result_dfs
            
            # Solve using solve_mcp_bfs
            result_bfs = solve_mcp_sym_subtour_elim(m, n, l, s, D)
            if result_bfs:
                results["sym_subtour_elim"] = result_bfs
            
            instance_number = os.path.splitext(file_name)[0].split("inst")[-1]
            output_file_name = f"{instance_number}.json"
            output_file_path = os.path.join(output_approach_folder, output_file_name)
            
            with open(output_file_path, 'w') as output_file:
                json.dump(results, output_file, indent=2)
            
            print(f"Results saved to {output_file_path}")

# Set input and output folders
input_folder = r"./models/CP/InstancesDZN"  # Replace with the path to your input folder containing .dzn files
output_folder = r"./res"  # Replace with the path to your output folder for saving .json files

# Run the main function
main(input_folder, output_folder, approach="SMT")
