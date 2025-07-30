import numpy as np
import cv2
from skimage.util import view_as_windows as viewW
from scipy import ndimage
import glob
from rs_tools import LightImage
from u3m.utils.utils import define_kernel, save_map, get_intersect_image
import os
import argparse
import tqdm
from skimage.transform import resize


def sliding_uniq_count(a, BSZ):
    out_shp = np.asarray(a.shape) - BSZ + 1
    a_slid4D = viewW(a,BSZ)
    a_slid2D = np.sort(a_slid4D.reshape(-1,np.prod(BSZ)),axis=1)    
    return ((a_slid2D[:,1:] != a_slid2D[:,:-1]).sum(1)+1).reshape(out_shp)



def generate_bldg_map(dsm_fn, outdir, usfeet, target_epsg, kernel_size=5, target_resolution = 0.5, height_threshold=1.5, 
                                s1=4, s2=0.1, bldg_size = 25, roughness_threshold = 25,
                                PLANARITY_WATERELEVATION_TILESZ = 2000, out_format='GTiff'):

    ndhm_frst_fn = os.path.join(outdir,'NDHM_FRST','ALL_NDHM_FRST.vrt')
    ndhm_last_fn = os.path.join(outdir,'NDHM_LAST','ALL_NDHM_LAST.vrt')
    water_list = sorted(glob.glob(os.path.join(outdir,'WATER_MAP','BIG_WATER_*.tif')))
    bldg_3d_list = glob.glob(os.path.join(outdir,'BUILDING_MAP','BUILDING_MAP_3D_*.tif'))
    rough_list = glob.glob(os.path.join(outdir,'BUILDING_MAP','ROUGHNESS_MAP_*.tif'))

    # for water_fn in tqdm.tqdm(water_list):

    fid = '_'.join(os.path.basename(dsm_fn).split('_')[2:])[:-4]
    water_fn = os.path.join(outdir,'WATER_MAP',f"BIG_WATER_{fid}.tif")
    # load water map metadata
    water_ = LightImage(water_fn)
    
    # get fid
    fid = '_'.join(os.path.basename(water_fn).split('_')[2:])[:-4]
    
    # set building map file name
    # bldg_map_fn = f"{outdir}/BUILDING_MAP/BUILDING_MAP_{fid}.tif"
    bldg_3d_map_fn = os.path.join(outdir,'BUILDING_MAP',f"BUILDING_MAP_3D_{fid}.tif")
    roughness_map_fn = os.path.join(outdir,'BUILDING_MAP',f"ROUGHNESS_MAP_{fid}.tif")
    
    # if bldg map already exists
    if bldg_3d_map_fn in bldg_3d_list or roughness_map_fn in rough_list:
        print(f"Building map {bldg_3d_map_fn} or roughness map {roughness_map_fn} already exists. Skipping.")
        return
    
    # get intersection
    water, ndhm_frst, extent = get_intersect_image(water_fn, ndhm_frst_fn, extent=True)
    _, ndhm = get_intersect_image(water_fn, ndhm_last_fn)
    
    # print(water,ndhm_frst,extent)
    # if no intersection
    if water is None:
        print(f"No intersection between {water_fn} and {ndhm_frst_fn} or {ndhm_last_fn}. Skipping.")
        return

    if water.shape != ndhm.shape:
        ndhm = resize(ndhm, water.shape, order=0, mode='reflect', preserve_range=True)
        
    if water.shape != ndhm_frst.shape:
        ndhm_frst = resize(ndhm_frst, water.shape, order=0, mode='reflect', preserve_range=True)
    
    gt = water_.geotransform
    gt = (extent[0], gt[1], gt[2], extent[1], gt[4], gt[5])
      
    # define kernel
    kernel = define_kernel(kernel_size)

    # define parameters
    S1 = s1
    S2 = s2
    building_is_larger_than_this = bldg_size
    DSM_resolution = target_resolution
    ksz = 5
    
    # roughness map
    roughness_map = np.zeros(np.shape(ndhm))

    # planarity map
    planarity_map = np.zeros(np.shape(ndhm))

    # roughness map : No. of unique values within WDW*WDW window
    r = int(np.floor(ksz/2))

    padded_ndhm = np.zeros((np.shape(ndhm)[0]+2*r,np.shape(ndhm)[1]+2*r))
    padded_ndhm[r:-r,r:-r] = ndhm
    ########## Make ndhm INTEGER in meter unit
    padded_ndhm = np.uint8(padded_ndhm) 

    roughness_map = sliding_uniq_count(padded_ndhm, [ksz,ksz])
    
    smooth_area = roughness_map<=roughness_threshold
    temp=ndhm>height_threshold
    temp = np.multiply(temp, smooth_area)
    temp2=temp!=0

    before_erosion = temp2 # just for visualization/evaluatio
    temp3=ndimage.binary_erosion(temp2, structure=kernel)
    before_dilation = temp3 # just for visualization/evaluation
    temp3=ndimage.binary_dilation(temp3, structure=kernel)
    building_candidate = temp3 # just for visualization/evaluation

    # water remove from the candidate
    temp3[water ==1]=0
    temp3 = np.uint8(temp3)

    CONNECTIVITY = 4
    number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(temp3, connectivity = CONNECTIVITY)

    stats_T = np.transpose(stats)
