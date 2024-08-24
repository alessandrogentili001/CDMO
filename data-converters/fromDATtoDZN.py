
def convert_dat_to_dzn(dat_file_path, dzn_file_path):
    """Convert a .dat file to a .dzn file."""
    with open(dat_file_path, 'r') as dat_file:
        lines = dat_file.readlines()

    # Read values from the .dat file
    m = int(lines[0])  # number of couriers
    n = int(lines[1])  # number of items
    l = [int(x) for x in lines[2].split()]  # maximum load of each courier
    s = [int(x) for x in lines[3].split()]  # size of each item

    # Read the distance matrix
    D = []
    for i in range(4, 4 + n + 1):
        D.append([int(x) for x in lines[i].strip().split()])

    # Write to the .dzn file
    with open(dzn_file_path, 'w') as dzn_file:
        dzn_file.write(f"m = {m};\n")
        dzn_file.write(f"n = {n};\n")
        dzn_file.write(f"l = {l};\n")
        dzn_file.write(f"s = {s};\n")
        dzn_file.write("D = [|\n")
        i = 1
        for row in D:
            if i == n+1: dzn_file.write(" " +  ", ".join(map(str, row)) + " |];\n")
            else: dzn_file.write(" " +  ", ".join(map(str, row)) + " |\n")
            i += 1 

dat_file_names = [f'inst0{i}.dat' for i in range(1, 10)]
dat_file_names = dat_file_names + [f'inst{i}.dat' for i in range(10, 22)]
    
dzn_file_names = [f'inst0{i}.dzn' for i in range(1, 10)]
dzn_file_names = dzn_file_names + [f'inst{i}.dzn' for i in range(10, 22)]

dat_paths = []
dzn_paths = []

for dat_file_name in dat_file_names:
    dat_paths.append(f'Instances/{dat_file_name}')
    
for dzn_file_name in dzn_file_names:
    dzn_paths.append(f'models/CP/InstancesDZN/{dzn_file_name}')
    
for i in range(len(dat_paths)):
    dat, dzn = dat_paths[i], dzn_paths[i]
    convert_dat_to_dzn(dat, dzn)
    
    
    



