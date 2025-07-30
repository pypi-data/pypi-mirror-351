import os
import glob
from u3m.map.bldg import generate_bldg_map
from u3m.map.dtm import generate_dtm
from u3m.map.ndhm import generate_ndhm
from u3m.map.tree import generate_tree_map
from u3m.map.water import generate_water_map, refine_water_map
from multiprocessing import Pool
from u3m.generate.merge import gdal_buildvrt, gdal_warpcog
import tqdm
from u3m.utils.utils import istarmap
from u3m.generate.workerProcess import generate_dsm_worker



def dsm(wsdir,lasdir,outdir,cogdir,usfeet,current_epsg,target_epsg,lonlat,num_thread,target_resolution):
    
    basename = os.path.basename(wsdir)
    # create output directory
    os.makedirs(f"{outdir}/OCC/", exist_ok=True)
    os.makedirs(f"{outdir}/DSM_FRST/", exist_ok=True)
    os.makedirs(f"{outdir}/DSM_LAST/", exist_ok=True)
        
    # generate dsm for each las file
    dsm_list = os.listdir(outdir + '/DSM_LAST/')
    las_filelist = sorted(glob.glob(lasdir+'/*.laz')) + sorted(glob.glob(lasdir+'/*.las'))
    outdirs = [outdir] * len(las_filelist)
    usfeets = [usfeet] * len(las_filelist)
    current_epsgs = [current_epsg] * len(las_filelist)
    target_epsgs = [target_epsg] * len(las_filelist)
    lonlats = [lonlat] * len(las_filelist)
    target_resolutions = [target_resolution] * len(las_filelist)
    
    args = tuple(zip(las_filelist, outdirs, usfeets, current_epsgs, target_epsgs, target_resolutions, lonlats))
    
    with Pool(num_thread) as p:
        results = list(tqdm.tqdm(istarmap(p,generate_dsm_worker,args), total=len(las_filelist)))
        
    # merge dsm
    if 'ALL_DSM_LAST.vrt' in dsm_list:
        print("DSM LAST VRT already exist")
    else:
        gdal_buildvrt(outdir, dsm=True)
    
    cog_fn = basename + '_DSM_FRST.tif'
    try:
        cog_list = os.listdir(cogdir)
        if cog_fn in cog_list:
            print("DSM FRST COG file already exist")
        else:
            gdal_warpcog(wsdir, cogdir, dsm=True)
    except:
        gdal_warpcog(wsdir, cogdir, dsm=True)



def dtm(wsdir, outdir, cogdir, usfeet, target_epsg, extent, buffer, slope_threshold, target_resolution):
    
    basename = os.path.basename(wsdir)
    # create output directory
    os.makedirs(f"{outdir}/DTM_LAST/", exist_ok=True)
    
    # generate dtm for each tile
    generate_dtm(outdir, usfeet, target_epsg, LARGE_EXTENT=extent, BUFFR_EXTENT=buffer, slope_threshold=slope_threshold, target_resolution=target_resolution)
    
    # check if merged DTM already exists.
    dtm_all = glob.glob(f"{outdir}/DTM_LAST/ALL_DTM_LAST.vrt")
    if dtm_all:
        print('DTM LAST VRT already exists')  
    else:
        # merge dtm tiles
        gdal_buildvrt(outdir, dtm=True)
        
    cog_fn = basename + '_DTM_LAST.tif'
    cog_list = os.listdir(cogdir)
    if cog_fn in cog_list:
        print("DTM LAST COG file already exist")
    else:
        gdal_warpcog(wsdir, cogdir, dtm=True)



def ndhm(wsdir, outdir, cogdir, target_epsg):
    
    basename = os.path.basename(wsdir)
    # create output directory
    os.makedirs(f"{outdir}/NDHM_FRST/", exist_ok=True)
    os.makedirs(f"{outdir}/NDHM_LAST/", exist_ok=True)

    # generate ndhm
    generate_ndhm(outdir, target_epsg)
    
    # check if merged NDHM already exists.
    ndhm_first_all = glob.glob(f"{outdir}/NDHM_FRST/ALL_NDHM_FRST.vrt")
    ndhm_last_all = glob.glob(f"{outdir}/NDHM_LAST/ALL_NDHM_LAST.vrt")
    if ndhm_first_all and ndhm_last_all :
        print('NDHM VRT already exists')
    else:
        # merge ndhm tiles
        gdal_buildvrt(outdir, ndhm=True)
        
    cog_fn = basename + '_NDHM_LAST.tif'
    cog_list = os.listdir(cogdir)
    if cog_fn in cog_list:
        print("NDHM LAST COG file already exist")
    else:
        gdal_warpcog(wsdir, cogdir, ndhm=True)


