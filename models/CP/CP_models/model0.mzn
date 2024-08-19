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

% Constraints on x ---------------------------------------------

% capacity constraint
constraint
    forall(i in 1..m)(
        sum(j in 1..n)(x[i,j] * s[j]) <= l[i] /\
        sum(j in 1..n)(x[i,j]) > 0                 
    );

% each item is delivered exactly once
constraint
    forall(j in 1..n)(
        sum(i in 1..m)(x[i,j]) = 1 
    );
    
% items must be equally distributed among couriers (SAFE)
constraint 
    forall(k1, k2 in 1..m where k1 < k2)(
        if l[k1] <= l[k2]
            then sum(i in 1..n)(x[k1, i] * s[i]) <= sum(i in 1..n)(x[k2, i] * s[i])
        else
            sum(i in 1..n)(x[k1, i] * s[i]) >= sum(i in 1..n)(x[k2, i] * s[i])
        endif 
    );

% constraints on y -------------------------------------------

% initial and final destination are the same
constraint forall(i in 1..m)(
   y[i,1] = o /\ y[i,n+2] = o
);

% courier i has the item j iff courier i pass from node j
constraint 
    forall(i in 1..m, j in 1..n)(
        x[i,j] = 1 <-> exists(t in 2..n+1)(y[i,t] = j)
    );
    
% fill the tour with the origin 
constraint 
    forall(i in 1..m, t in 2..n+1)(
        y[i,t] = o -> y[i,t+1] = o
    );
    
% never pass for the same point twice excluding the first and the last node 
constraint 
    forall(k in 1..m, i in 1..n)(
        sum(t in 2..n+1)(y[k,t] = i) <= 1
    );
    
% ensure that each node is visited by at most one courier
constraint 
    forall(j in 1..n)(
        sum(i in 1..m)(count(t in 2..n+1)(y[i,t] = j)) <= 1
    );

% symmetry breaking constraints -------------------------------------------

% symmetry breaking for couriers with same load capacity
%constraint
%    forall(i in 1..m-1, i_eq in i+1..m where l[i] == l[i_eq])(
%        lex_greatereq([x[i,j] | j in 1..n], [x[i_eq,j] | j in 1..n])
%    );

% constraints on distance --------------------------------------
    
% compute the distance 
constraint 
    forall(i in 1..m)(
        distance[i] = sum(t in 1..n+1)(D[y[i,t], y[i,t+1]])
    );

% Minimize the distance of the longest travel
var int: max_distance = max(distance);

solve 
    minimize max_distance;

% Output
output [
    "max_distance = ", show(max_distance), ";\n",
    "tour = ", show2d(y), ";\n",
    "assign = ", show2d(x), ";\n"
];
