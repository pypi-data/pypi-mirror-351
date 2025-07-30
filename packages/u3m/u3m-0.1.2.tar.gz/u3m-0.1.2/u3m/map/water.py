from ast import arg
import numpy as np
import cv2
from scipy.signal import convolve2d as conv2
import glob
from rs_tools import LightImage
import os
import argparse
from scipy import ndimage
from u3m.utils.utils import get_intersect_image, save_map
import tqdm
from osgeo import gdal
from skimage.transform import resize

def generate_water_map(fn, outdir, usfeet, target_epsg, target_resolution = 0.5, 
                       wdwsz_ = 9, sigma_ = 2, denom_ = 2, buffer = 50, bigwater_ = 5000,
                       onlybig = True, elevation = False, out_format='GTiff'):

    occ_list = sorted(glob.glob(os.path.join(outdir,'OCC','*.tif')))
    dsm_list = sorted(glob.glob(os.path.join(outdir,'DSM_LAST','*.tif')))
    water_list = glob.glob(os.path.join(outdir,'WATER_MAP','*.tif'))
    
    # for occ_fn,dsm_fn in tqdm.tqdm(zip(occ_list,dsm_list)):
        
    dsm_fn = fn        
    fid = '_'.join(os.path.basename(dsm_fn).split('_')[2:])[:-4]
    occ_fn = os.path.join(outdir,'OCC',f"OCCUPANCY_{fid}.tif")
    
    total_water_fn = os.path.join(outdir,'WATER_MAP',f"TOTAL_WATER_{fid}.tif")
    big_water_fn = os.path.join(outdir,'WATER_MAP',f'BIG_WATER_{fid}.tif')
    
    if total_water_fn in water_list or big_water_fn in water_list:
        return
    
    occ_ = LightImage(occ_fn)
    dsm_ = LightImage(dsm_fn)
    
    # occ,gt = occ_.get_box_all(buffer,-buffer,buffer,-buffer)
    # dsm,_ = dsm_.get_box_all(buffer,-buffer,buffer,-buffer)
    occ,gt = occ_.get_box_all(0,-1,0,-1)
    dsm,_ = dsm_.get_box_all(0,-1,0,-1)    
    
    occ = occ[0,:,:]
    dsm = dsm[0,:,:]
    
    DSM_resolution = target_resolution
    wdw_sz = wdwsz_
    sigma = sigma_
    denom = denom_
    # water_buffer = buffer_
    bigwater_threshold = bigwater_
    ## water mask
    w_points = occ == 1 # w_points = pixels where point exists
    point_density = np.sum(w_points)/np.shape(w_points)[0]/np.shape(w_points)[1]
    pr = point_density/denom
    criteria = int(wdw_sz*wdw_sz*pr - sigma*np.sqrt(wdw_sz*wdw_sz*pr*(1-pr)))
    # print("criteria:",criteria)
                        
    if target_epsg=='26916':
        criteria = 50
    if target_epsg=='26915':
        criteria = 30
        
    water = np.ones((w_points.shape[0]+wdw_sz-1,w_points.shape[1]+wdw_sz-1))
    water[int(wdw_sz/2):-int(wdw_sz/2),int(wdw_sz/2):-int(wdw_sz/2)] = w_points
    water = (conv2(water,np.ones((wdw_sz,wdw_sz),dtype=int),'same')< criteria).astype(int)
    water = water[int(wdw_sz/2):-int(wdw_sz/2),int(wdw_sz/2):-int(wdw_sz/2)]
    water = np.uint8(water)


    if elevation == False:

        number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(water, connectivity = 4)
        # print("shape of stats:",np.shape(stats))
        stats_T = np.transpose(stats)
        bbox_area = np.multiply(stats_T[2], stats_T[3])
        area_stat = stats_T[4]

        # large water for tree
        labels_meeting_criteria = np.where(area_stat >= bigwater_threshold/(DSM_resolution*DSM_resolution))[0][1:]

        mask_bigwater = np.isin(label_map, labels_meeting_criteria)

    total_water = np.zeros(np.shape(water))
    total_water[mask_bigwater==1]=1
    total_water[water==1]=1

    save_map(total_water_fn, total_water, occ_.ncol, occ_.nrow, target_epsg, gt, format=out_format)
    save_map(big_water_fn, mask_bigwater, occ_.ncol, occ_.nrow, target_epsg, gt, format=out_format)
    # save_map(f"{outdir}/WATER_MAP/WATER_{x1}_{y1}.tif", water, occ_.ncol, occ_.nrow, SRC, gt, format=out_format)


