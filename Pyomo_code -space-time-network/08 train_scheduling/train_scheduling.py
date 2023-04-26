import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from pyomo.util.infeasible import log_infeasible_constraints
import copy
import logging

logging.getLogger('pyomo').setLevel(logging.INFO)
#choose a solver
opt = pyo.SolverFactory('ipopt')
model = pyo.ConcreteModel()

# the network is the 6-node network in DTALite
model.U = pyo.Set(initialize=[i+1 for i in range(3)])
model.V = pyo.Set(initialize=[i+1 for i in range(3)])
model.K = pyo.Set(initialize=[i+1 for i in range(2)])
model.k_p= pyo.Set(initialize=[i+1 for i in range(2)])
model.J=pyo.Set(initialize=[i+1 for i in range(4)])
model.j_p=pyo.Set(initialize=[i+1 for i in range(4)])

model.cap=pyo.Param(initialize=10000)
model.sec_min=pyo.Param(initialize=5)
model.sta_min=pyo.Param(initialize=5)
model.buff_min=pyo.Param(initialize=1)
model.buff_max=pyo.Param(initialize=20)
model.dw_min=pyo.Param(initialize=2)
model.dw_max=pyo.Param(initialize=20)
model.ad=pyo.Param(initialize=2)

val_station_dict=dict()
for i in model.U:
    val_station_dict[i]=i
val_station_dict[0]=0
model.val_station=val_station_dict

val_train_dict=dict()
for j in model.J:
    val_train_dict[j]=j
val_train_dict[0]=0
model.val_train=val_train_dict

val_k_dict=dict()
for k in model.K:
    val_k_dict[k]=k
val_k_dict[0]=0
model.val_k=val_k_dict

time_dict=dict()
for k in model.K:
    for k_p in model.k_p:
        if k_p<k:
            time_dict[(k,k_p)]=1
model.time=time_dict

#OD pair station
od_dict=dict()
for o in model.U:
    for d in model.V:
        if o<d:
            od_dict[(o,d)]=1

model.od=od_dict

#define dummy trains
train_dict=dict()
for j in model.J:
    for j_p in model.j_p:
        if j>j_p:
            train_dict[(j,j_p)]=j_p
model.train=train_dict

#free running time in each nearst segement follow the station u
model.r={1:30,2:20,3:20,4:10,
                   5:10,6:20,7:30,8:20}

