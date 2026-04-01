#!/usr/bin/python3 

# This script, given the manufacturer specs, calculates how much energy will be
# generated in Tucson, in a given year (assume no cloudy days)
# https://sunwatts.com/395-watt-canadian-solar-mono-all-black-solar-panel-1/

from numpy import array
from solarpy import solar_panel
from datetime import datetime, timedelta
import math 

panelSurfaceArea=1.722 * 1.134
panelEfficiency=0.202
pannelAdvertisedkW=0.395

solarAngle = math.radians(-32)
panel = solar_panel(panelSurfaceArea, panelEfficiency, id_name='Tucson')  # surface, efficiency and name
panel.set_orientation(array([math.sin(solarAngle), 0, -1 * math.cos(solarAngle)]))  # upwards
panel.set_position(32.2540, 110.9742, 0)  # Tucson latitude, longitude, altitude

count = 0
cumulativeEnergyPerYear = 0.0

# Iterate through a year 
while count < (24 * 365):
    start_date = datetime(2024, 1, 1)
    target_date = start_date + timedelta(days=count % 24)
    panel.set_datetime(datetime(2024, target_date.month, target_date.day, count % 24, 0)) 
    panelOutput = panel.power()
    cumulativeEnergyPerYear = cumulativeEnergyPerYear + (panelOutput/1e3)
    count = count + 1

print("Cumulative Energy: " + str(cumulativeEnergyPerYear/pannelAdvertisedkW) + " kWh/yr/kW")
    
    
