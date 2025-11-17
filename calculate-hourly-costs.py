#!/usr/bin/python3

import csv

# This script is similar to plot-2024-ave.py, except instead of putting everything
# into one week for easy visualization, it will calculate across the whole year

def stringToFloat(s):
    try:
        return float(s)
    except ValueError as e:
        return 0.0

# Given a temperature in fahrenheit, return the temperature in celcius 
def fahrenheitToCelsius(f):
    return (f - 32) * 5.0/9.0

# Returns the data center energy use, in MW, given temperature in celcius 
def dataCenterEnergyUse(t):
    gridHookup = 286.0
    itLoad = 0.6 * 286.0
    coolingCOP = 4.0 
    itTemperature = fahrenheitToCelsius(85.0)
    maxTemp = fahrenheitToCelsius(125.0)
    slope = (gridHookup - (itLoad + (coolingCOP * itLoad))) / (maxTemp - itTemperature)
    coolingLoad = (coolingCOP * itLoad) + (slope * t)
    return min(gridHookup, itLoad + coolingLoad)

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
    } 
    
    importNames = {'azps': "Arizona Public Service (AZPS): "
        , 'epe': "El Paso Electric Company (EPE): "
        , 'pnm': "Public Service Company of New Mexico (PNM): "
        , 'srp': "Salt River Project (SRP): " 
        , 'walc': "Western Power Area AdataCenterEnergyUsedministration (WALC): "
    }
    
    # Read in the data 
    for row in dispatch[1:]:
        energyImports['demand'].append(stringToFloat(row[2]))
        energyImports['wind'].append(stringToFloat(row[6]))
        energyImports['solar'].append(stringToFloat(row[7]))
        energyImports['other'].append(stringToFloat(row[8]))
        energyImports['gas'].append(stringToFloat(row[9]))
        energyImports['coal'].append(stringToFloat(row[10]))
        energyImports['azps'].append(stringToFloat(row[11]))
        energyImports['epe'].append(stringToFloat(row[12]))
        energyImports['pnm'].append(stringToFloat(row[13]))
        energyImports['srp'].append(stringToFloat(row[14]))
        energyImports['walc'].append(stringToFloat(row[15]))
        energyImports['data'].append(stringToFloat(row[17]))
        energyImports['cost'].append(stringToFloat(row[18]))
        energyImports['temp'].append(stringToFloat(row[16]))
        
    totalImports = 0.0
    totalCost = 0.0
    totalExports = 0.0
    totalRevenue = 0.0
    totalImportsDataC = 0.0
    totalCostDataC = 0.0
    totalExportsDataC = 0.0
    totalRevenueDataC = 0.0
    # Calculate the energy costs, hour-by-hour 
    count = 0
    while count < len(energyImports['azps']):
        hourlyImport = -1.0 * min(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count], 0)
        hourlyExport = max(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count], 0)
        totalImports = totalImports +  hourlyImport
        totalExports = totalExports + hourlyExport
        hourlyCost = hourlyImport * energyImports['cost'][count]
        totalCost = totalCost + hourlyCost
        hourlyRevenue = hourlyExport * energyImports['cost'][count]
        totalRevenue = totalRevenue + hourlyRevenue
        
        hourlyImportDataC = -1.0 * min(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count] - dataCenterEnergyUse(energyImports['temp'][count]), 0)
        hourlyExportDataC = max(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count] - dataCenterEnergyUse(energyImports['temp'][count]), 0)
        totalImportsDataC = totalImportsDataC +  hourlyImportDataC
        totalExportsDataC = totalExportsDataC + hourlyExportDataC
        hourlyCostDataC = hourlyImportDataC * energyImports['cost'][count]
        totalCostDataC = totalCostDataC + hourlyCostDataC
        hourlyRevenueDataC = hourlyExportDataC * energyImports['cost'][count]
        totalRevenueDataC = totalRevenueDataC + hourlyRevenueDataC
        
        count = count + 1
    
    
    totalSum = abs(sum(energyImports['azps'])) + abs(sum(energyImports['epe'])) + abs(sum(energyImports['pnm'])) + abs(sum(energyImports['srp'])) + abs(sum(energyImports['walc']))
    
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
    
    print("")
    
    print("Typical: ")
    print("Total Imports (GWh): " + "%.2f" % (totalImports/1000))
    print("Total Cost ($): " + "%.2f" % (totalCost))
    print("Cost per MWh: " + "%.2f" % (totalCost/totalImports))
    print("Total Exports (GWh): " + "%.2f" % (totalExports/1000))
    print("Total Revenue ($): " + "%.2f" % (totalRevenue))
    print("Revenue per MWh: " + "%.2f" % (totalRevenue/totalExports))
    print("")
    print("With Datacenter: ")
    print("Total Imports (GWh): " + "%.2f" % (totalImportsDataC/1000))
    print("Total Cost ($): " + "%.2f" % (totalCostDataC))
    print("Cost per MWh: " + "%.2f" % (totalCostDataC/totalImportsDataC))
    print("Total Exports (GWh): " + "%.2f" % (totalExportsDataC/1000))
    print("Total Revenue ($): " + "%.2f" % (totalRevenueDataC))
    print("Revenue per MWh: " + "%.2f" % (totalRevenueDataC/totalExportsDataC))
    print("")
    print("Difference in energy imports (GWh): " + "%.2f" % ((totalImportsDataC - totalImports)/1000))
    print("Difference in revenue ($): " + "%.2f" % (((totalRevenueDataC - totalRevenue) - (totalCostDataC - totalCost))))
    print("")
    print("Data center energy use (GWh): " + "%2.f" % (sum(energyImports['data'])/1000))
    
    
