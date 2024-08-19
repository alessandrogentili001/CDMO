% Use this editor as a MiniZinc scratch book
include "globals.mzn";

int: m;  % number of couriers
int: n;  % number of items
array[1..m] of int: l;  % maximum load for each courier
array[1..n] of int: s;  % size of each item
array[1..n+1, 1..n+1] of int: D;  % distance matrix

int: o = n+1; % origin  

% decision variables
array[1..m, 1..n] of var 0..1: x; % if x[i,j] = 1 then courier i has the item j
array[1..m, 1..n+2] of var 1..n+1: y; % if y[i,t] = j then courier i is at node j at time t
array[1..m] of var int: distance; % distance travelled by each courier 

% New decision variable for subtour elimination
array[1..m, 1..n+1] of var 0..n: u; % u[i,j] is the position of node j in the tour of courier i

% constraints on x ------------------------------------------------------------------------------
constraint
    forall(i in 1..m)(
        sum(j in 1..n)(x[i,j] * s[j]) <= l[i] /\
        sum(j in 1..n)(x[i,j]) > 0                 
    );

constraint
    forall(j in 1..n)(
        sum(i in 1..m)(x[i,j]) = 1 
    );
    
constraint 
    forall(k1, k2 in 1..m where k1 < k2)(
        if l[k1] <= l[k2]
            then sum(i in 1..n)(x[k1, i] * s[i]) <= sum(i in 1..n)(x[k2, i] * s[i])
        else
            sum(i in 1..n)(x[k1, i] * s[i]) >= sum(i in 1..n)(x[k2, i] * s[i])
        endif 
    );

% constraints on y -----------------------------------------------------------------
constraint forall(i in 1..m)(
   y[i,1] = o /\ y[i,n+2] = o
);

constraint 
    forall(i in 1..m, j in 1..n)(
        x[i,j] = 1 <-> exists(t in 2..n+1)(y[i,t] = j)
    );
    
constraint 
    forall(i in 1..m, t in 2..n+1)(
        y[i,t] = o -> y[i,t+1] = o
    );
    
constraint 
    forall(k in 1..m, i in 1..n)(
        sum(t in 2..n+1)(y[k,t] = i) <= 1
    );
    
constraint 
    forall(j in 1..n)(
        sum(i in 1..m)(count(t in 2..n+1)(y[i,t] = j)) <= 1
    );

% simmetry breacking constraint ------------------------------------------------------------------------
constraint
    forall(i in 1..m-1, i_eq in i+1..m where l[i] == l[i_eq])(
        lex_greatereq([x[i,j] | j in 1..n], [x[i_eq,j] | j in 1..n])
    );

% constraints on distance --------------------------------------------------------------------------
constraint 
    forall(i in 1..m)(
        distance[i] = sum(t in 1..n+1)(D[y[i,t], y[i,t+1]])
    );

% constraints on subtour elimination ---------------------------------------------------------------
constraint
    forall(i in 1..m)(
        u[i,o] = 0 % The depot (origin) is always the first node
    );

constraint
    forall(i in 1..m, j in 1..n)(
        x[i,j] = 1 -> (u[i,j] >= 1 /\ u[i,j] <= n) % value range 
    );

constraint
    forall(i in 1..m, j in 1..n, k in 1..n where j != k)(
        (x[i,j] = 1 /\ x[i,k] = 1) -> u[i,j] != u[i,k] % different items must be delivered at different positions
    );

constraint
    forall(i in 1..m, j in 1..n, k in 1..n where j != k)(
        x[i,j] = 1 /\ x[i,k] = 1 -> 
        (u[i,j] - u[i,k] + n * (y[i, u[i,j]+1] != k) >= 1) % ordering deliveries 
    );

% solve 
var int: max_distance = max(distance);

solve :: seq_search([int_search(y, first_fail, indomain_random),
                    restart_linear(n*n)])
    minimize max_distance;

output [
    "max_distance = ", show(max_distance), ";\n",
    "tour = ", show2d(y), ";\n",
    "assign = ", show2d(x), ";\n",
    %"order = ", show2d(u), ";\n"
];