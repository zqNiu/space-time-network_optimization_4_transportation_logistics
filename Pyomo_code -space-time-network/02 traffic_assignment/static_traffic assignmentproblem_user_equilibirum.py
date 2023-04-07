import pyomo.environ as pyo
from pyomo.opt import SolverFactory

#指定求解器
opt = pyo.SolverFactory('ipopt')
model = pyo.ConcreteModel()

model.I = pyo.Set(initialize=[i+1 for i in range(4)])
model.J = pyo.Set(initialize=[i+1 for i in range(4)])
model.A=pyo.Set(initialize=[(1,2),(1,3),(2,4),(3,4),(3,2)])
model.c_a=pyo.Param({(1,2):60,(1,3):10,(2,4):10,(3,4):60,(3,2):10})
model.c_b=pyo.Param({(1,2):1,(1,3):10,(2,4):10,(3,4):1,(3,2):1})
model.demand_vehicle=6
model.origin_node=pyo.Set(initialize=[1])
model.destination_node=pyo.Set(initialize=[4])
model.intermediate_node=pyo.Set(initialize=[2,3])

model.x=pyo.Var(model.I,model.J,domain=pyo.PositiveReals,bounds=(0,None))

@model.Constraint(model.origin_node)
def origin_cos(model,i):
    val=0
    for j in model.J:
        if (i,j) in model.A:
            val+=model.x[i,j]
    return val==model.demand_vehicle

@model.Constraint(model.destination_node)
def desti_cos(model,j):
    val=0
    for i in model.I:
        if (i,j) in model.A:
            val+=model.x[i,j]
    return val==model.demand_vehicle

@model.Constraint(model.intermediate_node)
def inter_cos(model,i):
    left_val=0
    right_val=0
    for j in model.J:
        if (i,j) in model.A:
            left_val+=model.x[i,j]
        if (j,i) in model.A:
            right_val+=model.x[j,i]
    return left_val==right_val

@model.Objective
def obj_rule(model):
    val=0
    for i in model.I:
        for j in model.J:
            if (i,j) in model.A:
                val+=model.x[i,j]*model.c_a[(i,j)]+model.x[i,j]*model.x[i,j]*model.c_b[(i,j)]*0.5
    return val

opt.solve(model)
model.display()