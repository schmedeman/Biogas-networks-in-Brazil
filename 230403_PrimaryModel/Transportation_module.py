"""
Sustainable regional biogas networks in
Southern Brazil
Created 2021-2023
@authors: Phillip Schmedeman, Karthik Rajasekaran, Cristian Junge, Chun Hern Tan 
"""

## Loading Libraries

import numpy as np
import pandas as pd



## Module functions


def SupplyAndDemandBalance(Supply0,Demand0,SortedDistances,N):
    
    #SortSupply and create dataframes to update as the algorithm runs.
    
    Demand = Demand0.sort_values(by=['Demand0'], ascending=False)
    
    Demand.columns = ['Demand']
    
    #Supply         = Supply0.copy()
    col_name = Supply0.columns[0]
    Supply = Supply0.sort_values(by=[col_name], ascending=False)
    Supply.columns = ['Supply']
    
    N_muni        = len(Demand0)
    
    # Create Out DataFrames
    Movements_kg = pd.DataFrame(0,Demand0.index,Demand0.index)
    Movements_km = pd.DataFrame(0,Demand0.index,Demand0.index)
    
    
    ## Solve the diagonal term (self Satisfied demand)
    
    for m in Supply.index:
        dem_m = Demand.loc[m,'Demand']
            
        if dem_m > 0: # Is there demand?
            sup_i = Supply.loc[m,'Supply']
                
            if sup_i > 0: ## Is there supply available?
                
                if sup_i > dem_m: ## Is supply higher than demand?
                            
                    Movements_kg.loc[m,m]  = Movements_kg.loc[m,m] + dem_m  ## shipments to, from                             
                    Demand.loc[m,'Demand'] = 0
                    Supply.loc[m,'Supply'] = sup_i - dem_m
                        
                else:
                            
                    Movements_kg.loc[m,m]  = Movements_kg.loc[m,m] + sup_i ## shipments to, from 
                    Demand.loc[m,'Demand'] = dem_m - sup_i
                    Supply.loc[m,'Supply'] = 0
                
                
            
    
    ## Satisfy demand by looking at the N closest municipalities:
    
    # N = 2
    
    lp = 0
    flag = 0
    
    while flag == 0:
        
        for m in Supply.index:
            
            dem_m = Demand.loc[m,'Demand']
            
        
            if dem_m > 0:
                
                # Look at the supply of the N closest municipalities
                
                for i in range(N): 
                    
                    idx = lp*N + i
                    
                    if idx < N_muni:
                        
                        nearest_i = SortedDistances[m].index[idx]
                    else:
                        break
                    sup_i = Supply.loc[nearest_i,'Supply']
                    
                    if sup_i > 0: ## Is there supply available?
                    
                        Movements_km.loc[m,nearest_i] = SortedDistances[m].loc[nearest_i]
                        
                        if sup_i > dem_m: ## Is supply higher than demand?
                            
                            Movements_kg.loc[m,nearest_i]   = Movements_kg.loc[m,nearest_i] + dem_m  ## shipments to, from 
                            
                            Demand.loc[m,'Demand']         = 0
                            Supply.loc[nearest_i,'Supply'] = sup_i - dem_m
                        
                        else:
                            
                            Movements_kg.loc[m,nearest_i]  = Movements_kg.loc[m,nearest_i] + sup_i ## shipments to, from 
                            
                            Demand.loc[m,'Demand']         = dem_m - sup_i
                            Supply.loc[nearest_i,'Supply'] = 0
                    
                    
        lp = lp + 1
        
        # Conditions to exit                    
        if Demand.sum()[0] == 0:
            
            flag = 1
            
        elif Supply.sum()[0] == 0: 
            
            flag = 1
            
    

    return Movements_kg,Movements_km




def ListToStr(list):
    
    new_list = []
    
    for i in list:
        if type(i) == str:
            new_list.append(i)
            
        else:
            new_list.append(str(i))
            
    return new_list


def ListStrToInt(list):
    
    new_list = []
    
    for i in list:
        if type(i) == str:
            new_list.append(int(i))

        else:
            new_list.append(i)
                
            
    return new_list


def SortedDistancesDict(MuniDistances,Selected_munis):
    
    ## Function to create the Sorted Distances Dictionary
    
    cols = MuniDistances.columns
    
    cols = ListStrToInt(list(cols))
    
    MuniDistances.columns = cols
    
    #cols_select = ListToStr(list(Selected_munis))

    MuniDistances_select = MuniDistances.loc[Selected_munis,Selected_munis]
    print(MuniDistances_select.shape)
    SortedDistances = {}

    for i in MuniDistances_select.index:

        SortedDistances[i] = MuniDistances_select.loc[i,:].sort_values(axis=0)

    
    return SortedDistances
    
    
    
    
    
    


