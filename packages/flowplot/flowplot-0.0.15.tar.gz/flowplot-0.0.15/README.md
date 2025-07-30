<p align="center">
  <img src="https://github.com/user-attachments/assets/95150a22-f7bf-4b69-b387-e2f6c19e93af" width=70% height=70%>
</p>

# Quickstart
`pip install flowplot`

```python
from flowplot import cycle
cycle(r".\user-inputs\cycles\Overall.csv", delimiter=';')
```
<p align="center">
<img src="https://github.com/user-attachments/assets/7fcdd855-611f-4cb7-82df-bc82baaf2865" width=50% height=50%>
</p>

# Overview

flowplot is a visualisation and analysis tool for hydrological and general flow-stock, input-output-storage data for Python 🐳

Diagrams include 
- **Cycle**, including *Circles*, *Bar graphs*, and *Line graphs*
- **TSCompare** Time series of multiple simulations and observations, with statistics
- **ExceedanceProb** Exceedance probability and comparison, multiple simulations
- **BoxWhisker** Box-whisker plots, multiple simulations
- **HeatSeason** Seasonality, multiple simulations


![flowplot_portfolio](https://github.com/user-attachments/assets/2170632f-acbf-4d21-8303-73dd0d372fed)

# User inputs
### user-inputs folder includes: 
#### cycles: 
- associates the cycle flows as in, out, storage, and sub-flows
  
#### flow time series:
- Contains three columns for the date: YYYY, MM,  DD
- Column names match those indicated in the cycles csv above
- There can be several csv files holding flow time series
- Columns hold daily values of flows, with name and unit indicated in cycle csv

### Units
- standard
  - m3   (meaning m3/day)
  - m3s  
(meaning m3/second)
- with option num_cells_domain:
  - mmcell (meaning mm/day/averaged across all cells)
  - m3cell (meaning m3/day averaged across all cells)
 

  - m3scell (meaning m3/second averaged across all cells)
- with option cellsize_m2, assuming all cells are the same size in square metres
  - mm     (meaning mm/day)
```
cycle(r".\user-inputs\cycles\Overall.csv", delimiter=';', cellsize_m2=1000*1000, num_cells_domain=153451)
```
### Creates the following diagrams for a user-determined cycle:
  1. **Circles**, showing the partitioned inputs, outputs, net storage changes, and balance, aggregated spatiotemporally;
  2. **Bar graphs**, showing the partitioned inputs, outputs, net storage changes, and balance, aggregated spatiotemporal;
  3. **Line graphs, overall**, showing the inputs, outputs, net storage changes, and balance through time, aggregated spatially;
  4. **Line graphs, partitioned**, showing the partitioned flows through time, aggregated spatially.
![flowplot](https://github.com/user-attachments/assets/defcf9c5-6750-4270-b0a6-a74806361582)
