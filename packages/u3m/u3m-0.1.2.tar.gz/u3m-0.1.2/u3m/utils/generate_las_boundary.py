#!/usr/bin/env python

import laspy
import sys
import os
import glob
from osgeo import ogr, osr
import tqdm
import argparse
import math
from u3m.utils.utils import get_spatial_reference_from_las

# Check input argument
parser = argparse.ArgumentParser()
parser.add_argument("in_dir", help="Input directory for LiDAR data")
parser.add_argument("out_dir", help="Output file name")
args = parser.parse_args()

# Get input file directory
las_list = glob.glob(os.path.join(args.in_dir, "laz/*.las"))

# Coordinate system
_,src = get_spatial_reference_from_las(os.path.join(args.in_dir, "laz"))
assert src, "Spatial reference is not defined"

sproj = osr.SpatialReference()
sproj.ImportFromWkt(src)

## Create a shape file
driver = ogr.GetDriverByName('ESRI Shapefile')

# Delete file if already exists
base_name = os.path.basename(args.in_dir)
print(base_name)
out_fn = args.out_dir + f"/{base_name}.shp"
if os.path.exists(out_fn):
    # driver.DeleteDataSource(out_fn)
    print(f"{out_fn} already exists")
    sys.exit(1)

ds = driver.CreateDataSource(out_fn)

# Layer
layer = ds.CreateLayer('tile_boundary', srs=sproj, geom_type=ogr.wkbPolygon)

# Fields
fn_defn = ogr.FieldDefn('fn', ogr.OFTString)
layer.CreateField(fn_defn)

# Open the first file to get spatial reference information
for fn in tqdm.tqdm(las_list):
  f = laspy.open(fn)
  
  # Get min max
  xmin = f.header.mins[0]
  xmax = f.header.maxs[0]
  ymin = f.header.mins[1]
  ymax = f.header.maxs[1]
  
  # Need to round off numbers for the boundary coordinates.
  xmin_int = math.floor(xmin)
  xmax_int = math.ceil(xmax)
  ymin_int = math.floor(ymin)
  ymax_int = math.ceil(ymax)
  
  # Generate polygon
  outring = ogr.Geometry(ogr.wkbLinearRing)
  outring.AddPoint(xmin_int, ymin_int)
  outring.AddPoint(xmin_int, ymax_int)
  outring.AddPoint(xmax_int, ymax_int)
  outring.AddPoint(xmax_int, ymin_int)
  outring.AddPoint(xmin_int, ymin_int)

  tile = ogr.Geometry(ogr.wkbPolygon)
  tile.AddGeometry(outring)

  featureDefn = layer.GetLayerDefn()
  feature = ogr.Feature(featureDefn)
  feature.SetGeometry(tile)
  feature.SetField('fn', os.path.basename(fn))
  
  layer.CreateFeature(feature)

  tile.Destroy()
  feature.Destroy()
  
# Now close shapefile
ds.Destroy()