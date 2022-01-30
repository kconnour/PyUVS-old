import statsmodels.api as sm

# GET the very very important info from fits file
# Rebin the spectrum according to spectral bin width
# Load the wavelength centers for the file's spectral binning
# Calculate the spectral range of the file (spectral_pizel_start/ spectral-bin_width gets starting index)
# Make empty array of NaNs of len(n_wavelengths). Then place observed spectrum in this array starting at index from line 6. Also include uncertainty dim
# Compute calibratoin curve from loaded wavelength centers for this spectral binning
# Do WLS
# Multiply the appropriate template by the coefficients, calibrate, then integrate (wich gives result in kR)
# Loop through integrations and spatial bin to do the fit


# spectrum uncertainty is the random DN uncertainty
# Loop through integrations and spatial bin to do the fit
# (future) Zac says I can speed this up if I get a 1kR template
# Add in saturation threshhold
# aurora  = CO Cameron + UVD only