#passenger arrival rate PAX_minute
model.p={(1,2,1):1,(1,3,1):1,(1,4,1):2,(1,5,1):2,
   (1,6,1):2,(1,7,1):2,(1,8,1):2,(1,9,1):2,(2,3,1):1,
   (2,4,1):2,(2,5,1):2,(2,6,1):1,(2,7,1):2,(2,8,1):1,
   (2,9,1):3,(3,4,1):2,(3,5,1):2,(3,6,1):2,(3,7,1):1,
   (3,8,1):1,(3,9,1):2,(4,5,1):2,(4,6,1):2,(4,7,1):2,
   (4,8,1):2,(4,9,1):2,(5,6,1):2,(5,7,1):2,(5,8,1):2,
   (5,9,1):1,(6,7,1):3,(6,8,1):1,(6,9,1):2,(7,8,1):2,
   (7,9,1):2,(8,9,1):2,(1,2,2):2,(1,3,2):3,(1,4,2):1,
   (1,5,2):2,(1,6,2):1,(1,7,2):1,(1,8,2):1,(1,9,2):1,
   (2,3,2):3,(2,4,2):1,(2,5,2):2,(2,6,2):1,(2,7,2):2,
   (2,8,2):1,(2,9,2):1,(3,4,2):2,(3,5,2):2,(3,6,2):1,
   (3,7,2):1,(3,8,2):2,(3,9,2):1,(4,5,2):1,(4,6,2):3,
   (4,7,2):1,(4,8,2):2,(4,9,2):1,(5,6,2):1,(5,7,2):2,
   (5,8,2):3,(5,9,2):1,(6,7,2):2,(6,8,2):1,(6,9,2):1,
   (7,8,2):3,(7,9,2):2,(8,9,2):3,(1,2,3):3,(1,3,3):4,
   (1,4,3):3,(1,5,3):1,(1,6,3):1,(1,7,3):1,(1,8,3):1,
   (1,9,3):1,(2,3,3):3,(2,4,3):3,(2,5,3):2,(2,6,3):1,
   (2,7,3):1,(2,8,3):1,(2,9,3):2,(3,4,3):3,(3,5,3):2,
   (3,6,3):2,(3,7,3):2,(3,8,3):1,(3,9,3):1,(4,5,3):4,
   (4,6,3):2,(4,7,3):1,(4,8,3):1,(4,9,3):1,(5,6,3):3,
   (5,7,3):3,(5,8,3):1,(5,9,3):1,(6,7,3):2,(6,8,3):1,
   (6,9,3):1,(7,8,3):2,(7,9,3):2,(8,9,3):5,(1,2,4):2,
   (1,3,4):3,(1,4,4):2,(1,5,4):2,(1,6,4):1,(1,7,4):2,
   (1,8,4):1,(1,9,4):1,(2,3,4):2,(2,4,4):2,(2,5,4):1,
   (2,6,4):1,(2,7,4):2,(2,8,4):1,(2,9,4):1,(3,4,4):3,
   (3,5,4):1,(3,6,4):2,(3,7,4):1,(3,8,4):1,(3,9,4):2,
   (4,5,4):3,(4,6,4):1,(4,7,4):2,(4,8,4):1,(4,9,4):1,
   (5,6,4):3,(5,7,4):2,(5,8,4):1,(5,9,4):1,(6,7,4):2,
   (6,8,4):1,(6,9,4):1,(7,8,4):2,(7,9,4):2,(8,9,4):4,
   (1,2,5):2,(1,3,5):1,(1,4,5):2,(1,5,5):1,(1,6,5):1,
   (1,7,5):2,(1,8,5):1,(1,9,5):1,(2,3,5):1,(2,4,5):1,
   (2,5,5):1,(2,6,5):1,(2,7,5):2,(2,8,5):1,(2,9,5):1,
   (3,4,5):3,(3,5,5):1,(3,6,5):2,(3,7,5):1,(3,8,5):1,
   (3,9,5):2,(4,5,5):3,(4,6,5):1,(4,7,5):1,(4,8,5):1,
   (4,9,5):1,(5,6,5):1,(5,7,5):2,(5,8,5):1,(5,9,5):1,
   (6,7,5):1,(6,8,5):1,(6,9,5):1,(7,8,5):1,(7,9,5):1,
                   (8,9,5):1
}

#earliest and latest departure time from first station for train
model.TD_E={1:1,2:25,3:35,4:65,5:85,
                      6:105,7:135,8:155,9:175,
                      10:195}

model.TD_L={1:20,2:30,3:60,4:80,5:100,
                      6:130,7:150,8:170,9:190,
                      10:300}

#train j skip_stop pattern at station u
s_dict=dict()
zero_pair=[(2,2),(2,8),(3,6),(3,7),
           (4,3),(4,5),(5,2),(5,8),
           (6,6),(6,7),(7,3),(7,5),
           (8,2),(8,8),(9,6),(9,7),
           (10,3),(10,5)]
for j in model.J:
    for u in model.U:
        if (j,u) in zero_pair:
            s_dict[(j,u)]=0
        else:
            s_dict[(j,u)]=1
model.s=s_dict

#define variables
#binary variable that indicates if there is a train j_p which has the same couple_stop pattern as train j
model.B=pyo.Var(model.U,model.V,model.J,model.j_p,domain=pyo.Binary)
#binary variable that indicates if a train departure time at station u belongs to a spefific period k
model.x=pyo.Var(model.U,model.J,model.K,domain=pyo.Binary)
#binary variable for nearest dummy train pair j and j_p
model.beta=pyo.Var(model.U,model.V,model.J,model.j_p,domain=pyo.Binary)

#arrival time for train j at station u
model.TA=pyo.Var(model.U,model.J,domain=pyo.PositiveReals)
#departure time for train j at station u
model.TD=pyo.Var(model.U,model.J,domain=pyo.PositiveReals)
#buffer time at segement ahead of station u
model.TR=pyo.Var(model.U,model.J,domain=pyo.PositiveReals)
#Stopping time at station u  ;
model.TS=pyo.Var(model.U,model.J,domain=pyo.PositiveReals)

