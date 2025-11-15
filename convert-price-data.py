#!/usr/bin/python3
import xlrd

# Parsing data downloaded from 
# https://www.oasis.oati.com/WALC/index.html 
# > Casio Day Ahead Market Energy Prices > 2024 

import datetime

def isDateValid(y, m, d):
    correctDate = None
    try:
        newDate = datetime.datetime(y,m,d)
        correctDate = True
    except ValueError:
        correctDate = False
    return correctDate

monthList = ['JAN24.xlsx'
    ,'FEB24.xlsx'
    ,'MAR24.xlsx'
    ,'APR24.xlsx'
    ,'May2024.xlsx'
    ,'JUN24.xlsx'
    ,'JUL24.xlsx'
    ,'Aug2024.xlsx'
    ,'Sept2024.xlsx'
    ,'OCT24.xlsx'
    ,'NOV24.xlsx'
    ,'DEC24.xlsx' 
]

month = 1
for filename in monthList:
    book = xlrd.open_workbook("OASIS/" + filename)
    sh = book.sheet_by_index(0)

    day = 0
    for rx in range(sh.nrows):
        hour = 0
        for ry in sh.row(rx):
            if str(ry).split(':')[0] == 'number' and isDateValid(2024, month, day):
                print(str(month) + ", " + str(day) + ", " + str(hour) + ", " + str(ry).split(':')[1])
                hour = hour + 1
        day = day + 1 
    month = month + 1
