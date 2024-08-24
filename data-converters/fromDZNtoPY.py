import re

def parse_dzn_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    
    # Extracting m and n
    m = int(re.search(r'm = (\d+);', content).group(1))
    n = int(re.search(r'n = (\d+);', content).group(1))
    
    # Extracting l
    l = list(map(int, re.search(r'l = \[(.+?)\];', content).group(1).split(',')))
    
    # Extracting s
    s = list(map(int, re.search(r's = \[(.+?)\];', content).group(1).split(',')))
    
    # Extracting D
    D_match = re.search(r'D = \[\|(.+?)\|\];', content, re.DOTALL).group(1)
    D_lines = D_match.strip().split('\n')
    D = [list(map(int, re.split(r'\s*,\s*', line.strip().strip('|').strip()))) for line in D_lines]
    
    return m, n, l, s, D