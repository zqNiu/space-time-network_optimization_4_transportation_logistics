from pyomo.environ import *

model=ConcreteModel()
model.i = Set(initialize=[1])
model.j = Set(initialize=[1,2])

aI={1:10}
model.a=Param(model.i,initialize=aI)

bJ={1:7,2:3}
model.b=Param(model.j,initialize=bJ)

cIJ={(1,1):2,(1,2):3}
model.c=Param(model.i,model.j,initialize=cIJ)

model.x=Var(model.i,model.j,bounds=(0,None))

def supply_rule(model,i):
    return sum([model.x[i,j] for j in model.j])==model.a[i]
model.supply=Constraint(model.i,rule=supply_rule)

def demand_rule(model,j):
    return sum([model.x[i,j] for i in model.i])==model.b[j]
model.demand=Constraint(model.j,rule=demand_rule)

def objective_rule(model):
    return sum([sum([model.x[i,j]*model.c[i,j] for i in model.i]) for j in model.j])
model.objective=Objective(rule=objective_rule)

opt=SolverFactory("gurobi")
opt.solve(model)
print("the obj is{}".format(value(model.objective)))
model.x.display()
