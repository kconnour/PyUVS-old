from astropy.io import fits

# Open apoapse MUV file
hdulist = fits.open('/Volumes/Samsung_T5/IUVS_data/orbit03400/mvn_iuv_l1b_apoapse-orbit03453-muv_20160708T051356_v13_r01.fits.gz')
hdulist.info()
print('~'*20)

# Open apoapse FUV file
hdulist = fits.open('/Volumes/Samsung_T5/IUVS_data/orbit03400/mvn_iuv_l1b_apoapse-orbit03453-fuv_20160708T051356_v13_r01.fits.gz')
hdulist.info()
print('~'*20)

# Open periapse MUV File
hdulist = fits.open('/Volumes/Samsung_T5/IUVS_data/orbit03400/mvn_iuv_l1b_periapse-orbit03499-muv_20160716T141400_v13_r01.fits.gz')
hdulist.info()
print('~'*20)

# Open periapse FUV file
hdulist = fits.open('/Volumes/Samsung_T5/IUVS_data/orbit03400/mvn_iuv_l1b_periapse-orbit03499-fuv_20160716T141400_v13_r01.fits.gz')
hdulist.info()
print('~'*20)

# Open inlimb MUV file
hdulist = fits.open('/Volumes/Samsung_T5/IUVS_data/orbit03400/mvn_iuv_l1b_inlimb-orbit03486-muv_20160714T082823_v13_r01.fits.gz')
hdulist.info()
print('~'*20)

# Open inlimb FUV file
hdulist = fits.open('/Volumes/Samsung_T5/IUVS_data/orbit03400/mvn_iuv_l1b_inlimb-orbit03486-fuv_20160714T082823_v13_r01.fits.gz')
hdulist.info()
print('~'*20)
