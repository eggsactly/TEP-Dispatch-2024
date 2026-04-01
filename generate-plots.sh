#!/bin/bash 

./calculate-hourly-costs.py -o -1 # Baseline 2024 
./calculate-hourly-costs.py -o 0 # Data center with no intervention
./calculate-hourly-costs.py -o 1 # Data center with demand side management
./calculate-hourly-costs.py -o 2 # Data center with battery instead of demand side management
./calculate-hourly-costs.py -o 3 # Data center with nearly full renewable
./calculate-hourly-costs.py -o 4 # Full build of data center with no intervention 

