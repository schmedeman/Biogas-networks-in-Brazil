#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SA - Multi

MDO - Assignment 4b.

MIT - Spring 2021

@author: cristianjunge
"""

import pandas as pd
import math
import random
import numpy as np



def ConstraintsCalculation (x,manure_limit):
    
    r1 = 1000000
    
    
    Manure_total = x.Demand0.sum()
    
    if  Manure_total > manure_limit:
        
        g1 = r1*(Manure_total-manure_limit)**2
        print('Violation!')
    else:
        
        g1 = 0
    
    G = [g1]
    
    return G

def ObjectiveFunction (x,Model,ModelParameters,Lambd,co2_price,manure_limit):
    
    annual_net_income,Costs_tup,rev_dict,MovementsKg,net_co2_offset_kg_per_year = Model(x,*ModelParameters)
    
    ## Compute constraints
    
    G = ConstraintsCalculation (x,manure_limit)
    
    pen = 0
    
    for g in G:
        
        pen = pen + g
    #            lambda                   
    #obj_val = - (Lambd)*annual_net_income/0.01 - (1-Lambd)*net_co2_offset_kg_per_year/1 + pen
    obj_val = - (Lambd)*(annual_net_income+(net_co2_offset_kg_per_year*co2_price/1000))/0.01 - (1-Lambd)*net_co2_offset_kg_per_year/1 + pen
    #obj_val = - (0.95)*annual_net_income/1 - (0.05)*net_co2_offset_kg_per_year/1 + pen
    
    #return obj_val,annual_net_income,net_co2_offset_kg_per_year
    return obj_val,annual_net_income+(net_co2_offset_kg_per_year*co2_price/1000),net_co2_offset_kg_per_year

def PerturbationFun(x,params,N): ## Perturbs N dimensions and electricity
    
    manure_limit = 8870365.07
    
    perc_change = 0.05

    dem00  = np.array(x.Demand0)
    dem0   = np.array(x.Demand0)
    f_e0   = np.array(x.PerElect)
    
    dims   = [random.randint(0,len(x)-1) for i in range(N)]
    
    for d in dims:
    
        dem0[d] = dem0[d] + (random.random()*2-1)*manure_limit*perc_change
        
        if dem0[d] < 0:

            dem0[d] = 0
        
        
        tot_dem = np.sum(dem0)
        feas_loop = 0
        
        while tot_dem > manure_limit:
            feas_loop = feas_loop + 1
            if feas_loop >10000:
                print('Stuck')
                print(dem0)
            
            dem0[d] = dem00[d] + (random.random()*2-1)*manure_limit*perc_change
        
            if dem0[d] < 0:
                
                dem0[d] = 0
        
            tot_dem = np.sum(dem0)
        
        
    dims   = [random.randint(0,len(x)-1) for i in range(N)]
    
    for d in dims:  
        
        if dem0[d] == 0:
            f_e0[d] = 0
        else:
            f_e0[d] = random.random()
    
    x_new = pd.DataFrame(np.transpose([dem0,f_e0]),x.index,['Demand0','PerElect'])
    
    return x_new

def PerturbationFun_loose(x,params,N,manure_limit): ## Perturbs N dimensions and electricity
    

    
    dem0   = np.array(x.Demand0)
    f_e0   = np.array(x.PerElect)
    
    dims   = [random.randint(0,len(x)-1) for i in range(N)]
    
    for d in dims:
    
        dem0[d] = random.random()*manure_limit
    
        tot_dem = np.sum(dem0)
        
        while tot_dem > manure_limit:
            
            dem0[d] = random.random()*manure_limit
            
            tot_dem = np.sum(dem0)
        
    dims   = [random.randint(0,len(x)-1) for i in range(N)]
    
    for d in dims:  
        
        if dem0[d] == 0:
            f_e0[d] = 0
        else:
            f_e0[d] = random.random()
    
    x_new = pd.DataFrame(np.transpose([dem0,f_e0]),x.index,['Demand0','PerElect'])
    
    return x_new

def PerturbationFun_coupled(x,params,N): ## Perturbs N dimensions and electricity
    
    manure_limit = 8870365.07
    
    dem0   = np.array(x.Demand0)
    f_e0   = np.array(x.PerElect)
    
    dims   = [random.randint(0,len(x)-1) for i in range(N)]
    
    for d in dims:
    
        dem0[d] = random.random()*manure_limit
    
        tot_dem = np.sum(dem0)
        
        while tot_dem > manure_limit:
            
            dem0[d] = random.random()*manure_limit
            
            tot_dem = np.sum(dem0)
        
        
        if dem0[d] == 0:
            f_e0[d] = 0
        else:
            f_e0[d] = random.random()
    
    x_new = pd.DataFrame(np.transpose([dem0,f_e0]),x.index,['Demand0','PerElect'])
    
    return x_new

def PerturbationFunAll(x):
    
    manure_limit = 8870365.07
    
    perc_change = 0.01
    
    dem0   = np.array(x.Demand0)
    
    incr = [random.random()*manure_limit*perc_change for i in range(len(x))]
    
    demand = dem0 + incr
    fract_elect = [random.random() for i in range(len(x))]
    
    for i in range(len(demand)):
        if demand[i]<0:
            demand[i]      = 0
            fract_elect[i] = 0
    
    if np.sum(demand) > manure_limit:
        
        demand = demand*manure_limit/np.sum(demand)
        
    x_new = pd.DataFrame(np.transpose([demand,fract_elect]),x.index,['Demand0','PerElect'])
    
    
    return x_new


def cooling (params):
    
    Type  = params['Type']
    T0    = params['T0']
    
    T_end = params['T_end']
        
    dT    = params['dT']
    
    T_vect = [T0]

    T_i = T_vect[0]
    
    if Type == 1:  ## Exponential Cooling
        
        while T_i > T_end:
    
            T_i = dT*T_vect[-1]
            T_vect.append(T_i)
            
        return T_vect
    
    if Type == 0:  ## Linear Cooling
    
        while T_i > T_end:
    
            T_i = T_vect[-1] - dT
            T_vect.append(T_i)
            
        return T_vect
    
    
    
    
def SA_algorithm(x0,Model,SAparams,ModelParameters,Lambd,co2_price,manure_limit):

    CoolingSchedule = cooling(SAparams)
    
    x = x0
    
    X_hist = [x0]
    X_opt  = [x0]
    
    obj_val0,annual_net_income0,net_co2_offset_kg_per_year = ObjectiveFunction(x,Model,ModelParameters,Lambd,co2_price,manure_limit)
    
    
    E_hist = [obj_val0]
    
    E_opt  = [obj_val0]
    
    E_best = obj_val0
    
    E_bestV  = [obj_val0]
    
    NI_best  = annual_net_income0
    NI_bestV = [annual_net_income0]
    
    CO2_best  = net_co2_offset_kg_per_year
    CO2_bestV = [net_co2_offset_kg_per_year]
    
    
    x_best  = x
    
    Neq   = SAparams['Neq']
    
    N_it_max = len(CoolingSchedule)*Neq
    print('Number of iterations in cooling schedule:', N_it_max,'\n')
    #print('0 %',int(NI_best/1000),'kBRL')
    
    N_it  = 0
    
    i = 0

    for T in CoolingSchedule:
        
        for n in range(Neq):
        
            E,NI,CO2 = ObjectiveFunction(x,Model,ModelParameters,Lambd,co2_price,manure_limit)
            
            ## Perturbed x:
            
            #x_new = PerturbationFun(x,ModelParameters,1)
            x_new  = PerturbationFun_loose(x,ModelParameters,2,manure_limit)
            #x_new = PerturbationFun_coupled(x,ModelParameters,2)
            
            #x_new = PerturbationFunAll(x)
            
            X_hist.append(x_new)
        
            E_new,NI_new,CO2_new = ObjectiveFunction(x_new,Model,ModelParameters,Lambd,co2_price,manure_limit)
            
        
            E_hist.append(E_new)
        
            dE = E_new - E
      
            if E_new <  E:
            
                x = x_new
                X_opt.append(x)
                E_opt.append(E_new)
                
                if E_new < E_best:
                    E_best  = E_new
                    x_best  = x_new
                    NI_best = NI_new
                    CO2_best = CO2_new
                    
            elif math.exp(-dE/T) > random.random():
            
            
                x = x_new
                
            #X_opt.append(x)
            #E_opt.append(E_new)
            
            E_bestV.append(E_best)
            NI_bestV.append(NI_best)
            CO2_bestV.append(CO2_best)
            
            N_it = N_it +1
            
            i = print_progress(N_it/N_it_max*100,i,NI_best,CO2_best,NI_new,CO2_new)
            

    return X_hist,X_opt,E_hist,E_opt,E_bestV,N_it,x_best,NI_bestV,CO2_bestV
    
    
    
def print_progress(perc,i,NI_best,CO2_best,NI_new,CO2_new):
    marks = np.arange(0,105,5)
     
    if perc >= marks[i+1]:
        print(marks[i+1],'%',int(NI_best),'BRL', int(CO2_best),'kgCO2',int(NI_new),'BRL', int(CO2_new),'kgCO2')
         
        i = i + 1
    
    return i
     
    
    
    
    
    
    
    
    
    
    
    
    
    
    