# About
This repository shows Tucson/TEP energy demand changes as a result of the Project Blue data center Energy Service Agreement (ESA), Arizona Corporation Commission (ACC) docket [E-01933A-25-0187](https://edocket.azcc.gov/search/docket-search/item-detail/29640). This repository uses 2024 as a test year for assessing the impact of the data center on consumer rate increases. 

Running: 
`$ ./plot-2024-ave.py` will produce the following plots. 

![Average 2024 Dispatch Curve](https://i.imgur.com/G5P9OLS.png)
Plots the average 2024 dispatch curve to Tucson and the sources of generation throughout the year. 

![Average 2024 Dispatch Curve with Data Center](https://i.imgur.com/vbukCeO.png)
Plots the average 2024 dispatch curve to Tucson and the sources of generation throughout the year with a 200 MWh average load added to the dispatch modeling the data center. The area in pink is the amount of energy generated per week that TEP will likely generate with fracked gas generation. This would mean roughly 859 kilotons of CO2e emissions from the electricity generation. 