def refine_water_map(fn, outdir, usfeet, target_epsg, MINSIZE=1000, LEVEL=0.1, out_format='GTiff'):
    
    total_water_list = sorted(glob.glob(outdir + '/WATER_MAP/TOTAL_WATER_*.tif'))
    new_total_water_list = sorted(glob.glob(outdir + '/WATER_MAP/NEW_TOTAL_WATER_*.tif'))
    dsm_fn = os.path.join(outdir,'DSM_LAST/ALL_DSM_LAST.vrt')
    bldg_fn = os.path.join(outdir,'BUILDING_MAP/ALL_BUILDING_MAP_3D.vrt')
    
    # for total_water_fn in tqdm.tqdm(total_water_list):
        
    total_water_fn = fn
    print(total_water_fn)
    fid = '_'.join(os.path.basename(total_water_fn).split('_')[2:])[:-4]
    new_totalwater_fn = f"{outdir}/WATER_MAP/NEW_TOTAL_WATER_{fid}.tif"
    
    if new_totalwater_fn in new_total_water_list:
        return
    
    TW = LightImage(total_water_fn)
    DSML,totalwater = get_intersect_image(dsm_fn, total_water_fn)
    BLDG3D,_ = get_intersect_image(bldg_fn, total_water_fn)
    
    if DSML.shape != totalwater.shape:
        DSML = resize(DSML, totalwater.shape, order=0, mode='reflect', preserve_range=True)
    if BLDG3D.shape != totalwater.shape:
        BLDG3D = resize(BLDG3D, totalwater.shape, order=0, mode='reflect', preserve_range=True)
    
    # Refining Water 1
    #     ############################################################
    # among the water, if the segment overlap with tall & LARGE (>1000sqm)building, that water is highly likely not a water but an occlusion.
    
    # # midwater filter by size
    # Tall_Building_Buffer = np.uint8(Tall_Building_Buffer)
    
    # number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(Tall_Building_Buffer, connectivity = 4)
    # # print("shape of stats:",np.shape(stats))
    # stats_T = np.transpose(stats)
    # bbox_area = np.multiply(stats_T[2], stats_T[3])
    # area_stat = stats_T[4]

    # labels_meeting_criteria = np.where(area_stat >= 1000/(0.5*0.5))[0][1:]
    # Tall_Building_Buffer = np.isin(label_map, labels_meeting_criteria)
    # Tall_Building_Buffer = np.uint8(Tall_Building_Buffer)
    
    ############################################################
    # among the water, only for some mid-size(<5000sqm, >10sqm) segment, if the segment overlap with tall building, that water is highly likely not a water but an occlusion.
    
    # midwater filter by size
    midwater = np.uint8(totalwater)
    
    number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(midwater, connectivity = 4)
    # print("Refining water 1, Total water: shape of stats:",np.shape(stats))
    stats_T = np.transpose(stats)
    bbox_area = np.multiply(stats_T[2], stats_T[3])
    area_stat = stats_T[4]

    MIDSIZE_CRITERIA_1 = area_stat <= 5000/(0.5*0.5)
    MIDSIZE_CRITERIA_2 = area_stat >= 10/(0.5*0.5)
    MIDSIZE_CRITERIA = np.multiply(MIDSIZE_CRITERIA_1,MIDSIZE_CRITERIA_2)
    
    labels_meeting_criteria = np.where(MIDSIZE_CRITERIA)[0][1:]
    midwater = np.isin(label_map, labels_meeting_criteria)
    midwater = np.uint8(midwater)
    
    # for mid water, find the overlap segment
    # water segments overlapped with tall buildings should be excluded.
    
    contours, hierarchy = cv2.findContours(midwater, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    wrong_water = np.zeros(np.shape(midwater))

    # river/lake removal + water dem
    for c in contours:

        # access each segments
        segment_mask = np.zeros(np.shape(midwater))
        water_segment = cv2.drawContours(segment_mask, [c], -1, 1, -1)==1
        
        # if np.sum(np.multiply(Tall_Building_Buffer,water_segment))>0:
        #     wrong_water = wrong_water+water_segment
            
    # wrong_water mask
    totalwater[wrong_water==1]=0
    # totalwater[Tall_Building_Buffer==1]=0
        

    # Refining Water 2
    ############################################################
    # MID TALL BUILDING BOUNDARY CLEANING
    TALL_HEIGHT = 15
    Tall_Building = BLDG3D>=TALL_HEIGHT
    Tall_Building = np.uint8(Tall_Building)
    
    # if tall building size is smaller than 100sqm, than this should be a bird or error
    number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(Tall_Building, connectivity = 4)
    # print("Refining water 2, Tall Building (>15m): shape of stats:",np.shape(stats))
    stats_T = np.transpose(stats)
    bbox_area = np.multiply(stats_T[2], stats_T[3])
    area_stat = stats_T[4]
    
    MIDSIZE_CRITERIA = area_stat >= 100/(0.5*0.5)
    
    labels_meeting_criteria = np.where(MIDSIZE_CRITERIA)[0][1:]
    Tall_Building = np.isin(label_map, labels_meeting_criteria)
    Tall_Building = np.uint8(Tall_Building)
    
    
    Tall_Building_Buffer15 = ndimage.binary_dilation(Tall_Building, structure=np.ones((15,15)))

    Tall_Building_Buffer = Tall_Building_Buffer15
    totalwater[Tall_Building_Buffer==1]=0
    
    ############################################################

    
    
    # Refining Water 3
    ############################################################
    # Large water sometimes are not fully extracted due to the spectral variance (high point density area)
    # So, for large water bodies, water bodies are extended based one the assumption that
    # connected almost same elevation of DSM should be also water.
    
    
    # for only large water bodies (>5000)
    # large water bodies are extracted based on the cv2.connectedcomponets
    largewater = np.uint8(totalwater)
    
    # elevation will be allocated to only large water bodies (>500sqm)
    # boundaries of the water bodies might have some noise in its elevation, so we eroded
    largewater = ndimage.binary_erosion(largewater, structure=np.ones((5,5)))
    
#     # option 1:water segment의 elevation은 lidar point 값이 있는 것을 사용
#     DSML_OCCC = np.multiply(DSML,OCCC)
#     dsm_of_segment = DSML_OCCC[water_segment==1]

#     # option 2:water segment의 elevation은 interpolated 된 DSM의 값을 사용  ---> 이게 어떤 water는 아예 point가 없을수있으니까 나음.
#     dsm_of_segment = DSML[water_segment==1]
    
#     print("start, np.sum(totalwater):",np.sum(totalwater))
    LARGEWATER_AREA = []
    for i in range(2):
        
#         print("water refining iteration {}th".format(i))
        
        largewater = np.uint8(largewater)
        number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(largewater, connectivity = 4)
#         print("Refining water 3-1, total water: shape of stats:",np.shape(stats))
        stats_T = np.transpose(stats)
        bbox_area = np.multiply(stats_T[2], stats_T[3])
        area_stat = stats_T[4]

        LARGESIZE_CRITERIA = area_stat >= MINSIZE/(0.5*0.5)#100 default, NewOrleans 500

        labels_meeting_criteria = np.where(LARGESIZE_CRITERIA)[0][1:]
        largewater = np.isin(label_map, labels_meeting_criteria)
        largewater = np.uint8(largewater)

        # cv2.contour for large water bodies
        contours, hierarchy = cv2.findContours(largewater, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        connected_water = np.zeros(np.shape(largewater))
#         print("Refining Water 3-2, number of large water bodies:", len(contours))
        
        # largewater
        for c in contours:
            # access each segments
            segment_mask = np.zeros(np.shape(midwater))
            water_segment = cv2.drawContours(segment_mask, [c], -1, 1, -1)==1

            # water segment의 dem은 dsm중에서 -999가 아닌 것들을 모아서 median
            dsm_of_segment = DSML[water_segment==1]
            water_elevation = np.nanpercentile(dsm_of_segment, 10)
            #print("water_elevation:",water_elevation)
            upper_elevation = DSML<water_elevation+LEVEL
            lower_elevation = DSML>water_elevation-LEVEL

            DSM_sliced_by_elevation = np.multiply(lower_elevation, upper_elevation)
            DSM_sliced_by_elevation = np.uint8(DSM_sliced_by_elevation)

            # cv2.contour for large DSM_sliced_by_elevation
            number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(DSM_sliced_by_elevation, connectivity = 4)
            #print("DSM_sliced_by_elevation shape of stats:",np.shape(stats))
            stats_T = np.transpose(stats)
            bbox_area = np.multiply(stats_T[2], stats_T[3])
            area_stat = stats_T[4]

            LARGESIZE_CRITERIA = area_stat >= MINSIZE/(0.5*0.5)#100 default, NewOrleans 500

            labels_meeting_criteria = np.where(LARGESIZE_CRITERIA)[0][1:]
            DSM_sliced_by_elevation = np.isin(label_map, labels_meeting_criteria)
            DSM_sliced_by_elevation = np.uint8(DSM_sliced_by_elevation)


            # cv2.contour for water bodies
            contours_2, hierarchy_2 = cv2.findContours(DSM_sliced_by_elevation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #print("Refining Water 3, number of <large> DSM_sliced_by_elevation:", len(contours_2))
            for c_2 in contours_2:
                # access each segments
                segment_mask_2 = np.zeros(np.shape(DSM_sliced_by_elevation))
                water_segment_2 = cv2.drawContours(segment_mask_2, [c_2], -1, 1, -1)==1

                if np.sum(np.multiply(water_segment,water_segment_2))>0:
                    connected_water = connected_water+water_segment_2

        largewater = largewater+connected_water
        largewater = largewater>0

        LARGEWATER_AREA.append(np.sum(largewater))
        # print(LARGEWATER_AREA)
        if i>0 and (LARGEWATER_AREA[-1] == LARGEWATER_AREA[-2]):
            # print(LARGEWATER_AREA[-1],LARGEWATER_AREA[-2])
            break

    # wrong_water mask
    new_totalwater = totalwater + largewater
    new_totalwater = new_totalwater > 0
    
    save_map(new_totalwater_fn, new_totalwater, TW.ncol, TW.nrow,
                target_epsg, TW.geotransform, format=out_format, eType=gdal.GDT_Byte)


def get_args():
    
    argparser = argparse.ArgumentParser(description=__doc__)
    
    argparser.add_argument(
        '--fn',
        type=str,
        help='las filename')
    
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
    
    argparser.add_argument(
        '--base',
        action='store_true',
        default=False,
        help='base water map')
    
    argparser.add_argument(
        '--refine',
        action='store_true',
        default=False,
        help='refine water map')
    
    args = argparser.parse_args()
    return args


if __name__ == '__main__': 
    
    args = get_args()
    
    if args.base:
        generate_water_map(args.fn, args.outdir, args.usfeet, args.target_epsg)
        
    elif args.refine:
        refine_water_map(args.fn, args.outdir, args.usfeet, args.target_epsg)