# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 23:46:16 2021

@author: chunh
"""

import numpy as np
import pandas as pd

""" read in input data """

#financial parameters
#parameters = pd.read_csv('Financial Module Data.csv')

# dummy testing
###############

# total_distance_km=1
# total_manure_transported_kg_per_day=1
# TotElectCap=1
# TotCNGCap=1
# TotElectProd=1
# TotCNGProd=1

#Outputs from other modules 

# bio_out = (MethProd,biodigsize)
# transport_out=(total_distance_km,total_manure_transported_kg_per_day)
# product_out=(Bio,TotCNGCap,TotElectProd,TotCNGProd)

# total_upflow_cap_m3=0 #assumption that only lagoon type is being used
# total_pipe_km = 0 #assumption that no CNG is transported for now

"""defining functions"""
def net_income(parameters,total_pipe_km, total_upflow_cap_m3, transport_out,bio_out, product_out):


#read in parameters    
    pipe_cost_per_km                 = parameters.Values[0]
    truck_cost_per_km_per_m3         = parameters.Values[1]
    biodigester_inv_ref_capacity_m3  = parameters.Values[2]
    biodigester_inv_ref_cost         = parameters.Values[3]
    biodigester_om_cost_percent      = parameters.Values[4]
    electric_gen_per_mw_gas          = parameters.Values[5]
    electric_gen_per_mw_aero         = parameters.Values[6]
    electric_gen_per_mw_ocgt         = parameters.Values[7]
    electric_gen_per_mw_ccgt         = parameters.Values[8]
    electric_om_cost_percent         = parameters.Values[9]
    cng_cost_per_m3                  = parameters.Values[10]
    cng_om_cost_per_m3               = parameters.Values[11]
    rev_per_mwh                      = parameters.Values[12]
    rev_per_cng_m3                   = parameters.Values[13]
    capital_rec_factor               = parameters.Values[14]
    average_manure_density_kg_per_m3 = parameters.Values[15]
    Econ_scale_biodigester           = parameters.Values[22]
    
#read in biodigester variables

    #total_lagoon_cap_m3 = bio_out[1].sum(axis=0)[0]
    individual_biodigester_cap_m3 = bio_out[1].to_numpy()
    
    
#read in transport variables
    total_distance_km=transport_out[0]
    
    total_manure_transported_kg_per_day=transport_out[1]
    
#read in product variables
    prod_out                    = product_out[0] #product_out[0] is the full output dataframe from product module
    total_refinery_capacity_m3  = product_out[1]
    total_elect_mwh_per_day     = product_out[2]
    total_cng_m3_per_day        = product_out[3]

#compute individual cost components

#pipeline costs
    pipeline_inv_cost = pipe_cost_per_km*total_pipe_km

#vehicle costs    
    total_manure_volume_m3_per_day=total_manure_transported_kg_per_day/average_manure_density_kg_per_m3    
    #print(truck_cost_per_km_per_m3)
    truck_cost_per_day = truck_cost_per_km_per_m3*total_distance_km*total_manure_volume_m3_per_day
    
    #print('Truck cost:',truck_cost_per_day)
    
    
#biodigester costs    

    #print(total_lagoon_cap_m3)
    individual_biodigester_cost=individual_biodigester_cap_m3*(biodigester_inv_ref_cost/biodigester_inv_ref_capacity_m3)**Econ_scale_biodigester
    total_biodigester_inv_cost=np.sum(individual_biodigester_cost)
    
    biodigester_om_cost_per_year=biodigester_om_cost_percent/100*total_biodigester_inv_cost

    
#electricity costs
    prod_out['Cost_Function']=1 #np.asarray(1)

    for i in prod_out.index:
        if prod_out.loc[i,'ElectFac']==1:
            prod_out.loc[i,'Cost_Function']=electric_gen_per_mw_gas*prod_out.loc[i,'ElectProd']
        elif prod_out.loc[i,'ElectFac']==2:
            prod_out.loc[i,'Cost_Function']=electric_gen_per_mw_aero*prod_out.loc[i,'ElectProd']
        elif prod_out.loc[i,'ElectFac']==3:
            prod_out.loc[i,'Cost_Function']=electric_gen_per_mw_ocgt*prod_out.loc[i,'ElectProd']
        elif prod_out.loc[i,'ElectFac']==4:
            prod_out.loc[i,'Cost_Function']=electric_gen_per_mw_ccgt*prod_out.loc[i,'ElectProd']            
    
    electric_gen_inv_cost     = prod_out.loc[:,'Cost_Function'].sum(axis=0)
    electric_om_cost_per_year = electric_om_cost_percent*electric_gen_inv_cost/100

#CNG costs     
    cng_inv_cost        = cng_cost_per_m3*total_refinery_capacity_m3     
    cng_om_cost_per_day = cng_om_cost_per_m3*total_cng_m3_per_day

#compute revenue components    
    electric_revenue_per_year = rev_per_mwh*total_elect_mwh_per_day*365     
    cng_revenue_per_year      = rev_per_cng_m3*total_cng_m3_per_day*365


#summing up the annualized costs and revenue
   

    annualize_inv_cost = (pipeline_inv_cost+total_biodigester_inv_cost+electric_gen_inv_cost+cng_inv_cost)*capital_rec_factor/100
    
    #print('Inv_cost:',annualize_inv_cost)
    
    annual_op_cost = cng_om_cost_per_day*365 + electric_om_cost_per_year + truck_cost_per_day*365+biodigester_om_cost_per_year
    
    #print('CNG op cost:',cng_om_cost_per_day)
    #print('Op Cost:',annual_op_cost)
    
    annual_revenue = electric_revenue_per_year+cng_revenue_per_year
    
    rev_dict = {
        'Electricity': electric_revenue_per_year,
        'CNG'        : cng_revenue_per_year
    }
    

    
    annualize_inv_cost_dict = {
        
        'Biodigester_Inv' : total_biodigester_inv_cost,
        'PowerPlant_Inv'  : electric_gen_inv_cost,
        'CNG Refinery_Inv': cng_inv_cost
     #  'Pipeline'        : pipeline_inv_cost,
      # 'Upflow'          : upflow_inv_cost,
    }
        
    annual_op_cost_dict = {
        'CNG Op. Cost'    : cng_om_cost_per_day*365,
        'Elect. Op. Cost' : electric_om_cost_per_year,
        'Truck Op. cost'  : truck_cost_per_day*365
    }
    
    Costs_tup = (annualize_inv_cost_dict,annual_op_cost_dict)
    
  
#finding annual net income    
    annual_net_income = annual_revenue-annualize_inv_cost-annual_op_cost
       
    return annual_net_income,Costs_tup,rev_dict


def net_co2_offset(parameters,transport_out,bio_out):

#read in parameters     
    average_manure_density                     =parameters.Values[15]
#    biogas_meth_content                       = parameters.Values[16]
    meth_m3tokg_coversion                      =parameters.Values[17]
    methtoco2_conversion                       =parameters.Values[18]
    truck_to_car_consumption_ratio             =parameters.Values[19]
    biomethane_fuel_co2_emission_kg_per_km     =parameters.Values[20]
    truck_vol_m3                               =parameters.Values[21]
    
#read in biodigester variables
    total_methane_m3_per_day=bio_out[0].sum(axis=0)
    
#read in transport variables
    total_distance_km=transport_out[0]
    total_manure_transported_kg_per_day=transport_out[1]
    
#compute co2 emissions/reduction components       
    biogas_co2_reduction_kg_per_year=total_methane_m3_per_day*meth_m3tokg_coversion*methtoco2_conversion*365
    
    total_manure_volume_m3_per_day=total_manure_transported_kg_per_day/average_manure_density    
    #transport_co2_emission_kg_per_year= 365*total_distance_km*total_manure_volume_m3_per_day*vehicle_fuel_economy_l_per_km*fuel_co2_emission_kg_per_l/truck_vol_m3
    transport_co2_emission_kg_per_year= 365*total_distance_km*total_manure_volume_m3_per_day*biomethane_fuel_co2_emission_kg_per_km*truck_to_car_consumption_ratio/truck_vol_m3 
#finding annual co2_offset 
    net_co2_offset_kg_per_year=biogas_co2_reduction_kg_per_year-transport_co2_emission_kg_per_year
    
    return net_co2_offset_kg_per_year[0]


    
    
    