# -*- coding: utf-8 -*-
"""
Sustainable regional biogas networks inSouthern Brazil
Created 2021-2023
@authors: Phillip Schmedeman, Karthik Rajasekaran, Cristian Junge, Chun Hern Tan 
"""

import numpy as np
import pandas as pd


"""defining functions"""
def net_income(parameters,total_pipe_km, total_upflow_cap_m3, transport_out, bio_out, product_out):


#read in parameters    
    truck_cost_per_km_per_m3         = parameters.Values[1]
    biodigester_inv_ref_capacity_m3  = parameters.Values[2]
    biodigester_inv_ref_cost         = parameters.Values[3]
    biodigester_om_cost_percent      = parameters.Values[4]
    electric_gen_per_mw_gas          = parameters.Values[5]
    electric_gen_per_mw_aero         = parameters.Values[6]
    electric_gen_per_mw_ocgt         = parameters.Values[7]
    electric_gen_per_mw_ccgt         = parameters.Values[8]
    electric_om_cost_percent         = parameters.Values[9]
    biomethane_cost_per_m3           = parameters.Values[10]
    biomethane_om_cost_per_m3        = parameters.Values[11]
    rev_per_mwh                      = parameters.Values[12]
    rev_per_biomethane_m3            = parameters.Values[13]
    capital_rec_factor               = parameters.Values[14]
    average_manure_density_kg_per_m3 = parameters.Values[15]
    Econ_scale_biodigester           = parameters.Values[22]
    manure_collection_emissions      = parameters.Values[23]
    manure_storage_emissions         = parameters.Values[24]
    
#read in biodigester variables

    #total_lagoon_cap_m3 = bio_out[1].sum(axis=0)[0]
    individual_biodigester_cap_m3 = bio_out[1].to_numpy()
    
    
#read in transport variables

    total_distance_kg_km = transport_out[0]
    
    total_manure_transported_kg_per_day = transport_out[1]
    
    total_manure_processed_kg_per_day = transport_out[2]
    
#read in product variables
    prod_out                    = product_out[0] #product_out[0] is the full output dataframe from product module
    total_refinery_capacity_m3  = product_out[1]
    total_elect_mwh_per_day     = product_out[2]
    total_biomethane_m3_per_day = product_out[3]

#compute individual cost components
    
    # truck cost based on movement_kg_km
    transportation_cost_per_day = truck_cost_per_km_per_m3*total_distance_kg_km/ average_manure_density_kg_per_m3 #total_distance_km*total_manure_volume_m3_per_day
    
    #print('Truck cost:',transportation_cost_per_day)
    
    
#biodigester costs    

    #print(total_lagoon_cap_m3)
    individual_biodigester_cost=biodigester_inv_ref_cost*(individual_biodigester_cap_m3/biodigester_inv_ref_capacity_m3)**Econ_scale_biodigester
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

#biomethane costs     
    biomethane_inv_cost        = biomethane_cost_per_m3*total_refinery_capacity_m3     
    biomethane_om_cost_per_day = biomethane_om_cost_per_m3*total_biomethane_m3_per_day

#compute revenue components    
    electric_revenue_per_year = rev_per_mwh*total_elect_mwh_per_day*365     
    biomethane_revenue_per_year = rev_per_biomethane_m3*total_biomethane_m3_per_day*365


#summing up the annualized costs and revenue
   
    annualize_inv_cost = (total_biodigester_inv_cost+electric_gen_inv_cost+biomethane_inv_cost)*capital_rec_factor/100
       
    annual_op_cost = biomethane_om_cost_per_day*365 + electric_om_cost_per_year + transportation_cost_per_day*365+biodigester_om_cost_per_year
    
    annual_revenue = electric_revenue_per_year+biomethane_revenue_per_year
    
    rev_dict = {
        'Electricity': electric_revenue_per_year,
        'Biomethane'        : biomethane_revenue_per_year
    }
    

    
    annualize_inv_cost_dict = {
        
        'Biodigester_Inv' : total_biodigester_inv_cost,
        'PowerPlant_Inv'  : electric_gen_inv_cost,
        'Biomethane Refinery_Inv': biomethane_inv_cost
    }
        
    annual_op_cost_dict = {
        'Biomethane Op. Cost'    : biomethane_om_cost_per_day*365,
        'Elect. Op. Cost' : electric_om_cost_per_year,
        'Truck Op. cost'  : transportation_cost_per_day*365
    }
    
    Costs_tup = (annualize_inv_cost_dict,annual_op_cost_dict)
    

#finding annual net income
    annual_net_income = annual_revenue-annualize_inv_cost-annual_op_cost
       
    # appended annualize_inv_cost, annual_net_income, annual_revenue
    return annual_net_income,Costs_tup,rev_dict, annualize_inv_cost, annual_net_income, annual_revenue


def net_co2_offset(parameters,transport_out,bio_out):

#read in parameters     
    average_manure_density_kg_per_m3           =parameters.Values[15]
    meth_m3tokg_coversion                      =parameters.Values[17]
    methtoco2_conversion                       =parameters.Values[18]
    truck_to_car_consumption_ratio             =parameters.Values[19]
    biomethane_fuel_co2_emission_kg_per_km     =parameters.Values[20]
    truck_vol_m3                               =parameters.Values[21]
    manure_collection_emissions                =parameters.Values[23]
    manure_storage_emissions                   =parameters.Values[24]
    
#read in biodigester variables
    total_methane_m3_per_day=bio_out[0].sum(axis=0)
    
#read in transport variables
    total_distance_kg_km = transport_out[0]
    total_manure_transported_kg_per_day=transport_out[1]
    total_manure_processed_kg_per_day=transport_out[2]
    
#compute co2 emissions/reduction components       
    biogas_co2_reduction_kg_per_year=total_methane_m3_per_day*meth_m3tokg_coversion*methtoco2_conversion*365
    
    #total_manure_volume_m3_per_day=total_distance_kg_km/average_manure_density_kg_per_m3   
    
#compute transport emmisions per year
    #transport_co2_emission_kg_per_year = (365*total_distance_km*(total_manure_volume_m3_per_day)*biomethane_fuel_co2_emission_kg_per_km*truck_to_car_consumption_ratio/truck_vol_m3)+(365*total_manure_transported_kg_per_day*manure_storage_emissions)
    
    
# computation based on movement_kg_km
    transport_co2_emission_kg_per_year = (365*(total_distance_kg_km/average_manure_density_kg_per_m3)*biomethane_fuel_co2_emission_kg_per_km/truck_vol_m3) + (365*total_manure_transported_kg_per_day*manure_storage_emissions) 

#compute emissions from manure collection kg/year
    collection_co2_emissions_kg_per_year = 365 * total_manure_processed_kg_per_day * (manure_collection_emissions+manure_storage_emissions)

#compute annual co2_offset 
    net_co2_offset_kg_per_year = biogas_co2_reduction_kg_per_year - transport_co2_emission_kg_per_year - collection_co2_emissions_kg_per_year
    
    return net_co2_offset_kg_per_year[0]


    
    
    
