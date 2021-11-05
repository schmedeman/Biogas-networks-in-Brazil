#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 20:34:13 2021

@author: cristianjunge
"""

## Simulation model

import Transportation_moduleOptA3 as tm
import prod_module as pm
import Biodigester_module as bm
import Financial_v10 as im

import pandas as pd
import numpy as np
import time


def BioGasModel(DesignVector,*parameters):
                
    Supply,SortedDistances, BioParameters, ImpactParameters = parameters
    
    
    ## Transportation module

    Demand0 = pd.DataFrame(DesignVector['Demand0'])
    
    MovementsKg,MovementsKm = tm.SupplyAndDemandBalance(Supply,Demand0,SortedDistances,1)
    
    SSD = 0

    for m in MovementsKg:
    
        SSD = SSD + MovementsKg.loc[m,m]
        
    total_distance_km                   = MovementsKm.sum().sum()
    total_manure_transported_kg_per_day = MovementsKg.sum().sum() - SSD
    
    #print('Transportation ok!')
    
    ## Bio Module

    Biodigsize,BiogasProd,MethProd = bm.biomodulefunction(BioParameters,MovementsKg)
    #print('Bio ok!')
    ## Running Prod module

    bio_out             = BiogasProd
    bio_out['MethProd'] = MethProd

    bio, TotCNGCap, TotElectProd, TotCNGProd = pm.prod(DesignVector, bio_out)
    #print('Prod ok!')
    ## Impact Module

    bio_out2      = (MethProd,Biodigsize)
    
    transport_out = (total_distance_km,total_manure_transported_kg_per_day)
    
    product_out   = (bio,TotCNGCap,TotElectProd,TotCNGProd)

    total_upflow_cap_m3     = 0 #assumption that only lagoon type is being used
    total_pipe_km           = 0 #assumption that no CNG is transported for now
    annual_net_income,Costs_tup, rev_dict = im.net_income(ImpactParameters,
                                            total_pipe_km, 
                                            total_upflow_cap_m3,
                                            transport_out,
                                            bio_out2, 
                                            product_out)
    
    net_co2_offset_kg_per_year = im.net_co2_offset(ImpactParameters,transport_out,bio_out2)
    #print('Impact ok!')
    
    #print('Done!')
    
    return annual_net_income,Costs_tup,rev_dict,MovementsKg,net_co2_offset_kg_per_year




def CreateDemand(Supply,N,fraction_prod,random = False):
    
    ## Create demand, centralized or decentralized on the N biggest manure producers

    Big_prod = Supply['Supply0'].sort_values(axis=0,ascending=False)[0:N]
    
    Big_prod = Big_prod/Big_prod.sum()
    
    total_prod = Supply.sum()[0]*fraction_prod
    
    Demand   = pd.DataFrame(np.zeros(len(Supply.index)),Supply.index,['Demand0'])
    
    for i in Big_prod.index:
        
        Demand.loc[i,'Demand0'] = Big_prod.loc[i]*total_prod
    
    if random == True:
    
        dummy_demand = pd.DataFrame(np.random.rand(len(Supply.index)),Supply.index,['Demand0'])

        dummy_demand = dummy_demand/dummy_demand.sum()*Supply.sum()[0]    
        
        Demand = dummy_demand
    
    return Demand

def run_DOE_Demand(DOE,*parameters):
    
    Supply = parameters[0]
        
    DOE_OUT_DICT = {}
    
    DOE['NetIncome'] = 0
    
    
    for i in DOE.index:
        print(i)
        t0 = time.time()
        N   = DOE.loc[i , 'N']
        fp  = DOE.loc[i , 'F']
        El  = DOE.loc[i , 'Elect']
        
        dummy_demand = CreateDemand(Supply,N,fp)
        
        DesignVector = dummy_demand.copy()
        DesignVector['PerElect'] = np.ones(len(Supply.index))*El 
    
        annual_net_income,Costs_tup,rev_dict,MovementsKg,net_co2_offset_kg_per_year = BioGasModel(DesignVector,*parameters)
        
        outDict = {
            'Demand'    : dummy_demand,
            'NetIncome' : annual_net_income,
            'Costs'     : Costs_tup,
            'Revenue'   : rev_dict,
            'Transport' : MovementsKg,
            'CO2_offset': net_co2_offset_kg_per_year
        }
        
        
        DOE_OUT_DICT[i] = outDict
        
        
        DOE.loc[i , 'NetIncome (MMR)']  = annual_net_income/1000000
        DOE.loc[i , 'CO2_offset (MM)'] = net_co2_offset_kg_per_year[0]/1000000
        
        for c in Costs_tup:
            
            for c_i in c:
                
                DOE.loc[i , 'Cost - '+ c_i] = c[c_i]/1000000
        
        for r in rev_dict:
            
            DOE.loc[i , 'Rev - '+ r] = rev_dict[r]/1000000
        
        
        
        DOE.loc[i , 'Time'     ] = time.time()-t0
    
    
    return DOE,DOE_OUT_DICT
    #DOE.to_excel('DOE_out.xlsx')
        
    
def CreateDesignVector(Supply,N,fraction_prod,fract_elect):
    
    dummy_demand = CreateDemand(Supply,N,fraction_prod)

    DesignVector = dummy_demand.copy()

    DesignVector['PerElect'] = fract_elect*np.ones(len(Supply.index)) #np.random.rand(len(Supply.index))

    return DesignVector
    