#     bbox_area = np.multiply(stats_T[2], stats_T[3])
    area_stat = stats_T[4]


    labels_meeting_criteria = np.where(area_stat >= building_is_larger_than_this/(DSM_resolution*DSM_resolution))[0][1:]

    temp3 = np.isin(label_map, labels_meeting_criteria)
    temp3 = np.uint8(temp3)

    tile_sz = PLANARITY_WATERELEVATION_TILESZ

    INPUT = temp3
    ROUGH = roughness_map

    ##################
    ##### TILING #####
    ##################

    row_input, col_input = np.shape(INPUT)
    row_q, row_r = row_input//tile_sz, row_input%tile_sz
    col_q, col_r = col_input//tile_sz, col_input%tile_sz

    TILES = []

    # Quotient
    for r in range(row_q):
        for c in range(col_q):
            tile = INPUT[tile_sz*r:tile_sz*(r+1), tile_sz*c:tile_sz*(c+1)]
            TILES.append(tile)

    if col_r != 0:   
        # Remainder
        for r in range(row_q):
            tile = INPUT[tile_sz*r:tile_sz*(r+1), -col_r:]
            TILES.append(tile)

    if row_r != 0:   
        # Remainder
        for c in range(col_q):
            tile = INPUT[-row_r:, tile_sz*c:tile_sz*(c+1)]
            TILES.append(tile)

    if row_r != 0 and col_r != 0: 
        # very end
        tile = INPUT[-row_r:, -col_r:]
        TILES.append(tile)
        # print("VERY END")

    ROUGHNESS = []

    # Quotient
    for r in range(row_q):
        for c in range(col_q):
            tile = ROUGH[tile_sz*r:tile_sz*(r+1), tile_sz*c:tile_sz*(c+1)]
            ROUGHNESS.append(tile)

    if col_r != 0:  
        # Remainder
        for r in range(row_q):
            tile = ROUGH[tile_sz*r:tile_sz*(r+1), -col_r:]
            ROUGHNESS.append(tile)

    if row_r != 0:  
        # Remainder
        for c in range(col_q):
            tile = ROUGH[-row_r:, tile_sz*c:tile_sz*(c+1)]
            ROUGHNESS.append(tile)

    if row_r != 0 and col_r != 0: 
        # very end
        tile = ROUGH[-row_r:, -col_r:]
        ROUGHNESS.append(tile)
        # print("VERY END")


    new_building_map_tiles = []
    # planarity_map_tiles = []
    
    for tile, rough in zip(TILES,ROUGHNESS):

        planarity_map_tile = np.zeros(np.shape(tile))

        temp3 = tile

        number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(temp3, connectivity = CONNECTIVITY)
        new_mask  = np.ones(np.shape(temp3))#################################
        new_mask2 = np.ones(np.shape(temp3))#################################

        # non-building removal
        for c in range(1,np.max(label_map)+1):#c is each building candidate

            planarity = np.sum(rough[label_map==c]<S1)/np.sum(rough[label_map==c]<999)
            planarity_map_tile[label_map==c] = planarity
            
            # 2500sqm보다 크고, planarity가 낮은거는, 무조건 나무 군집이다.
            if np.sum(label_map==c)>2500/0.5/0.5 and planarity < 0.5:
                planarity_map_tile[label_map==c] = -1

        new_mask = planarity_map_tile > S2
        new_mask2 = planarity_map_tile != -1
        
        new_building_map_tile = new_mask*temp3#################################
        new_building_map_tile = new_mask2*new_building_map_tile#################################
        
        new_building_map_tiles.append(new_building_map_tile)
        # planarity_map_tiles.append(planarity_map_tile)
        

    ########################
    ##### FILLING BACK #####
    ########################

    new_building_map = np.zeros((row_input, col_input))
    # planarity_map = np.zeros((row_input, col_input))
    # Quotient
    count=0
    for r in range(row_q):
        for c in range(col_q):
            new_building_map[tile_sz*r:tile_sz*(r+1), tile_sz*c:tile_sz*(c+1)] = new_building_map_tiles[count]
            # planarity_map[tile_sz*r:tile_sz*(r+1), tile_sz*c:tile_sz*(c+1)] = planarity_map_tiles[count]
            count = count+1

    if col_r != 0:
        # Remainder
        for r in range(row_q):
            new_building_map[tile_sz*r:tile_sz*(r+1), -col_r:] = new_building_map_tiles[count]
            # planarity_map[tile_sz*r:tile_sz*(r+1), -col_r:] = planarity_map_tiles[count]
            count = count+1

    if row_r != 0: 
        # Remainder
        for c in range(col_q):
            new_building_map[-row_r:, tile_sz*c:tile_sz*(c+1)] = new_building_map_tiles[count]
            # planarity_map[-row_r:, tile_sz*c:tile_sz*(c+1)] = planarity_map_tiles[count]
            count = count+1

    if row_r != 0 and col_r != 0: 
        # very end
        new_building_map[-row_r:, -col_r:] = new_building_map_tiles[count]
        # planarity_map[-row_r:, -col_r:] = planarity_map_tiles[count]
        count = count+1
    
    # 3d building map
    NDHM_F = ndimage.median_filter(ndhm_frst,5)
    BLDG3D = np.multiply(new_building_map,NDHM_F)

    # save_map(bldg_map_fn, new_building_map, water_.ncol, water_.nrow, target_epsg, water_.geotransform, format=out_format)
    save_map(bldg_3d_map_fn, BLDG3D, BLDG3D.shape[1], BLDG3D.shape[0], target_epsg, gt, format=out_format)
    save_map(roughness_map_fn, roughness_map, roughness_map.shape[1], roughness_map.shape[0], target_epsg, gt, format=out_format)


def get_args():
    
    argparser = argparse.ArgumentParser(description=__doc__)
    
    argparser.add_argument(
        '--fn',
        type=str,
        help='water filename')
    
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
        type=int,
        help='target epsg code')   
    
    args = argparser.parse_args()
    return args


if __name__ == '__main__': 
    
    args = get_args()
    generate_bldg_map(args.fn, args.outdir, args.usfeet, args.target_epsg)