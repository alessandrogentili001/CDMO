import json
import matplotlib.pyplot as plt
import os

def create_route_images(json_folder):
    # List all JSON files in the specified folder
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    
    for file in json_files:
        # Construct the full path to the JSON file
        file_path = os.path.join(json_folder, file)
        
        # Read JSON data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Iterate through each key (e.g., Gurobi)
        for key in data:
            solution = data[key].get('sol')
            
            if solution is None:
                print(f"No solution found for {key} in file {file}")
                continue
            
            plt.figure()
            
            # Plot each courier's route starting and ending at (0, 0)
            for i, route in enumerate(solution):
                # Adding the starting and ending point (0)
                route_with_depot = [0] + route + [0]
                x_coords = range(len(route_with_depot))  # Just for visual representation
                y_coords = route_with_depot
                
                plt.plot(x_coords, y_coords, marker='o', label=f'Courier {i+1}')
                for (x, y) in zip(x_coords, y_coords):
                    plt.text(x, y, f'({x},{y})')
            
            plt.title(f'{file} - {key}')
            plt.xlabel('Step')
            plt.ylabel('Point')
            plt.legend()
            
            # Save the plot as an image
            output_dir = 'route_images'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            # Save with a specific naming convention
            image_path = os.path.join(output_dir, f'{os.path.splitext(file)[0]}_{key}.png')
            plt.savefig(image_path)
            plt.close()

# Folder containing the JSON files
for approach in ['CP', 'MIP', 'SMT']: # SAT model is not working 
    json_folder = './res/' + approach
    create_route_images(json_folder)
