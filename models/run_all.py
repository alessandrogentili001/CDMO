import subprocess
import sys

# List of scripts you want to run
scripts = sys.argv[1:]  # Get script names from command-line arguments

for script in scripts:
    print(f"Running {script}...")
    subprocess.run(['python', script])
    print(f"Finished running {script}.\n")
    
''' 

from commmand line perform the following instruction in order to generate results for all the models:

python models/run_all.py models/CP/generateResultsCP.py models/MIP/generateResultsMIP.py  models/SAT/generateResultsSAT.py  models/SMT/generateResultsSMT.py 

'''
