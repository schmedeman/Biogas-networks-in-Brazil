#!/usr/bin/env python
# coding: utf-8

# In[2]:


# import pandas to work with data frames
import pandas as pd


# In[11]:


# import input design vector
# BioParameters = pd.read_csv('Biodigester module data.csv',index_col=0)


# read in the output matrix from the Transport module
# MovementsKg = pd.read_csv('Transport module output.csv',index_col=0)


def biomodulefunction(BioParameters,MovementsKg):

    # calculate the amount of manure in each municipality each day, on the rows of the output from the transport module
    finalmanure = MovementsKg.sum(axis=1)

        # calculate size (m3) of the biodigester in each municipality - convert from kg/day of manure to m3/day, assuming manure = water in density, and multiply by 17 days for an average hydraulic retention time
    
    
    Biodigsize = finalmanure*(1/1000)*17
    Biodigsize = pd.DataFrame(Biodigsize,columns = ['Biodigsize'])
    
    # calculate the biogas production in each municipality based on the manure coming in to it:
    # had to use .values here or pandas wouldn't multiply properly
    BiogasProd = MovementsKg.dot(BioParameters.iloc[:,6].values)
    BiogasProd = pd.DataFrame(BiogasProd,columns = ['BiogasProd'])
    
    
    # then calculate the total methane production in each municipality based on the manure coming in to it:
    MethProd = MovementsKg.dot(BioParameters.iloc[:,7].values)
    
    MethProd = pd.DataFrame(MethProd,columns = ['MethProd'])


    return Biodigsize,BiogasProd,MethProd

