# fwhm_on_spots
## Full-width-half-maximum of 2D spots
This jython-fiji macro computes the FWHM on bright spots on dark background by
1) finding all maxima in an image (using fiji `find maxima`) and 2) iterating 
over all 2d peak location. For each peak the horizontal and vertical line intensity 
profile is extracted and a general Gaussian function is fit. From that the standard
deviation and goodness-of-fit is extracted. The standard deviation is converted 
to FWHM.

Peak locations, FWHM and goodness-of-fit are exported to an tab-delimited, excel
readable file. In additions, all (fiji-)Rois of the according line profile are 
exported into a fiji RoiManager zip-file.

### Input
1. Image: An gray-valued image (already open in fiji)
2. Peak tolerance: Height of the peak above background (see fiji `find maxima`)
3. Window radius for Gaussian fit in pixel
4. Pixel size in nano-meters (for export)
5. Output directory (for export)

### Output
1. `fwhm_values.txt`: Peak locations, FWHM in pixel and nano-meter, plus goodness-of-fit
2. `fwhm_fiji_rois.zip`: Rois with horizontal and vertical line profiles




