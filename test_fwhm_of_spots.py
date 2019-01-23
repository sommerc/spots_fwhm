import os
import sys

__file__ = globals()['javax.script.filename']
macro_path = os.path.dirname(__file__)

sys.path.append(macro_path)
from fwhm_of_spots import main

from ij import IJ
test_imp = IJ.openImage(os.path.join(macro_path, "test", "test_img.tif"))

main(test_imp, 50,7,20, os.path.join(macro_path, "test"))