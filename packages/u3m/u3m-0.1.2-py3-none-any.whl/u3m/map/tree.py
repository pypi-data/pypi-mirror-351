import numpy as np
from scipy import ndimage
import cv2
from rs_tools.rs3 import LightImage, world2Pixel
from u3m.utils.utils import define_kernel,get_intersect_image,save_map
import glob
import os
import argparse
from skimage.transform import resize

def generate_tree_map(fn, wsdir, outdir, usfeet, target_epsg, 
                      OHT=5,OPTION1=False,OPTION2=True,out_format='GTiff'):

    bldg_list = sorted(glob.glob(os.path.join(outdir,'BUILDING_MAP','BUILDING_MAP_3D_*.tif')))
    rough_list = sorted(glob.glob(os.path.join(outdir,'BUILDING_MAP','ROUGHNESS_MAP_*.tif')))
    water_list = sorted(glob.glob(os.path.join(outdir,'WATER_MAP','TOTAL_WATER_*.tif')))
    ortho_list = glob.glob(os.path.join(wsdir,'ortho','ALL_ORTHO_IMAGE.vrt'))
    ndhm_frst_fn = os.path.join(outdir,'NDHM_FRST','ALL_NDHM_FRST.vrt')
    ndhm_last_fn = os.path.join(outdir,'NDHM_LAST','ALL_NDHM_LAST.vrt')
    NDHMF = LightImage(ndhm_frst_fn)
    NDHML = LightImage(ndhm_last_fn)
    
    if ortho_list:
        ortho_fn = ortho_list[0]
        ORTHO = LightImage(ortho_fn)
        NDVI_EXISTS = True
        print('Ortho imagery has detected!')
    else:
        NDVI_EXISTS = False
        print('No ortho imagery has found')

    # for bldg_fn in tqdm.tqdm(bldg_list):
        
    bldg_fn = fn
    # get fid
    fid = '_'.join(os.path.basename(bldg_fn).split('_')[3:])[:-4]
    chm_list = glob.glob(os.path.join(outdir,'TREE_MAP','CHM_W_NDVI_MAP_*.tif'))
    chm_with_ndvi_map_fn = os.path.join(outdir,'TREE_MAP',f'CHM_W_NDVI_MAP_{fid}.tif')
    if chm_with_ndvi_map_fn in chm_list:
        print(f'{chm_with_ndvi_map_fn} already exists')
        return
    
    # check if all three inputs exist
    water_fn = os.path.join(outdir,'WATER_MAP',f'TOTAL_WATER_{fid}.tif')
    if water_fn not in water_list:
        print('No water map')
        return
    rough_fn = os.path.join(outdir,'BUILDING_MAP',f'ROUGHNESS_MAP_{fid}.tif')
    if rough_fn not in rough_list:
        print('No roughness map')
        return
    
    # get intersect region
    _,_,ext1 = get_intersect_image(bldg_fn, water_fn, extent=True)
    _,_,ext2 = get_intersect_image(bldg_fn, ortho_fn, extent=True)
    _,_,ext3 = get_intersect_image(water_fn, ortho_fn, extent=True)
    if ext1 is None or ext2 is None or ext3 is None:
        return
    ext = np.array([ext1,ext2,ext3])
    ext_left,ext_up,ext_right,ext_down = np.max(ext[:,0]), np.min(ext[:,1]), np.min(ext[:,2]), np.max(ext[:,3])
    
    TW = LightImage(water_fn)
    BLDG = LightImage(bldg_fn)
    ROUGH = LightImage(rough_fn)
    
    minx,miny = world2Pixel(TW.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(TW.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('No water map intersect')
        return
    totalwater,_ = TW.get_box_all(minx,maxx,miny,maxy)
    totalwater = totalwater[0,:,:]
    
    minx,miny = world2Pixel(BLDG.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(BLDG.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('No building map intersect')
        return
    bldg,_ = BLDG.get_box_all(minx,maxx,miny,maxy)
    New_Building = bldg[0,:,:]
    
    minx,miny = world2Pixel(ROUGH.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(ROUGH.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('No roughness map intersect')
        return
    rough,_ = ROUGH.get_box_all(minx,maxx,miny,maxy)
    Roughness_Map = rough[0,:,:]
    
    minx,miny = world2Pixel(NDHMF.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(NDHMF.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('No NDHM map intersect')
        return
    ndhmf,_ = NDHMF.get_box_all(minx,maxx,miny,maxy)
    NDHM_F = ndhmf[0,:,:]
    
    minx,miny = world2Pixel(NDHML.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(NDHML.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('No NDHM intersect')
        return
    ndhml,_ = NDHML.get_box_all(minx,maxx,miny,maxy)
    NDHM_L = ndhml[0,:,:]
    
    minx,miny = world2Pixel(ORTHO.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(ORTHO.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('No ortho image intersect')
        return
    ortho,_ = ORTHO.get_box_all(minx,maxx,miny,maxy)
    
    # compute NDVI
    R = ortho[0,:,:].astype(np.float32)
    R[R==0]=np.nan
    NIR = ortho[3,:,:].astype(np.float32)
    NIR[NIR==0]=np.nan
    NDVI = (NIR-R)/(NIR+R)
    
    if totalwater.shape != New_Building.shape:
        New_Building = resize(New_Building, totalwater.shape, order=0, mode='reflect', preserve_range=True)
    if totalwater.shape != Roughness_Map.shape:
        Roughness_Map = resize(Roughness_Map, totalwater.shape, order=0, mode='reflect', preserve_range=True)
    if totalwater.shape != NDHM_F.shape:
        NDHM_F = resize(NDHM_F, totalwater.shape, order=0, mode='reflect', preserve_range=True)
    if totalwater.shape != NDHM_L.shape:
        NDHM_L = resize(NDHM_L, totalwater.shape, order=0, mode='reflect', preserve_range=True)
    if totalwater.shape != NDVI.shape:
        NDVI = resize(NDVI, totalwater.shape, order=0, mode='reflect', preserve_range=True)
    
    # OHT = 5
    TREE_IS_TALLER_THAN_THIS = 2

    FILLHOLE = False
    FILLHOLE_BY_MEDIAN = True

    TALL_BUILDING_IS_BEFORE = True
    TALL_BUILDING_IS_AFTER = False
    TALL_HEIGHT = 20

    # Building buffer
    B_BUFFER = 7
    T_BUFFER = 9

    BUILDING_BUFFER_KERNEL = np.ones((B_BUFFER,B_BUFFER))
    TALLBUILDING_BUFFER_KERNEL = np.ones((T_BUFFER,T_BUFFER))
    
    VEGET_CRITERIA = 0
    
    KERNEL3D,KERNEL5D,KERNEL7D,KERNEL9D = \
        define_kernel(3),define_kernel(5),define_kernel(7),define_kernel(9)
    
    # print("------------------------------------")
    # print("OHT:", OHT)

    BLDG3D = np.multiply(New_Building, NDHM_L)

    Tall_Building = BLDG3D>=TALL_HEIGHT

    Tall_Building_Buffer = ndimage.binary_dilation(Tall_Building, structure=TALLBUILDING_BUFFER_KERNEL)

    ## non buildings
    NDHM_F[NDHM_F<0]=0

    ## Non Building and high points are trees
    # Building buffer
    New_Building_buffered = ndimage.binary_dilation(New_Building, structure=BUILDING_BUFFER_KERNEL)
    TREE_CANDIDATE1 = np.multiply(NDHM_F, 1-New_Building_buffered)

    # Tall Building Boundary Mask by Kernel2
    if TALL_BUILDING_IS_BEFORE:
        TREE_CANDIDATE1 = np.multiply(TREE_CANDIDATE1, 1-Tall_Building_Buffer)

    ## OVERHANGING TREE SHOULD BE CALUCLATED on NON-BUFFERED BUILDING
    if OPTION1:
        overhanging_tree = np.multiply(New_Building,Roughness_Map>OHT)
        TREE_CANDIDATE2 = np.multiply(NDHM_F, overhanging_tree)

    ## ONLY "SMALL (<2500sqm)" building with rough points are overhanging trees
    if OPTION2:        
        temp = np.uint8(New_Building)

        LARGE_BUILDING_THRESHOLD = 2500

        CONNECTIVITY = 8

        number_of_labels, label_map, stats, centroids = cv2.connectedComponentsWithStats(temp, connectivity = CONNECTIVITY)
        # print("shape of stats:",np.shape(stats))
        stats_T = np.transpose(stats)
        bbox_area = np.multiply(stats_T[2], stats_T[3])
        area_stat = stats_T[4]

        labels_meeting_criteria = np.where(area_stat >= LARGE_BUILDING_THRESHOLD/(0.5*0.5))[0][1:]
        mask = np.isin(label_map, labels_meeting_criteria)

        temp = temp-mask

        temp = ndimage.binary_dilation(temp, structure=BUILDING_BUFFER_KERNEL)

        overhanging_tree = np.multiply(temp,Roughness_Map>OHT)
        TREE_CANDIDATE2 = np.multiply(NDHM_F, overhanging_tree)


    TREE_CANDIDATE = TREE_CANDIDATE1 + TREE_CANDIDATE2

    ####################################################################################

    # Tree is not taller than 30 m
    TREE_CANDIDATE[NDHM_F>30] = 0
    TREE_CANDIDATE[totalwater==1]=0

    #############################################

    TREE_1D = TREE_CANDIDATE>TREE_IS_TALLER_THAN_THIS
    if FILLHOLE_BY_MEDIAN:
        TREE_1D = ndimage.median_filter(TREE_1D,5)

    #############################################

    TREE_3D = TREE_CANDIDATE>TREE_IS_TALLER_THAN_THIS
    TREE_3D = np.uint8(TREE_3D)

    if FILLHOLE:
        TREE_3D = ndimage.binary_fill_holes(TREE_3D).astype(int)
    if FILLHOLE_BY_MEDIAN:
        TREE_3D = ndimage.median_filter(TREE_3D,5)

    TREE_3D = ndimage.binary_erosion(TREE_3D, structure=KERNEL3D)
    TREE_3D = ndimage.binary_dilation(TREE_3D, structure=KERNEL3D)

    #############################################

    TREE_5D = TREE_CANDIDATE>TREE_IS_TALLER_THAN_THIS
    TREE_5D = np.uint8(TREE_5D)

    if FILLHOLE:
        TREE_5D = ndimage.binary_fill_holes(TREE_5D).astype(int)
    if FILLHOLE_BY_MEDIAN:
        TREE_5D = ndimage.median_filter(TREE_5D,5)

    TREE_5D = ndimage.binary_erosion(TREE_5D, structure=KERNEL5D)
    TREE_5D = ndimage.binary_dilation(TREE_5D, structure=KERNEL5D)

    #############################################

    TREE_7D = TREE_CANDIDATE>TREE_IS_TALLER_THAN_THIS
    TREE_7D = np.uint8(TREE_7D)

    if FILLHOLE:
        TREE_7D = ndimage.binary_fill_holes(TREE_7D).astype(int)
    if FILLHOLE_BY_MEDIAN:
        TREE_7D = ndimage.median_filter(TREE_7D,5)

    TREE_7D = ndimage.binary_erosion(TREE_7D, structure=KERNEL7D)
    TREE_7D = ndimage.binary_dilation(TREE_7D, structure=KERNEL7D)

    # Tall Building Boundary Mask by Kernel2
    if TALL_BUILDING_IS_AFTER:
        TREE_1D = np.multiply(TREE_1D, 1-Tall_Building_Buffer)
        TREE_3D = np.multiply(TREE_3D, 1-Tall_Building_Buffer)
        TREE_5D = np.multiply(TREE_5D, 1-Tall_Building_Buffer)
        TREE_7D = np.multiply(TREE_7D, 1-Tall_Building_Buffer)

    if NDVI_EXISTS:
        VEGET = NDVI>VEGET_CRITERIA
        VEGET_BUFFER = ndimage.binary_dilation(VEGET, structure=np.ones((15,15)))
    
    if NDVI_EXISTS:
        VEGET = NDVI>VEGET_CRITERIA
        VEGET=ndimage.binary_erosion(VEGET, structure=KERNEL9D)
        VEGET=ndimage.binary_dilation(VEGET, structure=KERNEL9D)          

    # if NDVI_EXISTS:
    #     veget_map_fn = f"{outdir}/TREE_MAP/VEGET_MAP_{fid}.tif"
    #     save_map(veget_map_fn, VEGET, water.ncol, water.nrow, target_epsg, water.geotransform, format=out_format)
    
    ##########################################################################################
    #######################################   3D TREE  #######################################
    ##########################################################################################
    CHM = np.multiply(TREE_5D,NDHM_F)
    CHM[CHM>50]=50
    # chm_map_fn = f"{outdir}/TREE_MAP/CHM_MAP_{fid}.tif"
    # save_map(chm_map_fn, CHM, water.ncol, water.nrow, target_epsg, water.geotransform, format=out_format)
    
    # ##########################################################################################
    # ####################################   TREE with NDVI ####################################
    # ##########################################################################################
    if NDVI_EXISTS:
        TREE_5D_with_NDVI = np.multiply(TREE_5D, VEGET_BUFFER)
        # tree_with_ndvi_map_fn = f"{outdir}/TREE_MAP/TREE_W_NDVI_MAP_{fid}.tif"
        # save_map(tree_with_ndvi_map_fn, TREE_5D_with_NDVI, TW.ncol, TW.nrow, target_epsg, TW.geotransform, format=out_format)
    
    ##########################################################################################
    ##################################   3D TREE with NDVI  ##################################
    ##########################################################################################
    if NDVI_EXISTS:
        CHM_with_NDVI = np.multiply(TREE_5D_with_NDVI,NDHM_F)            
        # CHM_with_NDVI[CHM_with_NDVI>50]=50
        save_map(chm_with_ndvi_map_fn, CHM_with_NDVI, CHM_with_NDVI.shape[1], CHM_with_NDVI.shape[0], 
                    target_epsg, (ext_left, BLDG.x_spacing, 0.0, ext_up, 0.0, BLDG.y_spacing), format=out_format)
        
        
def get_args():
    
    argparser = argparse.ArgumentParser(description=__doc__)
    
    argparser.add_argument(
        '--fn',
        type=str,
        help='building filename')
    
    argparser.add_argument(
        '--wsdir',
        type=str,
        help='working space directory') 
     
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
    generate_tree_map(args.fn, args.wsdir, args.outdir, args.usfeet, args.target_epsg)
    
    