#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sustainable regional biogas networks inSouthern Brazil
Created 2021-2023
@authors: Phillip Schmedeman, Karthik Rajasekaran, Cristian Junge, Chun Hern Tan 
"""


from datetime import datetime
import pandas as pd
import os
import pickle
import multiprocessing as mp

#
root_dir = os.getcwd()

root_dir = root_dir

print('START')

# %% Import Modules

import Transportation_module as tm
import SystemModel         as sm
import SimAnnealing as SAM

# %% Load Run file and muni scope

muni_scope = pd.read_excel('1_RunsSetup/MuniScope.xlsx')

runs = pd.read_excel('1_RunsSetup/ModelRuns.xlsx', index_col=(0))

print('Total number of runs:',len(runs.index))

Selected_munis = list(muni_scope.loc[:,'MuniID'])
print(Selected_munis)

print('Total number of municipalities:',len(Selected_munis))

# %% Load Parameters

ImpactParameters0 = pd.read_csv('0_InputData/Impacts module data.csv')

MuniDistances    =  pd.read_csv('0_InputData/Muni_centroids_distances_km_code_muni.csv',index_col=0)


BioParameters    = pd.read_csv('0_InputData/Biodigester module data.csv',index_col=0)

Supply           = pd.DataFrame(BioParameters.loc[:,'Manure generated (kg/day)'])

Supply.columns   = ['Supply0']

# %% Downscale data to selected municipalities

BioParameters  = BioParameters.loc[Selected_munis,:]

Supply         = Supply.loc[Selected_munis,:]

SortedDistances = tm.SortedDistancesDict(MuniDistances,Selected_munis)


manure_limit     = Supply.loc[:,'Supply0'].sum()


print('Total manure:',round(manure_limit))


# %% Creating the simmulated Annealing model

ModelParameters = (Supply,SortedDistances, BioParameters, ImpactParameters0)

Model = sm.BioGasModel

now = datetime.now()

def run_SA_instance(*inputs):
    
    co2_price,Lambd_i,Model,ModelParameters,manure_limit = inputs

    
    # co2_price = runs.loc[i,'CO2_price (R$/tonne)']
    # Lambd_i   = runs.loc[i,'Lambda']

    print('--------------- \n Starting run!')
    
    SAparams = {
        'T0'       : 100000, # Initial Temperature (default 100,000)
        'T_end'    : 0.5,
        'dT'       : 0.999, # Default 0.999 (0.99 for shorter runtime)
        'Type'     : 1, # 0 for linear, 1 for exponential
        'Neq'      : 1,  # Number of passes
        }

    
    x_best = sm.CreateDesignVector(Supply,11,1,0)
    
    N_pass = 2#runs.loc[i,'N_pass']
    
    for k in range(N_pass):
        
        print('\n Run:',i+1,'/',len(runs.index),' Pass:',k+1,'/',N_pass,'Lambda = ',Lambd_i)
        
        x0 = x_best
        
        X_hist,X_opt,E_hist,E_opt,E_bestV,N_it,x_best,NI_bestV,CO2_bestV, MethProd, BiogasProd,  annualize_inv_cost, annual_net_income, annual_revenue = SAM.SA_algorithm(x0,Model,SAparams,ModelParameters,Lambd_i,co2_price,manure_limit)
    
    Save_dict = {
            
        'Lambda'   : Lambd_i,
        'x_best'   : x_best,
        'NI_bestV' : NI_bestV,
        'CO2_bestV': CO2_bestV,
        'MethProd': MethProd, 
        'BiogasProd': BiogasProd,
        'annualize_inv_cost': annualize_inv_cost, 
        'annual_net_income': annual_net_income, 
        'annual_revenue': annual_revenue,
        'ModelParameters'   : ModelParameters,
        }
        
    pickle.dump(Save_dict, open("2_Output/Out_{}_L{}_PES{}.pkl".format(str(i+1),Lambd_i, co2_price), "wb"))  # save it into a file named save.p
    print('Run',i+1,'saved!')
    
    return Save_dict


# %% Create series of inputs

inputs = []

for i in runs.index:
    
    inputs.append((runs.loc[i,'CO2_PES (USD/tonne)'],runs.loc[i,'Lambda'],Model,ModelParameters,manure_limit))

# %% Running model

for i in range(len(inputs)):
    
    run_SA_instance(*inputs[i])
    
#pickle.dump(results, open("2_Output/Results.pkl", "wb"))  # save it into a file named save.p

print('Total Time:',(datetime.now()-now).seconds/60,'minutes')

print('END :)')
