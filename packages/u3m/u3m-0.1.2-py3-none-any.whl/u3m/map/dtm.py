import os
import numpy as np
from glob import glob
import cv2
from scipy.ndimage import median_filter, minimum_filter
from rs_tools import sobel_filter, interpolation, LightImage
import argparse
from u3m.utils.utils import save_map


def generate_dtm(tile_index, out_dir, usfeet, target_epsg, \
        LARGE_EXTENT, BUFFR_EXTENT, \
        slope_threshold, target_resolution=0.5, \
        bldg_is_rarely_bigger_than_this=50000, \
        dense_leaf=True, out_format = 'GTiff'):
    
    target_resolution = float(target_resolution)
    
    if usfeet:
        DSM_resolution = target_resolution*1/0.3048
    else:
        DSM_resolution = target_resolution
    
    CENTR_EXTENT_ROW = LARGE_EXTENT[0]-2*BUFFR_EXTENT[0]
    CENTR_EXTENT_COL = LARGE_EXTENT[1]-2*BUFFR_EXTENT[1]
    
    # print(CENTR_EXTENT)
    
    dsm_fn = os.path.join(out_dir,'DSM_LAST','ALL_DSM_LAST.vrt')
    dsm = LightImage(dsm_fn)
    # print("DSM vrt loaded")

    # Check data information
    # dsm_array = dsm.ReadAsArray() ## (3,6000,6000)
    
    """
    Following lines of code have been debugged from previous codes:
    
    nrow = dsm_array.shape[0]
    ncol = dsm_array.shape[1]
    
    to 
    """
    nrow = dsm.nrow - 2*BUFFR_EXTENT[0]
    ncol = dsm.ncol - 2*BUFFR_EXTENT[1]
    # print(nrow,ncol)
    
    gt = dsm.geotransform
    gt = [gt[0], gt[1], gt[2], gt[3], gt[4], gt[5]]
    # print(nrow,ncol)
    
    nrow = nrow//CENTR_EXTENT_ROW*CENTR_EXTENT_ROW
    ncol = ncol//CENTR_EXTENT_COL*CENTR_EXTENT_COL
    # print(nrow,ncol)
    
    ncol_out = ncol
    nrow_out = nrow
    
    XY_COMBS = []
    for x1 in np.arange(0,nrow,CENTR_EXTENT_ROW): 
        for y1 in np.arange(0,ncol,CENTR_EXTENT_COL):
            XY_COMB = []
            XY_COMB.append(x1)
            XY_COMB.append(y1)
            XY_COMBS.append(XY_COMB)
    print(f"DTM tiles: {len(XY_COMBS)}")
    # print(XY_COMBS)
    
    # get existing dtm_list
    dtm_list = glob(os.path.join(out_dir,'DTM_LAST','*_centered.tif'))
    
    
    # for XY in tqdm.tqdm(XY_COMBS, total=len(XY_COMBS)):
    XY = XY_COMBS[tile_index]            
    x1,y1 = int(XY[0]),int(XY[1])
    
    #
    dtm_fn = os.path.join(out_dir,'DTM_LAST',f'DTM_LAST_{x1}_{y1}_centered.tif')
    
    if dtm_fn in dtm_list:
        print(f"{dtm_fn} already exist")
        return           
    
    x2 = x1+LARGE_EXTENT[0]
    y2 = y1+LARGE_EXTENT[1]

    buffer_x = BUFFR_EXTENT[0]
    buffer_y = BUFFR_EXTENT[1]
    
    DSM,gt_box = dsm.get_box_all(y1,y2,x1,x2)
    DSM = DSM[0,:,:]
    
    # start_time = time.time()
    if dense_leaf:
        DSM_MED_5x5_1=minimum_filter(DSM,5)
    else:
        DSM_MED_5x5_1=median_filter(DSM,5)
    
    DSM_MED_5x5_2=median_filter(DSM_MED_5x5_1,5)
    DSM_MED_5x5_3=median_filter(DSM_MED_5x5_2,5)
    
    # end_time = time.time()
    # print("\nMedian filter took:", end_time-start_time)

    # sobel filter
    # start_time = time.time()
    sobel_threshold = np.tan(slope_threshold*np.pi/180)*4*DSM_resolution
    sobel_image = sobel_filter(DSM_MED_5x5_3)
    temp = sobel_image>=sobel_threshold
    # print("Sobel filter took:",time.time() - start_time)
    
    #
    temp1 = np.uint8(1-temp)
    temp1[:,0]=0
    temp1[0,:]=0
    temp1[-1,:]=0
    temp1[:,-1]=0
    
    #
    number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(temp1, connectivity = 4)
    stats_T = np.transpose(stats)
    bbox_area = np.multiply(stats_T[2], stats_T[3])
    area_stat = stats_T[4]
    
    #
    labels_meeting_criteria = np.where(area_stat >= bldg_is_rarely_bigger_than_this)[0][1:]
    if len(labels_meeting_criteria)==0:
        mask1 = np.ones(np.shape(label_map))
    else:
        mask1 = np.isin(label_map, labels_meeting_criteria)
    #
    img2 = DSM_MED_5x5_3
    img2[mask1==0]=np.nan
    #
    # start_time = time.time()
    dtm = interpolation(img2, interpolation_method='linear')
    # print("Interpolation took:",time.time() - start_time)
    if np.sum(np.isnan(dtm))>0:
        dtm = interpolation(dtm, interpolation_method='linear')

    # Refining
    # Create a mask for the refining conditions
    mask = (dtm > DSM) | (np.abs(dtm - DSM) < 0.1)

    # Update the DTM's pixels where the mask is True
    dtm[mask] = DSM[mask]
        
    #
    ncol_out = y2-y1
    nrow_out = x2-x1
    #
    gt_centered = [gt_box[0]+gt_box[1]*(buffer_y), gt_box[1], gt_box[2], gt_box[3]+gt_box[5]*(buffer_x), gt_box[4], gt_box[5]]
    ncol_out_centered = ncol_out-buffer_y*2
    nrow_out_centered = nrow_out-buffer_x*2    

    # Save output
    save_map(dtm_fn, dtm[buffer_x:-buffer_x,buffer_y:-buffer_y], ncol_out_centered, nrow_out_centered, target_epsg, gt_centered, format=out_format)
    # print(dtm_fn, "has saved")



