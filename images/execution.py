import json
import matplotlib.pyplot as plt
import os

def plot_execution_times(json_folder):
    # Initialize a dictionary to store execution times for each model
    execution_times = {}

    # List all JSON files in the specified folder
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]

    # Sort files to ensure they are in the correct order
    json_files.sort()

    # Iterate through each JSON file
    for file in json_files:
        # Construct the full path to the JSON file
        file_path = os.path.join(json_folder, file)
        
        # Read JSON data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract the instance number from the file name
        instance_num = int(os.path.splitext(file)[0])
        
        # Iterate through each model and collect execution times
        for model in data:
            time = data[model].get('time')
            if time is not None:
                if model not in execution_times:
                    execution_times[model] = []
                execution_times[model].append((instance_num, time))
    
    # Create a plot for execution times
    plt.figure(figsize=(12, 8))  # Increased figure size
    
    # Plot execution times for each model
    for model in execution_times:
        # Sort the execution times by instance number
        execution_times[model].sort(key=lambda x: x[0])
        
        # Extract instances and times
        instances = [x[0] for x in execution_times[model]]
        times = [x[1] for x in execution_times[model]]
        
        plt.plot(instances, times, marker='o', label=model)
    
    plt.title('Execution Times Comparison', fontsize=16)
    plt.xlabel('Instance', fontsize=14)
    plt.ylabel('Time', fontsize=14)
    plt.xticks(ticks=instances, labels=[str(i).zfill(2) for i in instances], fontsize=12)  # Display instance numbers as 01, 02, etc.
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    # Save the plot as an image
    output_dir = 'execution_times_plots'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    image_path = os.path.join(output_dir, 'execution_times_comparison.png')
    plt.savefig(image_path)
    plt.close()

# Folder containing the JSON files
json_folder = './res/MIP/'
plot_execution_times(json_folder)
