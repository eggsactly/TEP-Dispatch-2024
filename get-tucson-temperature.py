#!/usr/bin/python3

import urllib.request
import calendar
from datetime import date
import sys

year = 2023

# iterate through every months

#for m in range(

# Read from this page:
# http://www.atmo.arizona.edu/products/wxstn/

# Loop through months
for month in range(1, 13):
    # Loop through days
    _, daysInMonth = calendar.monthrange(year, month)
    for day in range (1, daysInMonth + 1):
        url = "http://www.atmo.arizona.edu/products/wxstn/" + "{:04d}".format(year) + "{:02d}".format(month) + "{:02d}".format(day) + "wxdata.txt"
        # Give the user updates
        print("info: " + url, file=sys.stderr)
    
        contents = urllib.request.urlopen(url).read()

        lines = contents.decode('utf-8').splitlines()
        lastHour = -1

        tempRecord = []
        # Loop through hours 
        for line in lines:
            splitline = line.split(" ")
            # Filter out empty lines 
            splitline = list(filter(None, map(str.strip, splitline)))
            
            timeArray = str(splitline[1]).split(':')
            hour = int(timeArray[0])
            temperature = float(str(splitline[4]))
            if hour > lastHour:
                lastHour = hour
                tempRecord.append({'date': str(splitline[0]), 'time': str(splitline[1]), 'temp': temperature})

        # Print the hours 
        for record in tempRecord:
            print(record['date'] + ', ' + record['time'] + ', ' + str(record['temp']))

    






