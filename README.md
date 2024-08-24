# COMBINATORIAL DECISION MAKING AND OPTIMIZATION - FINAL PROJECT - A.Y. 2023/2024

# Multiple Couriers Problem Solver

This repository contains implementations of various approaches to solve the Multiple Couriers Problem (MCP). The MCP is a variant of the Vehicle Routing Problem where multiple couriers need to deliver packages to different locations while minimizing the maximum distance traveled by any courier.

You can find a detailed problem description at **CDMO-project-description.pdf**.

## Approaches Implemented

1. **Constraint Programming (CP)**: Uses constraint satisfaction techniques to model and solve the problem.
2. **Boolean Satisfiability (SAT)**: Encodes the problem as a Boolean satisfiability problem and uses a SAT solver to find a solution.
3. **Mixed Integer Programming (MIP)**: Formulates the problem as a mixed integer linear program and solves it using mathematical optimization techniques.
4. **Satisfiability Modulo Theory (SMT)**: Extends SAT solving with additional theories to more naturally express the problem constraints.

## Repository Structure

```
CDMO/
│
├── checker/
│   ├── InputFolder/
│   ├── ResultFolder/
│   └── check_solution.py
|
├── data-converters/
│   ├── fromDATtoDZN.py
│   ├── fromDZNtoPY.py
│   └── move_files.py
|
├── images/
│   ├── 
│   ├── 
│   └── 
|
├── instances/
|
├── models/
│   ├── CP/
|       ├── CP_models/
|           ├── model0.mzn
|           ├── model1.mzn
|           ├── model2.mzn
|           └── model3.mzn
|       ├── instancesDZN/
|       └── generateResultsCP.py
│   ├── MIP/
|       ├── generateResultsMIP.py
|       └── MIP_models.py
│   ├── SAT/
|       ├── generateResultsSAT.py
|       ├── SAT_model.py
|       └── SAT_utils.py
│   ├── SMT/
|       ├── generateResultsSMT.py
|       └── SMT_models.py
|   └── run_all.py
│
├── res/
│   ├── CP/
│   ├── MIP/
│   ├── SAT/
│   └── SMT/
│
├── Dockerfile
├── README.md
├── Description.pdf
└── Report.pdf
```

## Getting Started

### Cloning the Repository

1. Open a terminal or command prompt.

2. Run the following command:

   ```
   git clone https://github.com/alessandrogentili001/CDMO.git
   ```

3. Navigate to the cloned repository:

   ```
   cd CDMO
   ```

### Setting Up the Docker

1. create a docker image:

   ```
   docker build -t dascenzo_gentili_project .
   ```

2. Activate the virtual environment:

   ```
   docker run dascenzo_gentili_project
   ```

### Reproduce the Experiments

1. Run the experiment script (look at the python file to better understand the args):

   ```
   python ./models/run_all.py [args]
   ```

2. After the experiments complete, move the files into the `./checker/ResultFolder` folder for checking solutions:

   ```
   python ./data-converters/move_files.py
   ```

3. finally check experimental results:

   ```
   python ./checker/check_solution.py ./checker/InputFolder ./checker/ResultFolder
   ```

### Exploring the Source Code

Each solver implementation is contained in its respective sub-directory in the `models` directory. Here's a brief overview of each:

- `./models/CP/CP_models`: Implements the Constraint Programming approach using MiniZinc.
- `./models/MIP/MIP_models.py`: Implements the SAT solver approach using the GurobiPy library.
- `./models/SAT/SAT_models.py`: Implements the Mixed Integer Programming approach using the z3 library.
- `./models/SMT/SMT_models.py`: Implements the Satisfiability Modulo Theory approach using the z3 library.

To play with a specific implementation, open the corresponding file in your preferred IDE.