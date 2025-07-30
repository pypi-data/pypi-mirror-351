import os


def generate_dsm_worker(file_name, outdir, usfeet, current_epsg, target_epsg, target_resolution, lonlat):
    
    if usfeet:
        usfeet='1'
    else:
        usfeet='0'
        
    if lonlat:
        lonlat='1'
    else:
        lonlat='0'
        
    # Get the directory where the main.py script is located
    cwd = os.path.dirname(os.path.abspath(__file__))
    mwd = os.path.dirname(cwd)
    os.system(f'python {mwd}/map/dsm.py' + ' --fn ' + file_name + ' --outdir '+ outdir + ' --usfeet '+ usfeet + ' --current-epsg ' + str(current_epsg) + ' --target-epsg ' + str(target_epsg) + ' --lonlat ' + lonlat + ' --target-resolution ' + str(target_resolution))
    
    return 0


def generate_dtm_worker(outdir, usfeet, target_epsg, large_extent, buffer_extent, slope_threshold):
    
    if usfeet:
        usfeet='1'
    else:
        usfeet='0'
        
    cwd = os.getcwd()
    os.system(f'python {cwd}/map/dtm.py' + \
        ' --outdir ' + outdir + ' --usfeet '+ usfeet + ' --target-epsg ' + str(target_epsg) + \
            ' --large-extent ' + large_extent + ' --buffer-extent ' + buffer_extent + ' --slope-threshold ' + slope_threshold)
    
    return 0


def generate_ndhm_worker(file_name, outdir, usfeet, SRC):
    
    if usfeet:
        usfeet='1'
    else:
        usfeet='0'
    
    cwd = os.getcwd()
    os.system(f'python {cwd}/map/ndhm.py' + \
        ' --fn ' + file_name + ' --outdir '+ outdir + ' --usfeet '+ usfeet + ' --SRC ' + SRC)
    
    return 0


def generate_water_worker(file_name, outdir, usfeet, SRC):
    
    if usfeet:
        usfeet='1'
    else:
        usfeet='0'
    
    cwd = os.getcwd()
    os.system(f'python {cwd}/map//water.py' + \
        ' --fn ' + file_name + ' --outdir '+ outdir + ' --usfeet '+ usfeet + ' --SRC ' + SRC)
    
    return 0



def generate_bldg_worker(file_name, outdir, usfeet, SRC):
    
    if usfeet:
        usfeet='1'
    else:
        usfeet='0'
    
    cwd = os.getcwd()
    os.system(f'python {cwd}/map//bldg.py' + \
        ' --fn ' + file_name + ' --outdir '+ outdir + ' --usfeet '+ usfeet + ' --SRC ' + SRC)
    
    return 0