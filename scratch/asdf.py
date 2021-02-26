from astropy.io import fits


hdul = fits.open('/media/kyle/Samsung_T5/IUVS_data/orbit07200/mvn_iuv_l1b_apoapse-orbit07287-muv_20180627T205457_v13_r01.fits.gz')
print(hdul['observation'].data.columns)
#print(hdul['observation'].data['solar_longitude'])