model.cs=pyo.Var(model.U,model.V,model.J) # couple_stop index which is equal to 1 if train j stops at both station u and v
model.part_1=pyo.Var(model.U,model.V,model.J,model.K)
model.part_2=pyo.Var(model.U,model.V,model.J,model.K)
model.W=pyo.Var(model.U,model.V,model.J)#passenger waiting time with OD demand before train j arrive
model.C=pyo.Var(model.U,model.V,model.J)#nearest dummy train variable for train j in terms of OD pair uv
model.D=pyo.Var(model.U,model.V,model.J,model.j_p) #variable to find train dummy train j_p
model.q=pyo.Var(model.U,model.V,model.J) #train load
model.capa=pyo.Var(model.J) # capacity of train j
model.tmp_bin=pyo.Var(model.U,model.V,model.J,model.J)
# model.tmp_u=pyo.Var(model.U,model.V,model.J)

M=100000
#define constraints
@model.Constraint(model.U,model.J,model.K)
def Con_1_x(model,u,j,k):
    return 60*model.val_k[k-1]-model.TD[u,j]<=M*(1-model.x[u,j,k])

@model.Constraint(model.U,model.J,model.K)
def Con_2_x(model,u,j,k):
    return model.TD[u,j]-60*model.val_k[k]<=M*(1-model.x[u,j,k])

@model.Constraint(model.U,model.J)
def Con_3_x(model,u,j):
    val=0
    for k in model.K:
        val+=model.x[u,j,k]
    return val==1

@model.Constraint(model.U,model.V,model.J)
def Con_cs(model,u,v,j):
    if (u,v) not in model.od:
        return pyo.Constraint.Skip
    return model.cs[u,v,j]==model.od[(u,v)]*model.s[(j,u)]*model.s[(j,v)]

@model.Constraint(model.U,model.V,model.J,model.j_p)
def Con_B(model,u,v,j,j_p):
    if (u,v) not in model.od or (j,j_p) not in model.train:
        return pyo.Constraint.Skip
    else:
        return model.B[u,v,j,j_p]==model.od[(u,v)]*model.train[(j,j_p)]*model.cs[u,v,j]*model.cs[u,v,j_p]/model.val_train[j_p]

# @model.Constraint(model.U,model.V,model.J)
# def Con_c_TMP1(model,u,v,j):
#     val=0
#     for j_p in model.j_p:
#         val+=model.B[u,v,j,j_p]*model.val_train[j_p]*model.tmp_bin[u,v,j,j_p]
#     return model.tmp_u[u,v,j]==val

@model.Constraint(model.U,model.V,model.J)
def Con_c_TMP2(model,u,v,j):
    val=0
    for j_p in model.j_p:
        val+=model.tmp_bin[u,v,j,j_p]
    return val==1

@model.Constraint(model.U,model.V,model.J,model.j_p)
def Con_c_TMP3(model,u,v,j,j_p):
    val = 0
    for j_p in model.j_p:
        val += model.B[u, v, j, j_p] * model.val_train[j_p] * model.tmp_bin[u, v, j, j_p]
    return val>=model.B[u,v,j,j_p]*model.val_train[j_p]

@model.Constraint(model.U,model.V,model.J)
def Con_C(model,u,v,j):
    if (u,v) not in model.od:
        return pyo.Constraint.Skip
    val = 0
    for j_p in model.j_p:
        val += model.B[u, v, j, j_p] * model.val_train[j_p] * model.tmp_bin[u, v, j, j_p]
    if model.od[(u,v)]>0:
        return model.C[u,v,j]== val
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.V,model.J,model.j_p)
def Con_D(model,u,v,j,j_p):
    if (u,v) not in model.od or (j,j_p) not in model.train:
        return pyo.Constraint.Skip
    if model.train[(j,j_p)]>0 and model.od[(u,v)]>0:
        return model.D[u,v,j,j_p]==model.C[u,v,j]-model.val_train[j_p]
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.V,model.J,model.j_p)
def Con_beta(model,u,v,j,j_p):
    if (u,v) not in model.od or (j,j_p) not in model.train:
        return pyo.Constraint.Skip
    if model.train[(j, j_p)] > 0 and model.od[(u, v)] > 0:
        return model.beta[u,v,j,j_p]*model.D[u,v,j,j_p]==0
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.V,model.J,model.j_p)
def Con_beta_1(model,u,v,j,j_p):
    if (u,v) not in model.od or (j,j_p) not in model.train:
        return pyo.Constraint.Skip
    if model.train[(j, j_p)] > 0 and model.od[(u, v)] > 0:
        return model.beta[u,v,j,j_p]+model.D[u,v,j,j_p]**2>=0.00001
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.J)
def Con_link_con_1(model,u,j):
    if model.val_station[u]>1:
        return model.TA[u,j]==model.TD[u-1,j]+model.r[u-1]+model.ad*(model.s[(j,u-1)]+model.s[(j,u)])*model.cs[u,u-1,j]+model.TR[u-1,j]
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.J)
def Con_link_con_2(model,u,j):
    if model.val_station[u] > 1:
        return model.TD[u, j] == model.TA[u, j] + model.TS[u,j]*model.s[(j,u)]
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.J)
def Con_link_con_3(model,u,j):
    if model.val_station[u] > 1:
        return model.TD[u, j] >= model.TD[u-1, j]
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.J)
def Con_sec_TD(model,u,j):
    if model.val_station[u] > 1 and model.val_train[j]>1:
        return model.TD[u, j] - model.TD[u, j-1]>=model.sec_min
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.J)
def Con_sec_TA(model,u,j):
    if model.val_station[u] > 1 and model.val_train[j]>1:
        return model.TA[u, j] - model.TA[u, j-1]>=model.sec_min
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.J)
def Con_sec(model,u,j):
    if model.val_station[u] > 1 and model.val_train[j]>1:
        return model.TA[u, j] - model.TD[u, j-1]>=model.sta_min
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.J)
def Con_stop_TSmin(model,u,j):
    if model.s[(j,u)] > 0:
        return model.TS[u, j] >=model.dw_min
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.J)
def Con_stop_TSmax(model,u,j):
    if model.s[(j,u)] > 0:
        return model.TS[u, j] <=model.dw_max
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U, model.J)
def Con_buff_TRmin(model, u, j):
    return model.TR[u, j] >= model.buff_min

