#!/usr/bin/env python
# coding: utf-8

"""
Sustainable regional biogas networks in
Southern Brazil
Created 2021-2023
@authors: Phillip Schmedeman, Karthik Rajasekaran, Cristian Junge, Chun Hern Tan 
"""

import pandas as pd
import numpy as np

# In[18]:

def prod(design_vector, bio_out):

    # load biogas production per municipality from bio_out
    bio = bio_out.copy() # pd.read_csv('DummyBiogas.csv',index_col = 0)

    e = 0.0105 # biogas to electricity ideal conversion ( MWh/Nm3 Meth ) old 0.00624 3/7/23 KR
    c = 0.94 # Percentage of methane in biomethane
    elec_index = [[0, 0.35], [57143, 0.38], [380953, 0.45], [1428571, 0.64]] # old [[0, 0.2], [96154, 0.4], [641026, 0.6], [2403846, 0.8]], updated 3/7/23 KR
    elec_index = pd.DataFrame(elec_index, columns = ['min', 'eff'])

    # load electricity fraction from design vector
    PerElect = design_vector.loc[:,'PerElect']#
    #pd.read_csv('DummyElectFraction.csv',index_col = 0) #
    bio['PerElect'] = PerElect

    # calc proportions
    bio['BioForElect'] = bio['BiogasProd'] * bio['PerElect']
    bio['BioForCNG'] = bio['BiogasProd'] * (1-bio['PerElect'])
    bio['PerMeth'] = bio['MethProd'] / (bio['BiogasProd'] + 0.00000000001)

    # initialize columns
    bio['ElectFac'] = np.asarray(1)
    bio['ElectEff'] = np.asarray(1)
    bio['ElectProd'] = np.asarray(1)
    bio['CNGProd'] = np.asarray(1)
    
    # calculate electricity production as a function of efficiency
    for i in bio.index:
        meth = (bio.loc[i,'BioForElect']*bio.loc[i,'PerMeth'])
        if meth <= elec_index.loc[1]['min']:
            bio.loc[i,'ElectFac'] = 1
            bio.loc[i,'ElectEff'] = elec_index.loc[0]['eff'] 
            # electricity (MW) = vol biogas for electicity/day * % methane (CH4) * ideal conversion (LHV) * efficiency / 24 (conversion from MWh to MW)
            bio.loc[i,'ElectProd'] = bio.loc[i,'BioForElect'] * bio.loc[i,'PerMeth'] * bio.loc[i,'ElectEff'] * e / 24
        elif meth <= elec_index.loc[2]['min']:
            bio.loc[i,'ElectFac'] = 2
            bio.loc[i,'ElectEff'] = elec_index.loc[1]['eff']
            # electricity (MW) = vol biogas for electicity * % methane (CH4) * ideal conversion * efficiency / 24
            bio.loc[i,'ElectProd'] =  bio.loc[i,'BioForElect'] * bio.loc[i,'PerMeth'] * bio.loc[i,'ElectEff'] * e / 24
        elif meth <= elec_index.loc[3]['min']:
            bio.loc[i,'ElectFac'] = 3
            bio.loc[i,'ElectEff'] = elec_index.loc[2]['eff']
            # electricity (MW) = vol biogas for electicity * % methane (CH4) * ideal conversion * efficiency / 24
            bio.loc[i,'ElectProd'] = bio.loc[i,'BioForElect'] * bio.loc[i,'PerMeth'] * bio.loc[i,'ElectEff'] * e / 24
        else:
            bio.loc[i,'ElectFac'] = 4
            bio.loc[i,'ElectEff'] = elec_index.loc[3]['eff']
            # electricity (MW) = vol biogas for electicity * % methane (CH4) * ideal conversion * efficiency / 24
            bio.loc[i,'ElectProd'] = bio.loc[i,'BioForElect'] * bio.loc[i,'PerMeth'] * bio.loc[i,'ElectEff'] * e / 24

    # calculate CNG production
    for i in bio.index:
        # volume CNG (m**3/day) = vol biogas for CNG (m**3/day) * % methane (CH4) / c
        bio.loc[i,'CNGProd'] = bio.loc[i,'BioForCNG'] * bio.loc[i,'PerMeth']/c

    # sum total capacities for Electicity and CNG
    # total capacities (MW/24hr) = sum of output across all municipalities 

    
    TotCNGCap = bio['CNGProd'].sum()/24
    
    TotElectProd = bio['ElectProd'].sum()*24
    
    TotCNGProd = bio['CNGProd'].sum()
    # TotElectCap = bio['ElectProd'].sum()/24

    return bio, TotCNGCap, TotElectProd, TotCNGProd

# In[ ]:
