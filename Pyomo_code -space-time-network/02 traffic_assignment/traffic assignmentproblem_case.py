import pyomo.environ as pyo
from pyomo.opt import SolverFactory

#choose a solver
opt = pyo.SolverFactory('ipopt')
model = pyo.ConcreteModel()

model.x1=pyo.Var(domain=pyo.PositiveReals,bounds=(0,None))
model.x2=pyo.Var(domain=pyo.PositiveReals,bounds=(0,None))
model.x3=pyo.Var(domain=pyo.PositiveReals,bounds=(0,None))

model.t1=pyo.Var(domain=pyo.PositiveReals,bounds=(0,None))
model.t2=pyo.Var(domain=pyo.PositiveReals,bounds=(0,None))
model.t3=pyo.Var(domain=pyo.PositiveReals,bounds=(0,None))

model.cos1=pyo.Constraint(expr=model.t1==10*(1+0.15*pow((model.x1/2),4)))
model.cos2=pyo.Constraint(expr=model.t2==20*(1+0.15*pow((model.x2/2),4)))
model.cos3=pyo.Constraint(expr=model.t3==25*(1+0.15*pow((model.x3/2),4)))
model.cos4=pyo.Constraint(expr=model.x1+model.x2+model.x3==10)

#SO
def objective_rule(model):
    return model.x1*model.t1+model.x2*model.t2+model.x3*model.t3
# #UE
# def objective_rule(model):
#     return model.t1+model.t2+model.t3


model.obj=pyo.Objective(rule=objective_rule,sense=pyo.minimize)

opt.solve(model)
model.display()
