def stringToFloat(s):
    try:
        return float(s)
    except ValueError as e:
        return 0.0

# Given a temperature in fahrenheit, return the temperature in celcius 
def fahrenheitToCelsius(f):
    return (f - 32) * 5.0/9.0

def fahrenheitToCentigrade(f):
    return f * 5.0/9.0

# Returns the data center energy use, in MW, given temperature in celcius 
def dataCenterEnergyUse(t):
    gridHookup = 286.0
    itLoad = 0.6 * 286.0
    coolingCOP = 4.396 
    itTemperature = fahrenheitToCelsius(85.0)
    maxTemp = fahrenheitToCelsius(120.0)
    slope = (gridHookup - (itLoad + (itLoad/coolingCOP))) / (maxTemp - itTemperature)
    coolingLoad = max((itLoad/coolingCOP) + (slope * (t - itTemperature)), 0)
    return min(gridHookup, itLoad + coolingLoad)