@model.Constraint(model.U, model.J)
def Con_buff_TRmax(model, u, j):
    return model.TR[u, j] <= model.buff_max

@model.Constraint(model.J)
def Con_fea_TD_1(model,j):
    return model.TD[1, j] >= model.TD_E[j]

@model.Constraint(model.J)
def Con_fea_TD_2(model,j):
    return model.TD[1, j] <= model.TD_L[j]

@model.Constraint(model.U,model.V,model.J,model.K)
def Con_def_part_1(model,u,v,j,k):
    if (u,v) not in model.od:
        return pyo.Constraint.Skip
    if model.od[(u,v)]==1:
        return model.part_1[u,v,j,k]==model.x[u,j,k]*model.TD[u,j]-model.x[u,j,k]*60*model.val_k[k-1]
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.V,model.J,model.K)
def Con_def_part_2(model,u,v,j,k):
    if (u,v) not in model.od:
        return pyo.Constraint.Skip
    if model.od[(u,v)]==1:
        val=0
        for j_p in model.j_p:
            val+=model.beta[u,v,j,j_p]*model.x[u,j_p,k]*(60*(model.val_k[k]-model.x[u,j,k])-model.TD[u,j_p])
        return model.part_2[u,v,j,k]==val
    else:
        return pyo.Constraint.Skip

@model.Constraint(model.U,model.V,model.J)
def Con_q(model,u,v,j):
    val=0
    for k in model.K:
        if (u,v,k) not in model.p:
            val+=0
        else:
            val+=model.p[u,v,k]*(model.part_1[u, v, j, k]+model.part_2[u, v, j, k])
    return model.q[u,v,j]==model.cs[u,v,j]*val

@model.Constraint(model.J)
def Con_capa(model,j):
    val=0
    for u in model.U:
        for v in model.V:
            val+=model.q[u,v,j]
    return model.capa[j]==val

@model.Constraint(model.J)
def Con_capa(model,j):
    return model.capa[j]<=model.cap

@model.Constraint(model.U,model.V,model.J)
def Con_w(model,u,v,j):
    val=0
    for k in model.K:
        if (u,v,k) not in model.p:
            val+=0
        else:
            val+=model.p[u,v,k]*(model.part_1[u, v, j, k]+model.part_2[u, v, j, k])** 2
    return model.W[u,v,j]==0.5*model.cs[u,v,j]*val

def obj_rule(model):
    val=0
    for u in model.U:
        for v in model.V:
            for j in model.J:
                val+=model.W[u,v,j]
    return val
model.objective=pyo.Objective(rule=obj_rule)

opt.solve(model)
log_infeasible_constraints(model)
print("obj is {}".format(pyo.value(model.objective)))
model.TA.pprint()
model.TD.pprint()
model.TR.pprint()
model.TS.pprint()
model.C.pprint()
model.D.pprint()
model.beta.pprint()
model.capa.pprint()
model.q.pprint()
model.W.pprint()
model.x.pprint()
model.part_1.pprint()
model.part_2.pprint()
