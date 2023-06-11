import pyomo.environ as pyo

#select a solver
opt = pyo.SolverFactory('cbc')
model = pyo.ConcreteModel()

I=[i+1 for i in range(8)]
T=[i for i in range(10)]
A=[i+1 for i in range(9)]

O=[(1,1,0),(2,1,0),(3,1,0),
   (4,1,0),(5,1,0),(6,1,1),
   (7,1,1),(8,1,1),(9,1,1) ]

D=[(1,4,9),(2,4,9),(3,4,9),
   (4,4,9),(5,4,9),(6,4,9),
   (7,4,9),(8,4,9),(9,4,9)]

space_time_arcs_ijts=[
(1,2,0,1),
(1,2,1,2),
(1,2,2,3),
(2,5,1,2),
(2,5,2,3),
(2,5,3,4),
(5,8,2,3),
(5,8,3,4),
(5,8,4,5),
(8,3,3,4),
(8,3,4,5),
(8,3,5,6),
(1,7,0,4),
(1,7,1,5),
(1,7,2,6),
(7,3,4,5),
(7,3,5,6),
(7,3,6,7),
(3,4,4,5),
(3,4,5,6),
(3,4,6,7),
(3,4,7,8),
(2,6,1,2),
(2,6,2,3),
(2,6,3,4),
(6,4,2,7),
(6,4,3,8),
(6,4,4,9),
(5,5,2,3),
(5,5,3,4),
(6,6,2,3),
(6,6,3,4),
(8,8,3,4),
(8,8,4,5),
(7,7,4,5),
(7,7,5,6),
(4,4,5,6),
(4,4,6,7),
(4,4,7,8),
(4,4,8,9)
]

M=[]
for a in A:
   for arc in space_time_arcs_ijts:
      node1=(a,arc[0],arc[2])
      node2=(a,arc[1],arc[3])
      if node1 not in O and node1 not in D:
         M.append(node1)
      if node2 not in O and node2 not in D:
         M.append(node2)

c_ijts={
(1,2,0,1):1,
(1,2,1,2):1,
(1,2,2,3):1,
(2,5,1,2):1,
(2,5,2,3):1,
(2,5,3,4):1,
(5,8,2,3):1,
(5,8,3,4):1,
(5,8,4,5):1,
(8,3,3,4):1,
(8,3,4,5):1,
(8,3,5,6):1,
(1,7,0,4):4,
(1,7,1,5):4,
(1,7,2,6):4,
(7,3,4,5):1,
(7,3,5,6):1,
(7,3,6,7):1,
(3,4,4,5):1,
(3,4,5,6):1,
(3,4,6,7):1,
(3,4,7,8):1,
(2,6,1,2):1,
(2,6,2,3):1,
(2,6,3,4):1,
(6,4,2,7):5,
(6,4,3,8):5,
(6,4,4,9):5,
(5,5,2,3):1,
(5,5,3,4):1,
(6,6,2,3):1,
(6,6,3,4):1,
(8,8,3,4):1,
(8,8,4,5):1,
(7,7,4,5):1,
(7,7,5,6):1,
(4,4,5,6):0,
(4,4,6,7):0,
(4,4,7,8):0,
(4,4,8,9):0

}

cap_ijts={
(1,2,0,1):3,
(1,2,1,2):3,
(1,2,2,3):3,
(2,5,1,2):3,
(2,5,2,3):3,
(2,5,3,4):3,
(5,8,2,3):2,
(5,8,3,4):2,
(5,8,4,5):2,
(8,3,3,4):1,
(8,3,4,5):1,
(8,3,5,6):1,
(1,7,0,4):2,
(1,7,1,5):2,
(1,7,2,6):2,
(7,3,4,5):1,
(7,3,5,6):1,
(7,3,6,7):1,
(3,4,4,5):2,
(3,4,5,6):2,
(3,4,6,7):2,
(3,4,7,8):2,
(2,6,1,2):3,
(2,6,2,3):3,
(2,6,3,4):3,
(6,4,2,7):1,
(6,4,3,8):1,
(6,4,4,9):1,
(5,5,2,3):100,
(5,5,3,4):100,
(6,6,2,3):100,
(6,6,3,4):100,
(8,8,3,4):100,
(8,8,4,5):100,
(7,7,4,5):100,
(7,7,5,6):100,
(4,4,5,6):100,
(4,4,6,7):100,
(4,4,7,8):100,
(4,4,8,9):100
}

model.x=pyo.Var(A,I,I,T,T,domain=pyo.Binary)
model.f=pyo.Var(I,I,T,T,domain=pyo.Reals)

def cons_o(model,a,i,t):
   if (a,i,t) not in O:
      return pyo.Constraint.Skip
   val = 0
   for j in I:
      for s in T:
         if (i,j,t,s) in space_time_arcs_ijts:
            val+=model.x[(a,i,j,t,s)]
   return val==1
model.cons_o=pyo.Constraint(A,I,T,rule=cons_o)

def cons_d(model,a,i,t):
   if (a,i,t) not in D:
      return pyo.Constraint.Skip
   val = 0
   for j in I:
      for s in T:
         if (j,i,s,t) in space_time_arcs_ijts:
            val+=model.x[(a,j,i,s,t)]
   return val==1
model.cons_d=pyo.Constraint(A,I,T,rule=cons_d)

def cons_m(model,a,i,t):
   if (a,i,t) not in M:
      return pyo.Constraint.Skip

   left_val = 0
   right_val=0
   for j in I:
      for s in T:
         if (i,j,t,s) in space_time_arcs_ijts:
            left_val+=model.x[(a,i,j,t,s)]
         if (j,i,s,t) in space_time_arcs_ijts:
            right_val+=model.x[(a,j,i,s,t)]
   return left_val==right_val
model.cons_m=pyo.Constraint(A,I,T,rule=cons_m)

def arc_flow(model,i,j,t,s):
   if (i, j, t, s) not in space_time_arcs_ijts:
      return pyo.Constraint.Skip
   val=0
   for a in A:
      val+=model.x[(a,i,j,t,s)]
   return model.f[(i,j,t,s)]==val
model.arc_flow=pyo.Constraint(I,I,T,T,rule=arc_flow)

def arc_cap(model,i,j,t,s):
   if (i, j, t, s) not in space_time_arcs_ijts:
      return pyo.Constraint.Skip
   return model.f[(i,j,t,s)]<=cap_ijts[(i,j,t,s)]
model.arc_cap=pyo.Constraint(I,I,T,T,rule=arc_cap)

def obj_rule(model):
   val=0
   for arc in space_time_arcs_ijts:
      val+=model.f[arc]*c_ijts[arc]
   return val
model.obj=pyo.Objective(rule=obj_rule,sense=pyo.minimize)

opt.solve(model)

print("obj is {}".format(model.obj()))

for arc in space_time_arcs_ijts:
   if model.f[arc]() and model.f[arc]()>0:
      print("arc_{},flow:{}".format(arc,model.f[arc]()))

