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
        if float(row[11]) > largest:
            largest = float(row[11])
            indexOfLargest = count
            date = row[1]
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
    return month, day, year, isPm, timeInt, timeOffsetd

dispatch = []

with open('TEP-Dispatch-2024.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        dispatch.append(row)
    
    
    # Find each 168th index section, add up all the weeks
    count = 0
    firstIteration = True
    weeks = 0
    averageWeekList = []
    hoursInWeek = 168
    xAxis = []
    for row in dispatch[1:]:
        if firstIteration:
            averageWeekList.append({'demand': float(row[2]), 'wind': float(row[6]), 'solar': float(row[7]), 'other': float(row[8]), 'gas': float(row[9]), 'coal': float(row[10]), 'weeks': 1})
            xAxis.append(count)
        else:
            try:
                averageWeekList[count]['demand'] = averageWeekList[count]['demand'] + float(row[2])
                averageWeekList[count]['wind'] = averageWeekList[count]['wind'] + float(row[6])
                averageWeekList[count]['solar'] = averageWeekList[count]['solar'] + float(row[7])
                averageWeekList[count]['other'] = averageWeekList[count]['other'] + float(row[8])
                averageWeekList[count]['gas'] = averageWeekList[count]['gas'] + float(row[9])
                averageWeekList[count]['coal'] = averageWeekList[count]['coal'] + float(row[10])
                averageWeekList[count]['weeks'] = averageWeekList[count]['weeks'] + 1
            except ValueError as e:
                print("Warning: Missing data on hour " + str(count))
                yolo = 0
        
        if count > hoursInWeek-2:
            
            count = 0
            firstIteration = False
        else:
            count = count + 1
    
    # For each day of our average week, divide by the number of days
    for row in averageWeekList:
        row['demand'] = row['demand'] / row['weeks']
        row['wind'] = row['wind'] / row['weeks']
        row['solar'] = row['solar'] / row['weeks']
        row['other'] = row['other'] / row['weeks']
        row['gas'] = row['gas'] / row['weeks']
        row['coal'] = row['coal'] / row['weeks']
    
    # Sort this list 
    averageWeekListSorted = sorted(averageWeekList, key=lambda d: d['demand'], reverse=True)
    
    # Turn the array of dictionaries, into a dictionary of arrays
    averageWeekDict = {'demand': [], 'wind': [], 'solar': [], 'other': [], 'gas': [], 'coal': []}
    averageWeekDictStacked = {'demand': [], 'wind': [], 'solar': [], 'other': [], 'gas': [], 'coal': []}
    for row in averageWeekListSorted:
        averageWeekDict['demand'].append(row['demand'])
        averageWeekDict['wind'].append(row['wind'])
        averageWeekDict['solar'].append(row['solar'])
        averageWeekDict['other'].append(row['other'])
        averageWeekDict['gas'].append(row['gas'])
        averageWeekDict['coal'].append(row['coal'])
        
        averageWeekDictStacked['demand'].append(row['demand'])
        averageWeekDictStacked['coal'].append(min(row['demand'], row['coal']))
        averageWeekDictStacked['solar'].append(min(row['demand'], row['solar'] + row['coal']))
        averageWeekDictStacked['wind'].append(min(row['demand'], row['wind'] + row['solar'] + row['coal']))
        averageWeekDictStacked['gas'].append(min(row['demand'], row['gas'] + row['wind'] + row['solar'] + row['coal']))
        averageWeekDictStacked['other'].append(min(row['demand'], row['other'] + row['gas'] + row['wind'] + row['solar'] + row['coal']))
    
    if len(xAxis) != 168:
        print("Error: X Axis is not size 168, it is: " + str(len(xAxis)))
        sys.exit(1)
    
    fig = plt.figure(figsize=(10, 8), dpi=100)
    
    plt.plot(xAxis, averageWeekDictStacked['demand'], label="demand", color='black')
    plt.fill_between(xAxis, averageWeekDictStacked['demand'], label="energy imports", color='grey')
    plt.fill_between(xAxis, averageWeekDictStacked['other'], label="other", color='white')
    plt.fill_between(xAxis, averageWeekDictStacked['gas'], label="fracked gas", color='brown')
    plt.fill_between(xAxis, averageWeekDictStacked['wind'], label="wind", color='blue')
    plt.fill_between(xAxis, averageWeekDictStacked['solar'], label="solar", color='yellow')
    plt.fill_between(xAxis, averageWeekDictStacked['coal'], label="coal", color='black')
    
    
    plt.title("TEP Dispatch Curve Average of 2024")
    plt.xlim(0, 167)
    plt.ylim(0, max(averageWeekDictStacked['demand']))
    plt.xlabel("Hour of Week (sorted)")  # Set x-axis label
    plt.ylabel("Energy Demand (MWh)")  # Set x-axis label

    
    plt.legend()

    plt.savefig('Ave-2024.png', dpi=100)
    #plt.show()
    plt.clf()
    
    
    
