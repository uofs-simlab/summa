#!/usr/bin/env python

# python largest_error_attrib.py [method_name] [stat]

import numpy as np
import xarray as xr
from pathlib import Path

top_fold    = '/home/avanb/scratch/'
attr_fold = '/home/avanb/TestScripts/settings/'
nBig = 10
do_rel = True # plot relative to the benchmark simulation

testing = False
if testing:
    top_fold = '/Users/amedin/Research/USask/test_py/'
    attr_fold = '/Users/amedin/Research/USask/test_py/settings/'
    method_name= 'be1'
    stat = 'rmnz'
else:
    import sys
    method_name = sys.argv[1]
    stat = sys.argv[2]

des_dir =  top_fold + 'statistics'
des_dir = Path(des_dir)

settings= ['scalarSWE','scalarTotalSoilWat','scalarTotalET','scalarCanopyWat','averageRoutedRunoff','wallClockTime']
viz_fil = method_name + '_hrly_diff_stats_{}.nc'
viz_fil = viz_fil.format(','.join(settings))
src_file =  des_dir / viz_fil
plot_vars = settings.copy()
short_name= ['SWE     ',
             'soilWat ',
             'ET      ',
             'canWat  ',
             'runoff  ']

attr_fil = Path(attr_fold) / 'attributes.nc'

# Open the netCDF file with RMSE data
summa = xr.open_dataset(src_file)
if stat == 'rmse' or stat == 'kgem': statr = 'mean_ben'
if stat == 'rmnz': statr = 'mnnz_ben'
if stat == 'maxe': statr = 'amax_ben'

for var in plot_vars:

    # Get the variable from the netCDF file
    stat0 = stat
    if var == 'wallClockTime': 
        if stat == 'rmse' or stat == 'kgem': stat0 = 'mean'
        if stat == 'rmnz': stat0 = 'mnnz'
        if stat == 'maxe': stat0 = 'amax'
    s = summa[var].sel(stat=stat0)
    if do_rel: 
        s_rel = summa[var].sel(stat=statr)
        if var != 'wallClockTime': s = s/s_rel

    # Mask the finite values of the variable
    mask = np.isfinite(s)
    s = s[mask]

    # Get the indices of the largest nBig values
    big_indices = abs(s).argsort()[-nBig:]
    
    # Get the largest nBig values
    val_big = s[big_indices.values]
    
    # Get the hru coordinate of the largest nBig values
    hru_big = s[big_indices.values].hru.values

    # Get the largest nBig bench values
    if do_rel: ben_big = s_rel.sel(hru=hru_big)
    
    # Print all the values of the biggest rmse hru
    if do_rel: 
        print(f"\n{var} raw error values of largest relative {stat} values:")
    else:
        print(f"\n{var} raw error values of largest {stat} values:")
    # Print all the raw values of the largest nBig values
    raw_vals = summa.sel(stat=stat0, hru=hru_big)
    for i,var0 in enumerate(plot_vars[:-1]):
        print(f"{short_name[i]}: [{' '.join(f'{val:8.1e}' for val in raw_vals[var0].values)}]")
    var0 = 'wallClockTime'
    if stat == 'rmse' or stat == 'kgem': stat00 = 'mean'
    if stat == 'rmnz': stat00 = 'mnnz'
    if stat == 'maxe': stat00 = 'amax'
    raw_vals = summa.sel(stat=stat00, hru=hru_big)
    print("wall"f"{stat00}: [{' '.join(f'{val:8.1e}' for val in raw_vals[var0].values)}]")

    # Open the netCDF file with local attributes
    attr = xr.open_dataset(attr_fil)

    # Mask the HRU variable from the netCDF file
    mask = attr['hruId'].isin(hru_big)

    # Get the vegTypeIndex, lat, lon variables from the netCDF file
    vegType_big = attr['vegTypeIndex'][mask]
    lat_big = attr['latitude'][mask]
    lon_big = attr['longitude'][mask]

    # Print the attributes of the largest nBig values
    print("HRU vals: [", " ".join([f"{val:8d}"  for val in hru_big]), "]", sep="")
    print("vegType : [", " ".join([f"{val:8d}"  for val in vegType_big.values]), "]", sep="")
    print("latitude: [", " ".join([f"{val:8.2f}"  for val in lat_big.values]), "]", sep="")
    print("longitud: [", " ".join([f"{val:8.2f}"  for val in lon_big.values]), "]", sep="")

    # Print the values of the largest nBig values, bench will be the mean, mnnz, or amax and err will be the rmse, rmnz, or maxe
    if do_rel: 
        #print(summa[var].sel(stat=stat0, hru=hru_big))
        print("Ben vals: [", " ".join([f"{val:8.1e}" for val in ben_big.values]), "]", sep="")
    print("Err vals: [", " ".join([f"{val:8.1e}" for val in val_big.values]), "]", sep="")
    