def water(wsdir, outdir, cogdir, usfeet, target_epsg):
    
    basename = os.path.basename(wsdir)
    # create output directory
    os.makedirs(f"{outdir}/WATER_MAP/", exist_ok=True)

    # generate water map
    generate_water_map(outdir, usfeet, target_epsg)
    
    # check if merged water map already exists.
    water_all = glob.glob(f"{outdir}/WATER_MAP/ALL_TOTAL_WATER.vrt")
    if water_all:
        print('TOTAL WATER VRT already exists')  
    else:
        # merge water tiles
        gdal_buildvrt(outdir, water=True)
        
    # cog_fn = basename + 'TOTAL_WATER.tif'
    # cog_list = os.listdir(cogdir)
    # if cog_fn in cog_list:
    #     print("TOTAL WATER COG file already exist")
    # else:
    #     gdal_warpcog(wsdir, cogdir, water=True)
        
        
def water_refine(wsdir, outdir, cogdir, usfeet, target_epsg):
    
    basename = os.path.basename(wsdir)
    # create output directory
    os.makedirs(f"{outdir}/WATER_MAP/", exist_ok=True)


    # generate refine water map
    refine_water_map(outdir, usfeet, target_epsg, target_epsg)
    
    # check if merged water map already exists.
    water_new_all = glob.glob(f"{outdir}/WATER_MAP/ALL_NEW_TOTAL_WATER.vrt")
    if water_new_all:
        print('NEW TOTAL WATER VRT already exists')  
    else:
        # merge water tiles
        gdal_buildvrt(outdir, water_new=True)
        
    cog_fn = basename + '_NEW_TOTAL_WATER.tif'
    cog_list = os.listdir(cogdir)
    if cog_fn in cog_list:
        print("NEW TOTAL WATER COG file already exist")
    else:
        gdal_warpcog(wsdir, cogdir, water_new=True)




def bldg(wsdir, outdir, cogdir, usfeet, target_epsg):
    
    basename = os.path.basename(wsdir)
    # create output directory
    os.makedirs(f"{outdir}/BUILDING_MAP/", exist_ok=True)

    # generate building map
    generate_bldg_map(outdir, usfeet, target_epsg)    
    
    # check if merged bldg map already exists.
    bldg_all = glob.glob(f"{outdir}/BUILDING_MAP/ALL_BUILDING_MAP.vrt")
    rough_all = glob.glob(f"{outdir}/BUILDING_MAP/ALL_ROUGHNESS_MAP.vrt")
    if bldg_all and rough_all:
        print('BUILDING and ROUGHNESS MAP VRT already exists')  
    else:
        # merge bldg tiles
        gdal_buildvrt(outdir, bldg=True)
    
    cog_fn = basename + '_BUILDING_MAP_3D.tif'
    cog_list = os.listdir(cogdir)
    if cog_fn in cog_list:
        print("BUILDING 3D MAP COG file already exist")
    else:
        gdal_warpcog(wsdir, cogdir, bldg=True)
        
    
def tree(wsdir, outdir, cogdir, usfeet, target_epsg):
    
    basename = os.path.basename(wsdir)
    # create output directory
    os.makedirs(f"{outdir}/TREE_MAP/", exist_ok=True)

    # generate tree map
    generate_tree_map(wsdir, outdir, usfeet, target_epsg, OPTION1=False, OPTION2=True)
    
    # check if merged tree map already exists.
    tree_all = glob.glob(f"{outdir}/TREE_MAP/ALL_TREE_MAP.vrt")
    if tree_all:
        print('TREE MAP VRT already exists')  
    else:
        # merge tree tiles
        gdal_buildvrt(outdir, tree=True)
        
    cog_fn = basename + '_TREE_MAP.tif'
    cog_list = os.listdir(cogdir)
    if cog_fn in cog_list:
        print("TREE MAP COG file already exist")
    else:
        gdal_warpcog(wsdir, cogdir, tree=True)
   
   
