#@ ImagePlus imp
#@ Integer(label="Peak tolerance",value=50) tolerance
#@ Integer(label="Window radius", value=7) window_radius
#@ Integer(label="Pixel size in nm", value=20) pixel_size_nm
#@ File(label="Select output directory", style="directory") out_dir
# author: Christoph Sommer, christoph.sommer@ist.ac.at

import os
import sys
import csv
import math
from ij import IJ
from ij.gui import PointRoi
from ij.gui import ProfilePlot
import java.awt.Color as Color
from ij.gui import Plot, Roi, Line
from ij.plugin.frame import RoiManager
from ij.plugin.filter import MaximumFinder
from ij.measure import ResultsTable, CurveFitter

# magic number sqrt(2)/2
MN = math.cos(math.pi/4)

# Plot gauss fit for peak_id == DEBUG, -1 for not
DEBUG = -1

# Curve fit for Gaussian
def fit_gauss(lroi, imp, p, peak_id, id_, type_, rm):
	lroi.setName("{}_{}_{}".format(str(id_), peak_id, type_))
	imp.setRoi(lroi)
	rm.addRoi(lroi)
	
	prof = ProfilePlot(imp)
	y = prof.getProfile()
	x = xrange(len(y))
	
	fitter = CurveFitter(x, y)
	fitter.doFit(CurveFitter.GAUSSIAN)
	param_values = fitter.getParams()
	std = param_values[3]
	fwhm = 2.3548 * std
	r2 = fitter.getFitGoodness()

	y_ = [fitter.f(x_) for x_ in x]
	
	area_profile = sum(y)  - len(y) *min(y)
	area_gauss   = sum(y_) - len(y_)*min(y_)
	
	output = {}
	output["x_pos"] = p.x
	output["y_pos"] = p.y
	output["fwhm"] = fwhm
	output["fwhm_nm"] = pixel_size_nm * fwhm
	output["r2_GoF"] = r2
	output["id"] = id_
	output["peak_id"] = peak_id
	output["type"] = type_
	# yai, excel maagic :-)
	output["avg_fwhm"] = '=AVERAGEIFS(F:F,B:B,B{},F:F,"<>"&"")'.format(id_+2)
	output["area_profile"] = area_profile
	output["area_gauss"] = area_gauss

	if peak_id == DEBUG:		
		plot = Plot("ROI peak {} type {}".format(peak_id, type_), "X (gray)", "Y (fit window)")
		plot.setLineWidth(2)
		plot.setColor(Color.RED)
		plot.addPoints(x, y, Plot.LINE)
		plot.setColor(Color.BLUE)
		plot.addPoints(x, y_, Plot.LINE)
		plot.show()
		
	return  output

def main(imp, tolerance, window_radius, pixel_size_nm, out_dir):
	# set output dir
	out_dir = str(out_dir)
	
	# Find maxima
	excludeOnEdge = True
	polygon = MaximumFinder().getMaxima(imp.getProcessor(), tolerance, excludeOnEdge)
	roi = PointRoi(polygon)

	# get RoiManager
	rm = RoiManager.getInstance();
	if rm is None:
	    rm = RoiManager()

	# Check if output table is writable
	out_table_fn = os.path.join(out_dir, "fwhm_values.txt")
	try:
		file_handle = open(out_table_fn, 'w')
	except IOError:
		IJ.showMessage("Output file '' not writeable. Check if file is open in Excel...")
		sys.exit(0)
				
	
	# iterate and write output
	with file_handle as csvfile:
		writer = csv.DictWriter(csvfile, 
		                        fieldnames=["id", "peak_id", "x_pos", "y_pos", 
		                                    "type", "fwhm", "fwhm_nm", "r2_GoF", 
		                                    "avg_fwhm", "area_profile", "area_gauss"], delimiter="\t", lineterminator='\n')
		writer.writeheader()
		id_ = 0
		# over all peaks
		for i, p in list(enumerate(roi)):
			IJ.showProgress(i, roi.getNCounters() +1)
			
			# Horizontal
			lroi = Line(p.x+0.5-window_radius, p.y+0.5, 
			            p.x+0.5+window_radius, p.y+0.5)
			output = fit_gauss(lroi, imp, p, i, id_, "H", rm)
			writer.writerow(output)
			id_+=1

			# Vertical
			lroi = Line(p.x+0.5, p.y+0.5-window_radius, 
			            p.x+0.5, p.y+0.5+window_radius)
			output = fit_gauss(lroi, imp, p, i, id_, "V", rm)
			writer.writerow(output)
			id_+=1

			# Diagonal 1
			lroi = Line(p.x+0.5-MN*window_radius, p.y+0.5+MN*window_radius, 
			            p.x+0.5+MN*window_radius, p.y+0.5-MN*window_radius)
			output = fit_gauss(lroi, imp, p, i, id_, "D1", rm)
			writer.writerow(output)
			id_+=1

			# Diagonal 2
			lroi = Line(p.x+0.5-MN*window_radius, p.y+0.5-MN*window_radius, 
			            p.x+0.5+MN*window_radius, p.y+0.5+MN*window_radius)
			output = fit_gauss(lroi, imp, p, i, id_, "D2", rm)
			writer.writerow(output)
			id_+=1
			
	IJ.showProgress(1)
	
	rm.runCommand("Deselect"); # deselect ROIs to save them all
	rm.runCommand("Save", os.path.join(out_dir, "fwhm_fiji_rois.zip"))
	
	IJ.showMessage("FWHM on Spots: Done")

if __name__ == "__builtin__":
	main(imp, tolerance, window_radius, pixel_size_nm, out_dir)



	
