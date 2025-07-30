import os

def gdal_buildvrt(ws_dir, dsm=False, dtm=False, water=False, ndhm=False, bldg=False, water_new=False, tree=False, ortho=False):

    ds_dir = os.path.join(ws_dir, 'out')
    if dsm:
        for ID in ['DSM_FRST', 'DSM_LAST', 'OCC']:
            print("Building virtual format file for: ", ID)
            command = f"gdalbuildvrt {ds_dir}/{ID}/ALL_{ID}.vrt {ds_dir}/{ID}/*.tif"
            os.system (command)

    if dtm:
        ID = 'DTM_LAST'
        print("Building virtual format file for:", ID)
        command = f"gdalbuildvrt {ds_dir}/{ID}/ALL_{ID}.vrt {ds_dir}/{ID}/{ID}_*.tif"
        os.system (command)
        
    if ndhm:
        for ID in ['NDHM_FRST','NDHM_LAST']:
            print("Building virtual format file for:", ID)                                                 
            command = f"gdalbuildvrt {ds_dir}/{ID}/ALL_{ID}.vrt {ds_dir}/{ID}/{ID}_*.tif"
            os.system (command)
        
    if water:
        for ID in ['TOTAL_WATER','BIG_WATER']:
            print("Building virtual format file for:", ID)
            command = f"gdalbuildvrt {ds_dir}/WATER_MAP/ALL_{ID}.vrt {ds_dir}/WATER_MAP/{ID}_*.tif"
            os.system (command)

    if bldg:
        for ID in ['BUILDING_MAP_3D','ROUGHNESS_MAP']:
            print("Building virtual format file for:", ID)
            command = f"gdalbuildvrt {ds_dir}/BUILDING_MAP/ALL_{ID}.vrt {ds_dir}/BUILDING_MAP/{ID}_*.tif"
            os.system (command)

    if water_new:
        print("Building virtual format file for:", 'NEW_TOTAL_WATER')
        command = f"gdalbuildvrt {ds_dir}/WATER_MAP/ALL_NEW_TOTAL_WATER.vrt {ds_dir}/WATER_MAP/NEW_TOTAL_WATER_*.tif"
        os.system (command)
            
    if tree:
        ID = 'CHM_W_NDVI_MAP'
        print("Building virtual format file for:", ID)
        command = f"gdalbuildvrt {ds_dir}/TREE_MAP/ALL_{ID}.vrt {ds_dir}/TREE_MAP/{ID}_*.tif"
        os.system (command)
        
    if ortho:
        print("Building virtual format file for:", 'ORTHO')
        command = f"gdalbuildvrt {ws_dir}/ortho/ALL_ORTHO.vrt {ws_dir}/ortho/*.tif"
        os.system (command)




def gdal_warpcog(ws_dir, cog_dir, dsm=False, dtm=False, water=False, ndhm=False, bldg=False, water_new=False, tree=False):

    base_name = os.path.basename(ws_dir)
    if not base_name:
        base_name = os.path.basename(ws_dir[:-1])
        
    try:
        os.makedirs(cog_dir, exist_ok=True)
    except Exception as e:
        print(e)

    if dsm:
        for ID in ['DSM_FRST', 'DSM_LAST']:
            print("Generate COG tif file: ", ID)
            command = f"gdalwarp {ws_dir}/out/{ID}/ALL_{ID}.vrt {cog_dir}/{base_name}_{ID}.tif \
            -dstnodata 0.000 -of COG -co NUM_THREADS=8 -co BIGTIFF=YES"
            os.system (command)

    if dtm:
        ID = 'DTM_LAST'
        print("Generate COG tif file: ", ID)
        command = f"gdalwarp {ws_dir}/out/{ID}/ALL_{ID}.vrt {cog_dir}/{base_name}_{ID}.tif \
        -dstnodata 0.000 -of COG -co NUM_THREADS=8 -co BIGTIFF=YES"
        os.system (command)
        
    if ndhm:
        for ID in ['NDHM_FRST','NDHM_LAST']:
            print("Generate COG tif file: ", ID)
            command = f"gdalwarp {ws_dir}/out/{ID}/ALL_{ID}.vrt {cog_dir}/{base_name}_{ID}.tif \
            -of COG -co NUM_THREADS=8 -co BIGTIFF=YES"
            os.system (command)   

    if water:
        for ID in ['TOTAL_WATER','BIG_WATER']:
            print("Generate COG tif file: ", ID)
            command = f"gdalwarp {ws_dir}/out/WATER_MAP/ALL_{ID}.vrt {cog_dir}/{base_name}_{ID}.tif \
            -of COG -co NUM_THREADS=8 -co BIGTIFF=YES"
            os.system (command)

    if bldg:
        for ID in ['BUILDING_MAP_3D']:
            print("Generate COG tif file: ", ID)
            command = f"gdalwarp {ws_dir}/out/BUILDING_MAP/ALL_{ID}.vrt {cog_dir}/{base_name}_{ID}.tif \
            -of COG -co NUM_THREADS=8 -co BIGTIFF=YES"
            os.system (command)
            
    if water_new:
        print("Generate COG tif file: ", 'NEW_TOTAL_WATER')
        command = f"gdalwarp {ws_dir}/out/WATER_MAP/ALL_NEW_TOTAL_WATER.vrt {cog_dir}/{base_name}_NEW_TOTAL_WATER.tif \
        -of COG -co NUM_THREADS=8 -co BIGTIFF=YES"
        os.system (command)

    if tree:
        ID = 'CHM_W_NDVI_MAP'
        print("Generate COG tif file: ", ID)
        command = f"gdalwarp {ws_dir}/out/TREE_MAP/ALL_{ID}.vrt {cog_dir}/{base_name}_{ID}.tif \
        -of COG -co NUM_THREADS=8 -co BIGTIFF=YES"
        os.system (command)