import json
import matplotlib.pyplot as plt
import os

def create_route_images(json_file):
    # Read JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Iterate through each model (no_sym, sym, sym_subtour_elim, sym_subtour_elim_heur)
    for model in data:
        solution = data[model].get('sol')
        
        if solution is None:
            print(f"No solution found for {model} in file {json_file}")
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
        
        plt.title(f'{json_file} - {model}')
        plt.xlabel('Step')
        plt.ylabel('Point')
        plt.legend()
        
        # Save the plot as an image
        output_dir = 'route_images'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Save with a specific naming convention
        image_path = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(json_file))[0]}_{model}.png')
        plt.savefig(image_path)
        plt.close()

# File JSON contenente i dati
json_file = 'res/SMT/10.json' # Modifica con il percorso corretto
create_route_images(json_file)
