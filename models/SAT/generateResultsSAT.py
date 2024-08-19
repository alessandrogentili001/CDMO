from SAT_utils import *
from SAT_model import *
import os

def main(input_folder: str, output_folder: str, approaches: dict, folder = "SAT"):
    output_approach_folder = os.path.join(output_folder, folder)
    os.makedirs(output_approach_folder, exist_ok=True)
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".dzn"):
            file_path = os.path.join(input_folder, file_name)
            m, n, l, s, D, num_bits = parse_dzn_file(file_path)

            results = {}
            
            for approach_name, approach_config in approaches.items():
                encoding = approach_config['encoding']
                solver = approach_config['solver']
                
                # Solve using solve_mcp
                result_mcp = solve_mcp(m, n, l, s, D, num_bits, encoding, solver)
                if result_mcp:
                    results[approach_name] = result_mcp
            
            instance_number = os.path.splitext(file_name)[0].split("inst")[-1]
            output_file_name = f"{instance_number}.json"
            output_file_path = os.path.join(output_approach_folder, output_file_name)
            
            with open(output_file_path, 'w') as output_file:
                json.dump(results, output_file, indent=2)
            

# Set input and output folders
input_folder = r"./models/CP/InstancesDZN"  # Replace with the path to your input folder containing .dzn files
output_folder = r"./res"  # Replace with the path to your output folder for saving .json files

# set parameters for the model  
encodings = ["sequential" ,"heule", "bitwise"]
solvers = [ "cdcl", "wsat"] 
approaches = {
    "cdcl_seq":{'encoding': 'sequential', 'solver': 'cdcl'},
    "cdcl_he":{'encoding':'heule', 'solver':'cdcl'},
    "cdcl_bin":{'encoding':'bitwise', 'solver':'cdcl'}, 
    "wsat_seq":{'encoding': 'sequential', 'solver': 'wsat'},
    "wsat_he":{'encoding':'heule', 'solver':'wsta'}, 
    "wsat_bin":{'encoding':'bitwise', 'solver':'wsat'}
    }
    
# Run the main function
main(input_folder, output_folder, approaches=approaches, folder = "SAT")