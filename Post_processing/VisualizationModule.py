# Regional analysis of biogas production
# VISUALIZATION MODULE
# V A5
# MIT - Spring 2021
########################################
"""
Created on Thu Apr 15 14:47:16 2021

@author: cristianjunge
"""


from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shapely.ops as so

import matplotlib as mpl

#import geobr



def get_muni_centroids(MuniGeom,muniscopeID):
    
    ## Get the centroids of the selected municipalities
    

    MuniGeom_select = MuniGeom[MuniGeom.code_muni.isin(muniscopeID)]
    
    MuniGeom_select.index = MuniGeom_select.code_muni


    centroids_dict = {}

    for m in MuniGeom_select.index:
    
        centroid_txt = MuniGeom_select.loc[m,'geometry'].centroid.wkt
    
        Lat  = float(centroid_txt.split(' ')[2].split(')')[0])
        Long = float(centroid_txt.split(' ')[1].split('(')[1])

        centroids_dict[m] = [Lat,Long]
    
    return centroids_dict,MuniGeom_select




def PlotMuni_filled(axs,Geom,Data,data_column,color_interpol):
    
    ## Geom is the dataframe containing the polygons
    #  Data is a dataframe containing the data to plot
    #  data_column is the column pof the dataframe that contains the data
    #  color_interpol is a list with two colors to interpolate fo color the faces
    
    c1 = color_interpol[0]
    c2 = color_interpol[1]
    data_min = color_interpol[2]
    data_max = color_interpol[3]
    
    for i in Geom.index:
        
        pol_i = Geom.loc[i,'geometry']
        
        data_i = Data.loc[i,data_column]
        
        color_i = (data_i-data_min)/(data_max-data_min)
        
        if pol_i.geom_type =='Polygon':
        
            xs, ys = pol_i.exterior.xy 
        
            axs.fill(xs, ys ,
                 facecolor = colorFader(c1,c2,color_i),
                 edgecolor='k', linewidth=0.2)
            
        else:
        
            for k in range(len(pol_i)):
            
                xs, ys = pol_i[k].exterior.xy  
            
                axs.fill(xs, ys, 
                     facecolor = colorFader(c1,c2,color_i),
                     edgecolor='k', linewidth=0.2)


    axs.axis('off')

def plotTransportation(axs,TransportMatrix,centroids_dict):
    
    ## Clean diagonal:
        
    TransportMatrix_Nodiag    = TransportMatrix.copy()
        
    for m in TransportMatrix.index:
        
        TransportMatrix_Nodiag.loc[m,m] = 0
    
    
    max_mov = TransportMatrix_Nodiag.max().max()
    
    for m in TransportMatrix_Nodiag.index:
        
        l1 = centroids_dict[m]
        
        for c in TransportMatrix_Nodiag.columns:

            mov = TransportMatrix_Nodiag.loc[m,c]
            if mov >0:
                
                l2 = centroids_dict[c]
                
                x = [l1[1],l2[1]]
                y = [l1[0],l2[0]]
                
                axs.plot(x,y,linewidth=4*mov/max_mov,color = 'k')

def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

def round_to(n,toN): 
    n2 = round(n/toN)*toN    # n is integer or float
    return n2





def plotFader(axs,color_interpol,ticks_setup):
    
    
    n = 500
    
    c1 = color_interpol[0]
    c2 = color_interpol[1]
    data_min = color_interpol[2]
    data_max = color_interpol[3]
    
    n_ticks = ticks_setup[0]
    scale   = ticks_setup[1]
    toN     = ticks_setup[2]
    
        
    for x in range(n+1):
        axs.axhline(x, color=colorFader(c1,c2, x/n  ), linewidth=4) 
    
    axs.set_ylim([0,n])   
    
    ticks = np.linspace(data_min,data_max,num=n_ticks)/scale

    ticks_round = [int(round_to(n,toN)) for n in ticks]
    
    axs.set_xticks([])

    axs.set_yticklabels(ticks_round)
    
def plotSolution(MuniGeom_select,centroids_dict,BioParameters,Demand,MovementsKg,ax):
    
    
    c1='#1f77b4' #blue
    c2='orangered' #green
    
    

    data_plot = BioParameters.copy()
    Variable  = 'Manure generated (kg/day)'


    data_max = max(max(data_plot[Variable]),Demand.max()[0])

    data_min = min(min(data_plot[Variable]),Demand.min()[0])

    color_interpol = [c1,c2,data_min,data_max]

    PlotMuni_filled(ax[0],MuniGeom_select,
                data_plot,Variable,
                color_interpol)

    ax[0].set_title('Manure Supply')

    ax[1].set_title('Manure Demand and Movements')

    PlotMuni_filled(ax[1],MuniGeom_select,
                Demand,'Demand0',
                color_interpol)

    plotFader(ax[2],color_interpol,[6,1000000,1])

    plotTransportation(ax[1],MovementsKg,centroids_dict)

def normalize_dv(DesignVector,Supply):
    
    ## Returns a normaulized design vector
    norm_dv = DesignVector.copy()
    for i in DesignVector.index:
        
        norm_dv.loc[i,'Demand0'] = norm_dv.loc[i,'Demand0']/Supply.loc[i,'Supply0']
        
    return norm_dv
        
def DV2Array(DesignVector):
    
    x = list(DesignVector['Demand0'])
    x = x + list(DesignVector['PerElect'])
    
    return x    



