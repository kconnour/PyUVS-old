from astropy.io import fits

f = '/media/kyle/Samsung_T5/IUVS_data/orbit07200/mvn_iuv_l1b_apoapse-orbit07210-muv_20180613T134305_v13_r01.fits.gz'
hdul = fits.open(f)
print(hdul['spacecraftgeometry'].data['sub_solar_lon'].shape)
print(hdul['primary'].data.shape)
