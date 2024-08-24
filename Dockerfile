# set the base image
FROM python:3.10 

# install the libraires
RUN pip install minizinc 
RUN pip install z3 
RUN pip install gurobipy 
RUN pip install pathlib 
RUN pip install datetime 
RUN pip install numpy  
RUN pip install typing

# set the working directory
WORKDIR /CDMO

# copy the content in the working directory 
ADD . .

# run command
# CMD ["python", "./checker/check_solution.py", "./checker/InputFolder", "./checker/ResultFolder"]   # run checker
CMD ["python", "models/run_all.py", "models/CP/generateResultsCP.py"]                            # run CP model
# CMD ["python", "models/run_all.py", "models/MIP/generateResultsMIP.py"]                          # run MIP model
# CMD ["python", "models/run_all.py", "models/SAT/generateResultsSAT.py"]                          # run SAT model
# CMD ["python", "models/run_all.py", "models/SMT/generateResultsSMT.py"]                          # run SMT model

############################# ON YOUR MACHINE #############################
# build the docker image
# docker build -t dascenzo_gentili_project .
# run the docker image
# docker run dascenzo_gentili_project