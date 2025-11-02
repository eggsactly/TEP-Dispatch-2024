#!/usr/bin/python3

import csv
import datetime
from operator import itemgetter
import matplotlib.pyplot as plt
import copy
import sys

# year month day
def zeller(y, m, q):
    if m < 3:   
        m += 12
        y -= 1

    k = y % 100  # yearpart
    j = y // 100 # century

    h = (q + (13 * (m + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7 
    
    return h

def findWeekOfPeak(dispatch):
    count  = 0
    largest = 0.0
    indexOfLargest = 0
    date = ''
    # This loop finds the row of the peak power demand
    for row in dispatch[1:]:
        try:
            if float(row[2]) > largest:
                largest = float(row[2])
                indexOfLargest = count
                date = row[1]
        except ValueError as e:
            print("Error: " + str(e) + " row: " + str(count))
        count = count + 1
        
    return largest, indexOfLargest, date

def stringToDate(date):
    dateArray = str(date).split(' ')[0].split('/')
    month = int(dateArray[0])
    day = int(dateArray[1])
    year = int(dateArray[2])
    timeString = str(date).split(' ')[1] + " " + str(date).split(' ')[2]
    isPm = str(date).split(' ')[2] == "p.m."
    timeOffset = int(str(date).split(' ')[1]) + (isPm * 12)
    timeInt = int(str(date).split(' ')[1])
    return month, day, year, isPm, timeInt, timeOffset

dispatch = []

with open('TEP-Dispatch-2024.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        dispatch.append(row)
    
    print(str(dispatch[0]))
    
    largest, indexOfLargest, date = findWeekOfPeak(dispatch)
        
    month, day, year, isPm, timeInt, timeOffset = stringToDate(date)
    
    
    
    theday = datetime.datetime(year, month, day)
    print(str(date) + " largest: " + str(largest) + " indexOfLargest: " + str(indexOfLargest))
    print(str(year) + " " + str(month) + " " + str(day))
    print(str(zeller(year,month,day)))
    print(str(timeOffset))
    
    indexOfSunday = indexOfLargest - (24*zeller(year,month,day)) - timeOffset
    print("index of sunday of hottest week: " + str(indexOfSunday))
    
    # copy all 
    worstCaseUnsorted = dispatch[indexOfSunday:(indexOfSunday+168)]
    
    sizeOfStorageMWh = 3000.0
    
    worstCaseUnsortedWithStorage = copy.deepcopy(worstCaseUnsorted)
    count = 0
    while count < len(worstCaseUnsortedWithStorage):
        date = worstCaseUnsortedWithStorage[count][1]
        month, day, year, isPm, timeInt, timeOffset = stringToDate(date)
        
        if(isPm and timeInt >= 2 and timeInt <= 8):
            worstCaseUnsortedWithStorage[count][8] = float(worstCaseUnsortedWithStorage[count][8]) + sizeOfStorageMWh/6
        count = count + 1
    
    print("Len: " + str(len(worstCaseUnsorted)))
    
    worstCase = sorted(worstCaseUnsorted, key=itemgetter(2), reverse=True)
    worstCaseWithStorage = sorted(worstCaseUnsortedWithStorage, key=itemgetter(2), reverse=True)
    
    # Build up the worst case column 
    worstCaseColumns = []
    for i in worstCase[0]:
        worstCaseColumns.append([])
        
        
    print("worstCaseColumns length: " + str(len(worstCaseColumns)))
    for row in worstCase:
        count = 0
        for item in row:
            try:
                worstCaseColumns[count].append(float(item))
            except ValueError:
                worstCaseColumns[count].append((item))
            count = count + 1
    
    highestValue = max(worstCaseColumns[2])
    
    hoursInWeek = list(range(0,168))
    
    print(str(worstCaseColumns[2]))
    print("highestValue: " + str(highestValue))
    
    coal = []
    gas = []
    solar = []
    wind = []
    other = []
    spotPurchases = []
    count = 0
    wh_purchased1 = 0.0
    wh_hours1 = 0
    for i in worstCaseColumns[2]:
        coal.append(worstCaseColumns[10][count])
        solar.append(worstCaseColumns[10][count] + worstCaseColumns[7][count])
        wind.append(worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count])
        gas.append(min(worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count] + worstCaseColumns[9][count], worstCaseColumns[2][count] + worstCaseColumns[12][count]))
        other.append(min(worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count] + worstCaseColumns[9][count] + worstCaseColumns[8][count], worstCaseColumns[2][count] + worstCaseColumns[12][count]))
        spotPurchases.append(worstCaseColumns[2][count] + worstCaseColumns[12][count])
        wh_hours1 = wh_hours1 + int((worstCaseColumns[2][count] + worstCaseColumns[12][count]) > (worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count] + worstCaseColumns[9][count] + worstCaseColumns[8][count]))
        wh_purchased1 = wh_purchased1 + max(0, (worstCaseColumns[2][count] + worstCaseColumns[12][count]) - (worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count] + worstCaseColumns[9][count] + worstCaseColumns[8][count]))
        count = count + 1
    
    print(str(spotPurchases))
    fig = plt.figure(figsize=(8, 6), dpi=100)
    
    print("Wh Purchased DC: " + str(wh_purchased1))
    print("Num hours with purchase DC: " + str(wh_hours1))
    
    print(str(len(spotPurchases)) + " " + str(len(hoursInWeek)))
    
    plt.plot(hoursInWeek, spotPurchases, label="demand", color='black')
    plt.fill_between(hoursInWeek, spotPurchases, label="spot purchases", color='grey')
    plt.fill_between(hoursInWeek, other, label="other", color='white')
    plt.fill_between(hoursInWeek, gas, label="fracked gas", color='brown')
    plt.fill_between(hoursInWeek, wind, label="wind", color='blue')
    plt.fill_between(hoursInWeek, solar, label="solar", color='yellow')
    plt.fill_between(hoursInWeek, coal, label="coal", color='black')
    
    
    plt.title("TEP Dispatch Curve Week of July 5th 2024 With Datacenter")
    plt.xlim(0, 167)
    plt.ylim(0, max(spotPurchases))
    
    plt.legend()

    plt.savefig('july-5-2024-datacenter.png', dpi=100)
    #plt.show()
    plt.clf()
    
    
    worstCaseWithStorage
    
    # Build up the worst case column 
    worstCaseWithStorageColumns = []
    for i in worstCaseWithStorage[0]:
        worstCaseWithStorageColumns.append([])
        
        
    print("worstCaseWithStorage length: " + str(len(worstCaseWithStorage)))
    for row in worstCaseWithStorage:
        count = 0
        for item in row:
            try:
                worstCaseWithStorageColumns[count].append(float(item))
            except ValueError:
                worstCaseWithStorageColumns[count].append((item))
            count = count + 1
    
    coal = []
    gas = []
    solar = []
    wind = []
    other = []
    spotPurchases = []
    count = 0
    wh_purchased3 = 0.0
    wh_hours3 = 0
    for i in worstCaseWithStorageColumns[2]:
        coal.append(worstCaseWithStorageColumns[10][count])
        solar.append(worstCaseWithStorageColumns[10][count] + worstCaseWithStorageColumns[7][count])
        wind.append(worstCaseWithStorageColumns[10][count] + worstCaseWithStorageColumns[7][count] + worstCaseWithStorageColumns[6][count])
        gas.append(min(worstCaseWithStorageColumns[10][count] + worstCaseWithStorageColumns[7][count] + worstCaseWithStorageColumns[6][count] + worstCaseWithStorageColumns[9][count], worstCaseWithStorageColumns[2][count] + worstCaseWithStorageColumns[17][count]))
        other.append(min(worstCaseWithStorageColumns[10][count] + worstCaseWithStorageColumns[7][count] + worstCaseWithStorageColumns[6][count] + worstCaseWithStorageColumns[9][count] + worstCaseWithStorageColumns[8][count], worstCaseWithStorageColumns[2][count] + worstCaseWithStorageColumns[17][count]))
        spotPurchases.append(worstCaseWithStorageColumns[2][count] + worstCaseWithStorageColumns[17][count])
        wh_hours3 = wh_hours3 + int((worstCaseWithStorageColumns[2][count] + worstCaseWithStorageColumns[17][count]) > worstCaseWithStorageColumns[10][count] + worstCaseWithStorageColumns[7][count] + worstCaseWithStorageColumns[6][count] + worstCaseWithStorageColumns[9][count] + worstCaseWithStorageColumns[8][count])
        wh_purchased3 = wh_purchased3 + max(0, worstCaseWithStorageColumns[2][count] + worstCaseWithStorageColumns[17][count] - (worstCaseWithStorageColumns[10][count] + worstCaseWithStorageColumns[7][count] + worstCaseWithStorageColumns[6][count] + worstCaseWithStorageColumns[9][count] + worstCaseWithStorageColumns[8][count]))
        
        count = count + 1
    
    print(str(spotPurchases))
    fig = plt.figure(figsize=(8, 6), dpi=100)
    
    print("Wh Purchased DC + S: " + str(wh_purchased3))
    print("Num hours with purchase DC + S: " + str(wh_hours3))
    
    print(str(len(spotPurchases)) + " " + str(len(hoursInWeek)))
    
    plt.plot(hoursInWeek, spotPurchases, label="demand", color='black')
    plt.fill_between(hoursInWeek, spotPurchases, label="spot purchases", color='grey')
    plt.fill_between(hoursInWeek, other, label="other", color='white')
    plt.fill_between(hoursInWeek, gas, label="fracked gas", color='brown')
    plt.fill_between(hoursInWeek, wind, label="wind", color='blue')
    plt.fill_between(hoursInWeek, solar, label="solar", color='yellow')
    plt.fill_between(hoursInWeek, coal, label="coal", color='black')
    
    
    plt.title("TEP Dispatch Curve Week of July 5th 2024 With Datacenter with storage")
    plt.xlim(0, 167)
    plt.ylim(0, max(spotPurchases))
    
    plt.legend()

    plt.savefig('july-5-2024-datacenter-with-storage.png', dpi=100)
    #plt.show()
    plt.clf()
    
    
    coal = []
    gas = []
    solar = []
    wind = []
    other = []
    count = 0
    wh_purchased2 = 0
    wh_hours2 = 0
    for i in worstCaseColumns[2]:
        coal.append(worstCaseColumns[10][count])
        solar.append(worstCaseColumns[10][count] + worstCaseColumns[7][count])
        wind.append(worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count])
        gas.append(min(worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count] + worstCaseColumns[9][count], worstCaseColumns[2][count]))
        other.append(min(worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count] + worstCaseColumns[9][count] + worstCaseColumns[8][count], worstCaseColumns[2][count]))
        wh_hours2 = wh_hours2 + int(worstCaseColumns[2][count] > (worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count] + worstCaseColumns[9][count] + worstCaseColumns[8][count]))
        wh_purchased2 = wh_purchased2 + max(0, worstCaseColumns[2][count] - (worstCaseColumns[10][count] + worstCaseColumns[7][count] + worstCaseColumns[6][count] + worstCaseColumns[9][count] + worstCaseColumns[8][count]))
        count = count + 1
    
    print("Wh Purchased: " + str(wh_purchased2))
    print("Num hours with purchase: " + str(wh_hours2))
    
    print(str(float(wh_purchased1 / wh_purchased2)))
    
    #fig = plt.figure(figsize=(8, 6), dpi=100)
    
    plt.plot(hoursInWeek, worstCaseColumns[2], label="demand", color='black')
    plt.fill_between(hoursInWeek, worstCaseColumns[2], label="spot purchases", color='grey')
    plt.fill_between(hoursInWeek, other, label="other", color='white')
    plt.fill_between(hoursInWeek, gas, label="fracked gas", color='brown')
    plt.fill_between(hoursInWeek, wind, label="wind", color='blue')
    plt.fill_between(hoursInWeek, solar, label="solar", color='yellow')
    plt.fill_between(hoursInWeek, coal, label="coal", color='black')
    
    
    plt.title("TEP Dispatch Curve Week of July 5th 2024")
    plt.xlim(0, 167)
    plt.ylim(0, max(spotPurchases))
     
    plt.legend()

    plt.savefig('july-5-2024.png', dpi=100)
    #plt.show()
    
    
