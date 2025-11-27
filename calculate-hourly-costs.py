#!/usr/bin/python3

import csv
from numpy import array
from solarpy import solar_panel
from datetime import datetime, timedelta
import math 
from lib.ProjectBlue import * 
# This script is similar to plot-2024-ave.py, except instead of putting everything
# into one week for easy visualization, it will calculate across the whole year


# Parameters 
costFactor = 1.0
tempOffset = fahrenheitToCentigrade(0)
tempFactor = 1.00

# For exploring how many renewables the data center needs 
# Surface area in meters
panelSurfaceArea = 0.0
storageCapacity = 0.0
panelSurfaceArea = 9000000.0
storageCapacity = 4170.0


# Setting turnOffDataCenter to True will shut off data center between 6 and 7pm
turnOffDataCenter = False

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
        energyImports['co2e'].append(stringToFloat(row[21]))
        
        
    totalImports = 0.0
    totalCost = 0.0
    totalExports = 0.0
    totalRevenue = 0.0
    totalImportsDataC = 0.0
    totalCostDataC = 0.0
    totalExportsDataC = 0.0
    totalRevenueDataC = 0.0
    co2EDataC = 0.0
    peakEnergyUseDataC = [0.0, 0.0]
    peakEnergyUseDataC2 = [0.0, 0.0]
    peakEnergyUseDataC3 = [0.0, 0.0]
    energyUsedDataC = 0.0
    previousDataCenterUse = 0.0
    dataCenterOffUse = 0.0
    # Calculate the energy costs, hour-by-hour 
    count = 0
    
    dataCenterGridUseWithRenewables = 0.0
    dataCenterEmissionsWithRenewables = 0.0
    currentStorage = 0.0
    
    while count < len(energyImports['azps']):
        hourlyImport = -1.0 * min(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count], 0)
        hourlyExport = max(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count], 0)
        totalImports = totalImports +  hourlyImport
        totalExports = totalExports + hourlyExport
        hourlyCost = hourlyImport * (costFactor * energyImports['cost'][count])
        totalCost = totalCost + hourlyCost
        hourlyRevenue = hourlyExport * (costFactor * energyImports['cost'][count])
        totalRevenue = totalRevenue + hourlyRevenue
        
        
        
        if (count % 17 == 0 or count % 18 == 0):
            dataCenterOffUse = dataCenterOffUse + dataCenterEnergyUse(tempFactor * energyImports['temp'][count] + tempOffset)
        
        # Turn off data center at 6pm and 7pm 
        if turnOffDataCenter and (count % 17 == 0 or count % 18 == 0):
            hourlyImportDataC = -1.0 * min(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count], 0)
            hourlyExportDataC = max(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count], 0)
        else:
            dataCenterUse = dataCenterEnergyUse(tempFactor * energyImports['temp'][count] + tempOffset)
            energyUsedDataC = energyUsedDataC + dataCenterUse
            hourlyImportDataC = -1.0 * min(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count] - dataCenterUse, 0)
            hourlyExportDataC = max(energyImports['azps'][count] + energyImports['epe'][count] + energyImports['pnm'][count] + energyImports['srp'][count] + energyImports['walc'][count] - dataCenterUse, 0)
            
            # We're only looking at storing power for two hours because 6 and 7pm are the most expensive hours 
            co2EDataC = co2EDataC + (dataCenterUse * energyImports['co2e'][count])
            if (dataCenterUse + previousDataCenterUse) > (peakEnergyUseDataC[0] + peakEnergyUseDataC[1]):
                peakEnergyUseDataC3[1] = peakEnergyUseDataC2[1]
                peakEnergyUseDataC3[0] = peakEnergyUseDataC2[0]
                peakEnergyUseDataC2[1] = peakEnergyUseDataC[1]
                peakEnergyUseDataC2[0] = peakEnergyUseDataC[0]
                peakEnergyUseDataC[1] = previousDataCenterUse
                peakEnergyUseDataC[0] = dataCenterUse
                
            
            
            previousDataCenterUse = dataCenterUse
            
            # Given renewables (solar) and batteries, calculate grid use 
            start_date = datetime(2024, 1, 1)
            target_date = start_date + timedelta(days=count % 24)

            solarAngle = math.radians(-32)
            panel = solar_panel(panelSurfaceArea, 0.2, id_name='Tucson')  # surface, efficiency and name
            panel.set_orientation(array([math.sin(solarAngle), 0, -1 * math.cos(solarAngle)]))  # upwards
            panel.set_position(32.2540, 110.9742, 0)  # Tucson latitude, longitude, altitude
            panel.set_datetime(datetime(2024, target_date.month, target_date.day, count % 24, 0)) 
            # Panel output in MWh
            panelOutput = panel.power()/1e6
            
            storageEfficiency = 0.8 # https://www.eia.gov/todayinenergy/detail.php?id=46756
            # If panel output exceeds the data center use
            if panelOutput > dataCenterUse:
                # Add to current storage until we hit capacity 
                currentStorage = min(storageCapacity, currentStorage + panelOutput - dataCenterUse)
            else:
                # If panel and storage exceeds data center needs
                if panelOutput + (storageEfficiency * currentStorage) > dataCenterUse:
                    currentStorage = max(0, currentStorage - ((1/storageEfficiency)*(dataCenterUse - panelOutput)))
                # If storage and solar do not exceed data center needs 
                else:
                    # Use what is left in the panels and remove whatever is left in storage 
                    dataCenterGridUseWithRenewables = dataCenterGridUseWithRenewables + (dataCenterUse - panelOutput - (storageEfficiency * currentStorage))
                    dataCenterEmissionsWithRenewables = dataCenterEmissionsWithRenewables + ((dataCenterUse - panelOutput - (storageEfficiency * currentStorage)) * energyImports['co2e'][count])
                    # Zero out storage
                    currentStorage = 0.0 
            
            
        totalImportsDataC = totalImportsDataC +  hourlyImportDataC
        totalExportsDataC = totalExportsDataC + hourlyExportDataC
        hourlyCostDataC = hourlyImportDataC * (costFactor * energyImports['cost'][count])
        totalCostDataC = totalCostDataC + hourlyCostDataC
        hourlyRevenueDataC = hourlyExportDataC * (costFactor * energyImports['cost'][count])
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
    print("Data center energy use (GWh): " + "%2.f" % (energyUsedDataC))
    print("Data center energy emissions (kg CO2): " + "%2.f" % (co2EDataC))
    if turnOffDataCenter:
        print("Battery Capacity Needed for 2 hours (MWh): " + "%2.f" % peakEnergyUseDataC[0] + " + " + "%2.f" % peakEnergyUseDataC[1] + " = " + "%2.f" % (sum(peakEnergyUseDataC)))
        print("Battery Capacity Needed for 2 hours (MWh): " + "%2.f" % peakEnergyUseDataC2[0] + " + " + "%2.f" % peakEnergyUseDataC2[1] + " = " + "%2.f" % (sum(peakEnergyUseDataC2)))
        print("Battery Capacity Needed for 2 hours (MWh): " + "%2.f" % peakEnergyUseDataC3[0] + " + " + "%2.f" % peakEnergyUseDataC3[1] + " = " + "%2.f" % (sum(peakEnergyUseDataC3)))
        print("Data center energy use in that time (MWh): " + str(dataCenterOffUse))
    print("Data Center Grid Use with Renewables (MWh):" + "%2.f" % (dataCenterGridUseWithRenewables))
    print("Data Center Emissions with Renewables (CO2e):" + "%2.f" % (dataCenterEmissionsWithRenewables))
    
