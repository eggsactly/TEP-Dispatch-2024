#!/usr/bin/python3

import csv

with open('TEP-Dispatch-2024.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    dispatch = []
    for row in spamreader:
        dispatch.append(row)
        
    purchaseList = []
    firstIteration = True
    
    energyImports = {'azps': []
        , 'epe': []
        , 'pnm': []
        , 'srp': []
        , 'walc': []
        , 'data': []
    } 
    
    for row in dispatch[1:]:
        try:
            energyImports['azps'].append(float(row[11]))
        except ValueError as e:
            pass
        try:
            energyImports['epe'].append(float(row[12]))
        except ValueError as e:
            pass
        try:
            energyImports['pnm'].append(float(row[13]))
        except ValueError as e:
            pass
        try:
            energyImports['srp'].append(float(row[14]))
        except ValueError as e:
            pass
        try:
            energyImports['walc'].append(float(row[15]))
        except ValueError as e:
            pass
        try:
            energyImports['data'].append(float(row[17]))
        except ValueError as e:
            pass
        
    totalSum = abs(sum(energyImports['azps'])) + abs(sum(energyImports['epe'])) + abs(sum(energyImports['pnm'])) + abs(sum(energyImports['srp'])) + abs(sum(energyImports['walc']))
    
    importNames = {'azps': "Arizona Public Service (AZPS): "
        , 'epe': "El Paso Electric Company (EPE): "
        , 'pnm': "Public Service Company of New Mexico (PNM): "
        , 'srp': "Salt River Project (SRP): " 
        , 'walc': "Western Power Area Administration (WALC): "
    } 
    
    maxWidth = max(len(importNames['azps']), len(importNames['epe']), len(importNames['pnm']), len(importNames['srp']), len(importNames['walc']))
    
    print("Utility".ljust(maxWidth) + "Interchange GWh (positive is out, negative is in)")
    print(importNames['azps'].ljust(maxWidth) + str(sum(energyImports['azps'])/1000).ljust(len("Interchange GWh")) + " " + ("%.2f" % (sum(energyImports['azps']) * 100 / totalSum)) + "%")
    print(importNames['epe'].ljust(maxWidth) + str(sum(energyImports['epe'])/1000).ljust(len("Interchange GWh")) + " " + ("%.2f" % (sum(energyImports['epe']) * 100 / totalSum)) + "%")
    print(importNames['pnm'].ljust(maxWidth) + str(sum(energyImports['pnm'])/1000).ljust(len("Interchange GWh")) + " " + ("%.2f" % (sum(energyImports['pnm']) * 100 / totalSum)) + "%")
    print(importNames['srp'].ljust(maxWidth) + str(sum(energyImports['srp'])/1000).ljust(len("Interchange GWh")) + " " + ("%.2f" % (sum(energyImports['srp']) * 100 / totalSum)) + "%")
    print(importNames['walc'].ljust(maxWidth) + str(sum(energyImports['walc'])/1000).ljust(len("Interchange GWh")) + " " + ("%.2f" % (sum(energyImports['walc']) * 100 / totalSum)) + "%")
    
    # Print net energy imports 
    print("Sum: ".ljust(maxWidth) + str(
        (sum(energyImports['azps']) 
        + sum(energyImports['epe']) 
        + sum(energyImports['pnm']) 
        + sum(energyImports['srp']) 
        + sum(energyImports['walc'])
        )/1000))
    
    netEnergyInterchange = {}
    # Calculate net energy sold per utility 
    for key in energyImports:
        count = 0
        netEnergyInterchange[key] = {'imports': 0, 'exports': 0}
        while count < len(energyImports[key]):
            value = energyImports[key][count]
            if value < 0:
                netEnergyInterchange[key]['imports'] = netEnergyInterchange[key]['imports'] - value
            else:
                netEnergyInterchange[key]['exports'] = netEnergyInterchange[key]['exports'] + value
            count = count + 1
    
    # Calculate total energy sold and total energy imported 
    totalEnergySold = 0.0
    totalEnergyImported = 0.0
    for key in energyImports:
        totalEnergySold = netEnergyInterchange[key]['exports'] + totalEnergySold
        totalEnergyImported = netEnergyInterchange[key]['imports'] + totalEnergyImported
        
    print("Total Energy Sold (GWh): " + "%2.f" % (totalEnergySold/1000))    
    print("Total Energy Imported (GWh): " + "%2.f" % (totalEnergyImported/1000))    
    
    
    print("Data center energy use (GWh): " + "%2.f" % (sum(energyImports['data'])/1000))
    
    
