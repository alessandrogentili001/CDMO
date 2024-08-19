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
WORKDIR /dascenzo_gentili_CODM

# copy the content in the working directory 
ADD . .

# run command (checking solution found)
CMD ["python", "./checker/check_solution.py", "./checker/InputFolder", "./checker/ResultFolder"]

############################# ON YOUR MACHINE #############################
# build the docker image
# docker build -t dascenzo_gentili_project .
# run the docker image
# docker run dascenzo_gentili_project