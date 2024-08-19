from itertools import combinations
import json 
from z3 import *
import re 

################ ENCODINGS #################

# naive encoding
def at_least_one_np(bool_vars, name = ""):
    return Or(bool_vars)

def at_most_one_np(bool_vars, name = ""):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one_np(bool_vars, name = ""):
    return at_most_one_np(bool_vars) + [at_least_one_np(bool_vars)]


# sequential encoding
def at_least_one_seq(bool_vars, name = ""):
    return at_least_one_np(bool_vars)

def at_most_one_seq(bool_vars, name = ""):
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n - 1)] #the trick to distinguish variables is using index numbers
    constraints.append(Or(Not(bool_vars[0]), s[0])) #implication 
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2]))) #s has length n-1
    for i in range(1, n - 1):
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1])))
        constraints.append(Or(Not(s[i-1]), s[i]))
    return And(constraints) #CNF

def exactly_one_seq(bool_vars, name = ""):
    return And(at_least_one_seq(bool_vars), at_most_one_seq(bool_vars, name))

def at_most_k_seq(bool_vars, k, name):
    if k >= len(bool_vars):
        return True
    constraints = []
    n = len(bool_vars)
    s = [[Bool(f"s_{name}_{i}_{j}") for j in range(k)] for i in range(n)]
    for i in range(n):
        if i < n-1:
            constraints.append(Or(Not(bool_vars[i]), s[i][0]))
            for j in range(1, k):
                constraints.append(Or(Not(bool_vars[i]), Not(s[i-1][j-1]), s[i][j]))
            constraints.append(Or(Not(s[i][k-1]), Not(bool_vars[i+1])))
    return And(constraints)

def at_least_k_seq(bool_vars, k, name):
    return at_most_k_seq([Not(v) for v in bool_vars], len(bool_vars) - k, name)

def exactly_k_seq(bool_vars, k, name):
    return And(at_most_k_seq(bool_vars, k, name), at_least_k_seq(bool_vars, k, name))


# bitwise encoding
def toBinary(num, length = None):
    num_bin = bin(num).split("b")[-1]
    if length:
        return "0"*(length - len(num_bin)) + num_bin
    return num_bin
    
def at_least_one_bw(bool_vars, name = ""):
    return at_least_one_np(bool_vars)

def at_most_one_bw(bool_vars, name = ""):
    constraints = []
    n = len(bool_vars)
    m = math.ceil(math.log2(n))
    r = [Bool(f"r_{name}_{i}") for i in range(m)]
    binaries = [toBinary(i, m) for i in range(n)]
    for i in range(n):
        for j in range(m):
            phi = Not(r[j])
            if binaries[i][j] == "1":
                phi = r[j]
            constraints.append(Or(Not(bool_vars[i]), phi))        
    return And(constraints)

def exactly_one_bw(bool_vars, name = ""):
    return And(at_least_one_bw(bool_vars), at_most_one_bw(bool_vars, name)) 


# heule encoding
def at_least_one_he(bool_vars, name = ""):
    return at_least_one_np(bool_vars)

def at_most_one_he(bool_vars, name = ""):
    if len(bool_vars) <= 4:
        return And(at_most_one_np(bool_vars))
    y = Bool(f"y_{name}")
    return And(And(at_most_one_np(bool_vars[:3] + [y])), And(at_most_one_he(bool_vars[3:] + [Not(y)], name+"_")))

def exactly_one_he(bool_vars, name = ""):
    return And(at_most_one_he(bool_vars, name), at_least_one_he(bool_vars))

###########################################

# read instance files 
def parse_dzn_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    
    # Extracting m and n
    m = int(re.search(r'm = (\d+);', content).group(1))
    n = int(re.search(r'n = (\d+);', content).group(1))
    num_bits = math.floor(math.log2(n)) # for bitwise encoding only
    
    # Extracting l
    l = list(map(int, re.search(r'l = \[(.+?)\];', content).group(1).split(',')))
    
    # Extracting s
    s = list(map(int, re.search(r's = \[(.+?)\];', content).group(1).split(',')))
    
    # Extracting D
    D_match = re.search(r'D = \[\|(.+?)\|\];', content, re.DOTALL).group(1)
    D_lines = D_match.strip().split('\n')
    D = [list(map(int, re.split(r'\s*,\s*', line.strip().strip('|').strip()))) for line in D_lines]
    
    return m, n, l, s, D, num_bits 

         