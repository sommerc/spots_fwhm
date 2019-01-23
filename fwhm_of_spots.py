#@ ImagePlus imp
#@ Integer(label="Peak tolerance",value=50) tolerance
#@ Integer(label="Window radius", value=7) window_radius
#@ Integer(label="Pixel size in nm", value=20) pixel_size_nm
#@ File(label="Select output directory", style="directory") out_dir
# author: Christoph Sommer, christoph.sommer@ist.ac.at

import os
import sys
import csv
from ij import IJ
from ij.gui import PointRoi
from ij.gui import ProfilePlot
import java.awt.Color as Color
from ij.gui import Plot, Roi, Line
from ij.plugin.frame import RoiManager
from ij.plugin.filter import MaximumFinder
from ij.measure import ResultsTable, CurveFitter

# set output dir
out_dir = str(out_dir)

# Find maxima
excludeOnEdge = True
polygon = MaximumFinder().getMaxima(imp.getProcessor(), tolerance, excludeOnEdge)
roi = PointRoi(polygon)

rm = RoiManager.getInstance();
if (rm is None):
    rm = RoiManager()

# Curve fit for Gaussian
def fit_gauss():
	y = prof.getProfile()
	x = xrange(len(y))
	fitter = CurveFitter(x, y)
	fitter.doFit(CurveFitter.GAUSSIAN)
	param_values = fitter.getParams()
	std = param_values[3]
	fwhm = 2.3548 * std
	r2 = fitter.getFitGoodness()

	return  fwhm, r2

# iterate and write output
with open(os.path.join(out_dir, "fwhm_values.txt"), 'w') as csvfile:
	writer = csv.DictWriter(csvfile, 
	                        fieldnames=["id", "x_pos", "y_pos", "type", "fwhm", "fwhm_nm", "r2"], delimiter="\t", lineterminator='\n')
	writer.writeheader()
	for i, p in list(enumerate(roi)):
		IJ.showProgress(i, roi.getNCounters() +1)
		# Horizontal
		id_ = i * 2
		output = {}
		lh = Line(p.x+0.5-window_radius, p.y+0.5, p.x+0.5+window_radius, p.y+0.5)
		lh.setName(str(id_))
		rm.addRoi(lh)
		imp.setRoi(lh)
		prof = ProfilePlot(imp)
		fwhm_h, r2_h = fit_gauss()
		output["id"] = id_
		output["x_pos"] = p.x
		output["y_pos"] = p.y
		output["type"] = "H"
		output["fwhm"] = fwhm_h
		output["fwhm_nm"] = pixel_size_nm * output["fwhm"]
		output["r2"] = r2_h
	
		writer.writerow(output)
		
		# Vertical
		id_ = i * 2 + 1
		lv = Line(p.x+0.5, p.y+0.5-window_radius, p.x+0.5, p.y+0.5+window_radius)
		lv.setName(str(id_))
		imp.setRoi(lv)
		rm.addRoi(lv)
		prof = ProfilePlot(imp)
		fwhm_v, r2_v = fit_gauss()
		output["id"] = id_
		output["type"] = "V"
		output["fwhm"] = fwhm_v
		output["fwhm_nm"] = pixel_size_nm * output["fwhm"]
		output["r2"] = r2_v
	
		writer.writerow(output)
IJ.showProgress(1)

rm.runCommand("Deselect"); # deselect ROIs to save them all
rm.runCommand("Save", os.path.join(out_dir, "fwhm_fiji_rois.zip"))

IJ.showMessage("FWHM on Spots: Done")




	
