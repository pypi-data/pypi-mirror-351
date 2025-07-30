import copy
import numpy as np
from scipy import interpolate
from rs_tools import geo2proj
import os
import laspy
import argparse
from u3m.utils.utils import save_map

def generate_dsm(las_fn, outdir, usfeet, current_epsg, target_epsg, target_resolution = 0.5, lonlat=False, out_format='GTiff'):
    
    try:
        dsm_list = os.listdir(os.path.join(outdir,'DSM_LAST'))
    except:
        dsm_list = []
        
    target_resolution = float(target_resolution)
    
    fid = os.path.splitext(os.path.basename(las_fn))[0]
    dsm_id = f"DSM_LAST_{fid}.tif"
    
    if dsm_id in dsm_list:
        print(f"{dsm_id} already exist", flush=True)
        return
    else:
        las = laspy.read(las_fn)
        # DSM
        BoundOff = False
        #
        if usfeet:
            # intenstity remove
            # points_temp = np.vstack((las.x, las.y, las.z*0.3048, las.intensity)).transpose()
            points_ = np.vstack((las.x, las.y, las.z*0.3048)).transpose()
            DSM_resolution = target_resolution*1/0.3048
        else:
            # points_temp = np.vstack((las.x, las.y, las.z, las.intensity)).transpose()
            points_ = np.vstack((las.x, las.y, las.z)).transpose()
            DSM_resolution = target_resolution
        
        if current_epsg != target_epsg:
            x, y = geo2proj(points_[:,0], points_[:,1], current_epsg=current_epsg, target_epsg=target_epsg)
            points = np.vstack((x, y, points_[:,2])).transpose()
        else:
            points = points_
        
        
        num_points = points.shape[0]
        #
        if BoundOff == True:
            #
            Bound_off_rate = 0.01
            #
            sorted_X = np.sort(points[:,0])
            sorted_y = np.sort(points[:,1])
            #
            min_x = sorted_X[int(len(points)*Bound_off_rate)]
            max_x = sorted_X[int(len(points)*(1-Bound_off_rate))]
            min_y = sorted_y[int(len(points)*Bound_off_rate)]
            max_y = sorted_y[int(len(points)*(1-Bound_off_rate))]
        else:
            #
            min_x = min(points[:,0])
            max_x = max(points[:,0])
            min_y = min(points[:,1])
            max_y = max(points[:,1])
        #
        lidar = np.zeros((num_points, 5))
        #
        ncol = max_x-min_x # 1meter/feet resolution
        nrow = max_y-min_y # 1meter/feet resolution
        nrow_out = int(np.ceil(nrow/DSM_resolution))
        ncol_out = int(np.ceil(ncol/DSM_resolution))
        #
        if nrow_out == 0 or ncol_out == 0:
            # print(f"{dsm_id}: the size of input array is zero")
            return

        ul_x = min(points[:,0])
        ul_y = max(points[:,1])
        #
        gt_out = [ul_x, DSM_resolution, 0, ul_y, 0, -DSM_resolution]
    
        #x,y,z,intensity
        lidar[:,0:3] = points[:,0:3]
        #col
        lidar[:,3] = (lidar[:,0]-ul_x)/DSM_resolution
        #row
        lidar[:,4] = (lidar[:,1]-ul_y)/(-DSM_resolution)
        
        # Initialize INTENSITY array with -999
        # INT_FRST = np.ones((nrow_out, ncol_out), dtype = np.float32)*(-999)
        # INT_LAST = np.ones((nrow_out, ncol_out), dtype = np.float32)*(-999)
        # Initialize DSM array with -999
        DSM_FRST = np.ones((nrow_out, ncol_out), dtype = np.float32)*(-999)
        DSM_LAST = np.ones((nrow_out, ncol_out), dtype = np.float32)*(-999)

        # create progressbar widget       
        # widgets = [
        #     ' [', progressbar.Timer(), '] ',
        #     progressbar.GranularBar(), ' ',
        #     progressbar.Percentage(),
        # ]
        # with progressbar.ProgressBar(max_value=num_points, widgets=widgets, ) as bar:
            # PRE - DSM & Intensity
            # For each LiDAR point
            
        for i in range(num_points):
            # if (i/num_points*10)%1 < 1E-6:
                # bar.update(i)
            #
            col = int(lidar[i,3])
            row = int(lidar[i,4])
            # Check all the points are within DTM boundary
            # if point does not fall within dtm boundary, skip
            if col < 0 or col >= ncol_out:
                #print('x out of dtm boundary', lidar[i,0])
                continue
            if row < 0 or row >= nrow_out:
                #print('y out of dtm boundary', lidar[i,1])
                continue
            # if statement?
            if DSM_FRST[row,col] < lidar[i,2] and DSM_FRST[row,col]==-999:
                DSM_FRST[row,col] = lidar[i,2]
            elif DSM_FRST[row,col] < lidar[i,2]:
                DSM_FRST[row,col] = lidar[i,2]
            #
            if DSM_LAST[row,col] < lidar[i,2] and DSM_LAST[row,col]==-999:
                DSM_LAST[row,col] = lidar[i,2]
            elif DSM_LAST[row,col] > lidar[i,2]:
                DSM_LAST[row,col] = lidar[i,2]
            # #
            # if INT_FRST[row,col] < lidar[i,3] and INT_FRST[row,col]==-999:
            #     INT_FRST[row,col] = lidar[i,3]
            # elif INT_FRST[row,col] < lidar[i,3]:
            #     INT_FRST[row,col] = lidar[i,3]
            # #
            # if INT_LAST[row,col] < lidar[i,3] and INT_LAST[row,col]==-999:
            #     INT_LAST[row,col] = lidar[i,3]
            # elif INT_LAST[row,col] > lidar[i,3]:
            #     INT_LAST[row,col] = lidar[i,3]
	
        # create occupancy map
        w_points = DSM_FRST != -999 
        LiDAR_point_occupancy = w_points

        ## DSM Interpolation # should be processed after creating the water mask
        temp = copy.deepcopy(DSM_FRST)
        temp[temp==-999] = np.nan

        # Nearest Interpolation
        x = np.arange(0, temp.shape[1])
        y = np.arange(0, temp.shape[0])
        # mask invalid values
        temp = np.ma.masked_invalid(temp)
        xx, yy = np.meshgrid(x, y)
        # get only the valid values
        x1 = xx[~temp.mask]
        y1 = yy[~temp.mask]
        newarr = temp[~temp.mask]
	
        INTERP_DSM_FRST = interpolate.griddata((x1, y1), newarr.ravel(),(xx, yy),method='nearest')
        #print("Interpolated_DSM_FRST interpolation generation takes:",time.time()-start_time)


        ## DSM Interpolation # should be processed after creating the water mask
        temp = copy.deepcopy(DSM_LAST)
        temp[temp==-999] = np.nan

        # Nearest Interpolation
        x = np.arange(0, temp.shape[1])
        y = np.arange(0, temp.shape[0])
        # mask invalid values
        temp = np.ma.masked_invalid(temp)
        xx, yy = np.meshgrid(x, y)
        # get only the valid values
        x1 = xx[~temp.mask]
        y1 = yy[~temp.mask]
        newarr = temp[~temp.mask]

        INTERP_DSM_LAST = interpolate.griddata((x1, y1), newarr.ravel(),(xx, yy),method='nearest')
        #print("Interpolated_DSM_LAST interpolation generation takes:",time.time()-start_time)
        
        save_map(os.path.join(outdir,'OCC',f"OCCUPANCY_{fid}.tif"), LiDAR_point_occupancy, ncol_out, nrow_out, target_epsg, gt_out, format=out_format)
        save_map(os.path.join(outdir,'DSM_FRST',f"DSM_FRST_{fid}.tif"), INTERP_DSM_FRST, ncol_out, nrow_out, target_epsg, gt_out, format=out_format)
        save_map(os.path.join(outdir,'DSM_LAST',f"DSM_LAST_{fid}.tif"), INTERP_DSM_LAST, ncol_out, nrow_out, target_epsg, gt_out, format=out_format)

        return 0
    

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
        '--current-epsg',
        type=str,
        help='current epsg code')   
    
    argparser.add_argument(
        '--target-epsg',
        type=str,
        help='target epsg code')   
    
    argparser.add_argument(
        '--lonlat',
        type=int,
        help='if the unit is lon/lat')   
    
    argparser.add_argument(
        '--target-resolution',
        type=str,
        help='output resolution in meter')   
    
    args = argparser.parse_args()
    
    return args


if __name__ == '__main__':
    args = get_args()
    generate_dsm(las_fn=args.fn, outdir=args.outdir, 
                 usfeet=args.usfeet, current_epsg = args.current_epsg, 
                 target_epsg=args.target_epsg, target_resolution=args.target_resolution, 
                 lonlat=args.lonlat)