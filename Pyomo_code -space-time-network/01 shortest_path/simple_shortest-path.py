from pyomo.environ import *

model=ConcreteModel()
model.N = Set(initialize=[i+1 for i in range(6)])
model.A=Set(initialize=[(1,3),(1,2),(2,3)])
model.N_in_A=Set(initialize=[1,2,3])
model.o=Set(initialize=[1])
model.d=Set(initialize=[3])
model.m=Set(initialize=[2,4,5,6])
model.c=Param(model.A,initialize={(1,3):4,(1,2):1,(2,3):2})


model.x=Var(model.A,domain=Binary,bounds=(0,None),)

def origin_rule(model,i):
    val=0
    for arc in model.A:
        if arc[0]==i:
            val+=model.x[arc]
    return val==1
model.origin=Constraint(model.o,rule=origin_rule)

def destination_rule(model,i):
    val=0
    for arc in model.A:
        if arc[1]==i:
            val+=model.x[arc]
    return val==1
model.destination=Constraint(model.d,rule=destination_rule)

def intermediate_rule(model,i):
    left_val=0
    right_val=0
    for arc in model.A:
        if arc[0]==i:
            right_val+=model.x[arc]
        elif arc[1]==i:
            left_val+=model.x[arc]
    if i not in model.N_in_A:
        return model.x[arc]>=0
    return left_val==right_val

model.intermediate=Constraint(model.m,rule=intermediate_rule)


def objective_rule(model):
    return sum( model.x[arc]*model.c[arc] for arc in model.A)
model.objective=Objective(rule=objective_rule)

opt=SolverFactory('cbc')
opt.solve(model)
print("obj is {}".format(value(model.objective)))
model.x.display()