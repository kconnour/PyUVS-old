from scipy.io import netcdf
f = netcdf.netcdf_file('/media/kyle/Samsung_T5/diagfi_MY34_Ls180_210_LT_A.nc', 'r')
print(f.variables)
