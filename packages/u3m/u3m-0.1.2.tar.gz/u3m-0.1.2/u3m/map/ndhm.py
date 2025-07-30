import os, glob
import numpy as np
from osgeo import gdal
from u3m.utils.utils import get_intersect_image, save_map
import argparse
import tqdm

def generate_ndhm(fn, out_dir, usfeet, target_epsg, out_format = 'GTiff'):
    
    # open dsm
    dsmf_fn = os.path.join(out_dir,'DSM_FRST','ALL_DSM_FRST.vrt')
    dsml_fn = os.path.join(out_dir,'DSM_LAST','ALL_DSM_LAST.vrt')
    
    # get dtm file list
    dtm_list = sorted(glob.glob(os.path.join(out_dir,'DTM_LAST','*_centered.tif')))
    ndhm_first_list = glob.glob(os.path.join(out_dir,'NDHM_FRST','NDHM_FRST_*.tif'))
    ndhm_last_list = glob.glob(os.path.join(out_dir,'NDHM_LAST','NDHM_LAST_*.tif'))
     
    # for dtm_fn in tqdm.tqdm(dtm_list, total=len(dtm_list)):
      
    dtm_fn = fn
    # get file name
    fid = os.path.basename(dtm_fn).split('_')
    x1, y1 = fid[2], fid[3]
    
    # check existence
    ndhm_first_fn = os.path.join(out_dir,'NDHM_FRST',f"NDHM_FRST_{x1}_{y1}.tif")
    ndhm_last_fn = os.path.join(out_dir,'NDHM_LAST',f"NDHM_LAST_{x1}_{y1}.tif")
    
    if ndhm_first_fn in ndhm_first_list or ndhm_last_fn in ndhm_last_list:
        return
    
    dtm = gdal.Open(dtm_fn)
    gt = dtm.GetGeoTransform()
    DTMC, DSMF = get_intersect_image(dtm_fn, dsmf_fn)
    _, DSML = get_intersect_image(dtm_fn, dsml_fn)
    nrow, ncol = np.shape(DTMC)

    # create ndhm
    NDHM_F = DSMF - DTMC
    NDHM_F[NDHM_F<0]=0
    
    NDHM_L = DSML - DTMC
    NDHM_L[NDHM_L<0]=0
    
    # save NDHM first return
    save_map(ndhm_first_fn, NDHM_F, ncol, nrow, target_epsg, gt, format=out_format)           
    save_map(ndhm_last_fn, NDHM_L, ncol, nrow, target_epsg, gt, format=out_format)


def get_args():
    
    argparser = argparse.ArgumentParser(description=__doc__)
    
    argparser.add_argument(
        '--fn',
        type=str,
        help='dtm filename')
    
    argparser.add_argument(
        '--outdir',
        type=str,
        help='output directory')  
      
    argparser.add_argument(
        '--usfeet',
        type=int,
        help='is usfeet')

    argparser.add_argument(
        '--target-epsg',
        type=str,
        help='spatial reference coordinate')   
    
    args = argparser.parse_args()
    return args


if __name__ == '__main__': 
    
    args = get_args()
    generate_ndhm(args.fn, args.outdir, args.usfeet, args.target_epsg)