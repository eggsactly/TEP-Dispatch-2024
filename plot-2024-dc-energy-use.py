#!/usr/bin/python3

import csv
from numpy import array
from solarpy import solar_panel
from datetime import datetime, timedelta
import math 
from lib.ProjectBlue import * 
import matplotlib.pyplot as plt

with open('TEP-Dispatch-2024.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    dispatch = []
    for row in spamreader:
        dispatch.append(row)
        
    purchaseList = []
    firstIteration = True
    
    energyImports = {
        'demand': []
        , 'wind': []
        , 'solar': []
        , 'other': []
        , 'gas': []
        , 'coal': []
        ,'newGas': []
        ,'azps': []
        , 'epe': []
        , 'pnm': []
        , 'srp': []
        , 'walc': []
        , 'data': []
        , 'cost': []
        , 'temp': []
        ,'co2e':[]
    } 
    
    importNames = {'azps': "Arizona Public Service (AZPS): "
        , 'epe': "El Paso Electric Company (EPE): "
        , 'pnm': "Public Service Company of New Mexico (PNM): "
        , 'srp': "Salt River Project (SRP): " 
        , 'walc': "Western Power Area AdataCenterEnergyUsedministration (WALC): "
    }
    
    # Read in the data 
    for row in dispatch[1:]:
        energyImports['temp'].append(stringToFloat(row[16]))
    
    hoursInADay = 24
    
    labels = []
    # initialize hourlyEnergyUse to be a 24 element array of elements 
    hourlyEnergyUse = []
    count = 0
    while count < hoursInADay:
        hourlyEnergyUse.append([])
        count = count + 1
        labels.append(str(count))
    
    # loop through every day, accumlating energy use
    count = 0
    while count < len(energyImports['temp']):
        hourlyEnergyUse[count % hoursInADay].append(dataCenterEnergyUse(energyImports['temp'][count]))
        count = count + 1 
    
    fruit_weights = hourlyEnergyUse

    fig, ax = plt.subplots()
    plt.title("Project Blue, Tucson (2024) (Hypothetical)")
    ax.set_ylabel('Energy Use (MWh)')
    ax.set_xlabel('Time of Day')
    plt.ylim(0, 286)

    bplot = ax.boxplot(fruit_weights,
                       patch_artist=True,  # fill with color
                       )  # will be used to label x-ticks


    plt.legend()

    plt.savefig('project-blue-energy-use-bar-and-whisker.png', dpi=100)
    #plt.show()
    plt.clf()
    