def get_args():
    
    argparser = argparse.ArgumentParser(description=__doc__)
    
    argparser.add_argument(
        '--tile-index',
        type=int,
        help='tile index')
    
    argparser.add_argument(
        '--outdir',
        type=str,
        help='las filename')
      
    argparser.add_argument(
        '--usfeet',
        type=int,
        help='is usfeet')

    argparser.add_argument(
        '--target-epsg',
        type=int,
        help='epsg code')   

    argparser.add_argument(
        '--large-extent',
        nargs=2,
        type=int,
        metavar=('Extent row','Extent col'),
        help='output directory')  
    
    argparser.add_argument(
        '--buffer-extent',
        nargs=2,
        type=int,
        metavar=('Buffer row','Buffer col'),
        help='specify buffer extent')  
    
    argparser.add_argument(
        '--slope-threshold',
        type=float,
        default=45.0,
        help='slope threshold parameter')  
    
    args = argparser.parse_args()
    return args


if __name__ == '__main__': 
    
    args = get_args()
    
    generate_dtm(
        tile_index       = args.tile_index,
        out_dir          = args.outdir,
        usfeet           = args.usfeet,
        target_epsg      = args.target_epsg,
        LARGE_EXTENT     = args.large_extent,   # [nrow, ncol]
        BUFFR_EXTENT     = args.buffer_extent,  # [brow, bcol]
        slope_threshold  = args.slope_threshold
    )