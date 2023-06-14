import pyomo.environ as pyo

#select a solver
opt=pyo.SolverFactory('gurobi')
# opt.options['NonConvex'] = 2  for FIFO constraint
model=pyo.ConcreteModel()

A=[i+1 for i in range(20)]
J=[i+1 for i in range(3)] #OD pair
N=[i+1 for i in range(8)] #node index
T=[i+1 for i in range(30)]

initial_af=dict()
for a in A:
    for j in J:
        initial_af[(a,j)]=0

od_desire=dict()
od_val=[125,250,500,375,125,0]
for t in T:
    for j in J:
        id=int(t/5)
        if t%5==0:
            id-=1
        od_desire[(t,j)]=od_val[id]

od_nodes={
    1:(2,6),
    2:(6,2),
    3:(8,3)
}

node_in_arcs={
    2:[1,11],4:[2,5,11,14],1:[3,7],5:[4,9,14],6:[6,17],3:[8,14],7:[10,15,20],8:[13,18]
}
node_out_arcs={
    1:[1,2,3],2:[3,4],3:[5,6],4:[7,8,9,10],5:[11,12,13],6:[14,15,],7:[16,17,18],8:[19,20]

}

#key:arc id  value:len cap vmax
arc_para={
    1:[0.5,260,0.5],2:[0.5,260,0.5],3:[0.5,260,0.5],4:[0.5,260,0.75],
    5:[0.5,260,0.75],6:[0.5,260,0.5],7:[0.5,260,0.5],8:[0.5,260,0.75],
    9:[0.5,260,0.75],10:[0.5,260,0.75],11:[0.5,260,0.75],12:[0.5,260,0.75],
    12:[0.5,260,0.5],13:[0.5,260,0.5],14:[0.5,260,0.5],15:[0.5,260,0.75],
    16:[0.5,260,0.75],17:[0.5,260,0.75],18:[0.5,260,0.5],19:[0.5,260,0.5],
    20:[0.5,260,0.5]
}


pen=99
delta=0.5 #size of time interval
alpha=1
v_min=0.1

model.x_tja=pyo.Var(T,J,A,domain=pyo.PositiveIntegers)  #number of vehicles j on arc a at the end of period t
model.cx_ta=pyo.Var(T,A,domain=pyo.PositiveIntegers)  #total number of vehicles on arc a at t
model.e_tja=pyo.Var(T,J,A,domain=pyo.PositiveIntegers)  #number of vehicles entering arc a at t for od j
model.l_tja=pyo.Var(T,J,A,domain=pyo.PositiveIntegers)  #number of vehicles leaving arc a at t for od j
model.dn_j=pyo.Var(J,domain=pyo.PositiveIntegers) #number of vehicles cannot arrive at d for od j
model.q_tj=pyo.Var(T,J,domain=pyo.PositiveIntegers) #number of vehicles cannot leave at t for od j

def cos1(model,a,j,t):
    if t==1:
        return pyo.Constraint.Skip
    return model.x_tja[(t,j,a)]==model.x_tja[(t-1,j,a)]+model.e_tja[(t,j,a)]-model.l_tja[(t,j,a)]
model.cos1=pyo.Constraint(A,J,T,rule=cos1)

def cos2(model,a,j,t):
    if t==1:
        return pyo.Constraint.Skip
    return model.l_tja[(t,j,a)]<=model.x_tja[(t-1,j,a)]
model.cos2=pyo.Constraint(A,J,T,rule=cos2)

def cos3(model,n,j,t):
    if n==od_nodes[j][0] or n==od_nodes[j][1]:
        return pyo.Constraint.Skip
    left_val=0
    for a in node_out_arcs[j]:
        left_val+=model.l_tja[(t,j,a)]

    right_val=0
    for a in node_in_arcs[j]:
        right_val+=model.e_tja[(t,j,a)]

    return left_val==right_val
model.cos3=pyo.Constraint(N,J,T,rule=cos3)

def cos4(model,n,j,t):
    if n!=od_nodes[j][0] or t==1:
        return pyo.Constraint.Skip
    left_val=0
    for a in node_in_arcs[j]:
        left_val+=model.e_tja[(t,j,a)]

    return left_val==od_desire[(t,j)]-model.q_tj[(t,j)]+model.q_tj[(t-1,j)]
model.cos4=pyo.Constraint(N,J,T,rule=cos4)

def cos5(model,n,j):
    if n!=od_nodes[j][1]:
        return pyo.Constraint.Skip
    left_val=0
    for t in T:
        for a in node_out_arcs[n]:
            left_val+=model.l_tja[(t,j,a)]
    right_val=0
    for t in T:
        right_val+=od_desire[(t,j)]
    right_val-=model.dn_j[j]
    return left_val==right_val
model.cos5=pyo.Constraint(N,J,rule=cos5)

def cos6(model,a,t):
    val=0
    for j in J:
        val+=model.x_tja[(t,j,a)]
    return val==model.cx_ta[(t,a)]
model.cos6=pyo.Constraint(A,T,rule=cos6)

def cos7(model,a,t):
    return model.cx_ta[(t,a)]<=arc_para[a][1]
model.cos7=pyo.Constraint(A,T,rule=cos7)

def cos8(model,a,t):
    if t==1:
        return pyo.Constraint.Skip
    left_val=0
    for j in J:
        left_val+=model.l_tja[(t,j,a)]

    right_val=model.cx_ta[(t-1,a)]/arc_para[a][0]*(
        arc_para[a][2]+(arc_para[a][2]-v_min)*(1-model.cx_ta[(t-1,a)]/arc_para[a][1])
    )*delta
    return left_val<=right_val
model.cos8=pyo.Constraint(A,T,rule=cos8)

#FIFO constraint
# def cos9(model,a,t,j):
#     left_val=0
#     for j_id in J:
#         left_val+=model.l_tja[(t,j_id,a)]
#     left_val=model.x_tja[(t,j,a)]*left_val
#
#     right_val=0
#     for j_id in J:
#         right_val+=model.x_tja[(t,j_id,a)]
#     right_val=model.l_tja[(t,j,a)]*right_val
#     return left_val==right_val
# model.cons9=pyo.Constraint(A,T,J,rule=cos9)



def obj(model):
    part1=0
    for a in A:
        for j in J:
            for t in T:
                part1+=model.x_tja[(t,j,a)]
    part1=part1*delta

    part2=0
    for j in J:
        part2 += model.dn_j[j]
        for t in T:
            part2+=model.q_tj[(t,j)]
    part2=part2*pen
    return part1+part2
model.obj=pyo.Objective(rule=obj,sense=pyo.minimize)

opt.solve(model)
print("obj is {}".format(model.obj()))

print("time dependent arc flow")
for t in T:
    val=[]
    for a in A:
       val.append(model.cx_ta[(t,a)]())
    print("t{}:{}".format(t,val))