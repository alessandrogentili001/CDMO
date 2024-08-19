import os
import shutil

# Define the source and destination directories
source_dir = 'res'
destination_dir = 'checker/ResultFolder'

# Ensure the destination directory exists
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)
else:
    # Clean the destination directory by removing all its contents
    for item in os.listdir(destination_dir):
        item_path = os.path.join(destination_dir, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Remove directory
        else:
            os.remove(item_path)  # Remove file
    print(f"Cleaned the destination directory: {destination_dir}")


# Loop through all the items in the source directory
for item in os.listdir(source_dir):
    source_path = os.path.join(source_dir, item)
    destination_path = os.path.join(destination_dir, item)

    # Check if it is a directory
    if os.path.isdir(source_path):
        shutil.copytree(source_path, destination_path)
        print(f"Copied directory: {item}")

print("All directories have been copied.")
