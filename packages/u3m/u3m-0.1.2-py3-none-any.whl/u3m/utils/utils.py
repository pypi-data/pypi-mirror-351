import glob
import numpy as np
import copy
import scipy
from scipy.signal import convolve2d as conv2
from osgeo import gdal, osr
from scipy import interpolate
from skimage.util import view_as_windows as viewW
import laspy
from rs_tools import LightImage, world2Pixel
import multiprocessing.pool as mpp
import pyproj
import os


def get_spatial_reference_from_epsg(epsg):
    
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(epsg)
    SRC = sr.ExportToWkt()
    
    return SRC



def get_spatial_reference_from_epsg(epsg):
    
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(epsg)
    SRC = sr.ExportToWkt()
    
    return SRC


def get_spatial_reference_from_las(lasdir):
    
    las_list = sorted(glob.glob(lasdir + '/*.laz')) + sorted(glob.glob(lasdir + '/*.las'))
    las = laspy.read(las_list[0])
    check=False
    
    # check variable length records
    try:
        for i in range(len(las.vlrs)):
            unit = las.vlrs[i].parse_crs().axis_info[0].unit_name
            # src = las.vlrs[i].string
            crs = las.vlrs[i].parse_crs()
            if crs.is_compound:
                epsg = crs.sub_crs_list[0].to_epsg()
                if epsg is None:
                    epsg = crs.sub_crs_list[0].source_crs.to_epsg()
            else:
                epsg = crs.to_epsg()
            check=True
    except:
        pass
    
    # check extended variable length records
    try:
        for i in range(len(las.evlrs)):        

            unit = las.evlrs[i].parse_crs().axis_info[0].unit_name
            # src = las.evlrs[i].string
            crs = las.evlrs[i].parse_crs()
            if crs.is_compound:
                epsg = crs.sub_crs_list[0].to_epsg()
                if epsg is None:
                    epsg = crs.sub_crs_list[0].source_crs.to_epsg()
            else:
                epsg = crs.to_epsg()
            check=True
    except:
        pass
        
    # return values
    if check:        
        if unit == 'US survey foot':
            usfeet = True
            # print("US survey foot: ",usfeet)
        elif unit == 'meter' or 'metre': 
            usfeet = False
            # print("Meter: ", not usfeet)
        # print("Coordinate reference system: ", crs)    
        return usfeet, epsg
    else:
        return False, False



def get_spatial_reference_from_shp(shpdir, AREA):

    if AREA == 'CHICAGO':
        usfeet = True
        f = glob.glob(f'{shpdir}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'NYC':
        usfeet = False
        EPSG = 26918
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(EPSG)
        SRC = sr.ExportToWkt()
        
    if AREA == 'LA':
        usfeet = True
        EPSG = 2229
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(EPSG)
        SRC = sr.ExportToWkt()
        
    if AREA == 'DENVER':
        usfeet = False
        EPSG = 26913 #DENVER
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(EPSG)
        SRC = sr.ExportToWkt()
        
    if AREA == 'DALLAS':
        usfeet = False
        EPSG = 26914 #DALLAS
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(EPSG)
        SRC = sr.ExportToWkt()
        
    if AREA == 'ORLANDO':
        usfeet = True
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 2236  

    if AREA == 'FLORIDAKEY':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 2236  
        
    if AREA == 'FLORIDAHOLLYWOOD':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 2236  

    if AREA == 'FLORIDAHOLLYWOOD2':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 2236  


    if AREA == 'WINDRIVER':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 2236  


    if AREA == 'NEWORLEANS':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 2236  

    if AREA == 'PURDUE':
        usfeet = True
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'BOSTON':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'CLEVELAND':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'BOULDER':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'MEXICOBEACH_POS':
        usfeet = True
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'MEXICOBEACH_PRE':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'PORTST_POS':
        usfeet = True
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'PORTST_PRE':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'PHOENIX':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'CHICAGO_FEI_1':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'CHICAGO_FEI_2':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  

    if AREA == 'CHICAGO_FEI_3':
        usfeet = False
        f = glob.glob(f'{shpdir}/{AREA}/*.shp')[0]
        DS = gdal.OpenEx(f, gdal.OF_VECTOR)
        SRC = DS.GetLayer().GetSpatialRef().ExportToWkt()
    #     EPSG = 26916  
    
    return usfeet, SRC


def save_map(map_fn, src, ncol, nrow, target_epsg, geotransform, bands=1, eType=gdal.GDT_Float32, format='GTiff'):
    os.makedirs(os.path.dirname(map_fn), exist_ok=True)
    driver = gdal.GetDriverByName(format)
    map_ds = driver.Create(map_fn, xsize = int(ncol), ysize = int(nrow), bands = bands, eType=eType)
    wkt = pyproj.CRS.from_epsg(target_epsg).to_wkt()
    map_ds.SetProjection(wkt)
    map_ds.SetGeoTransform(geotransform)
    if bands == 1:
        map_ds.GetRasterBand(1).WriteArray(src)
    else:
        for b in range(bands):
            map_ds.GetRasterBand(b + 1).WriteArray(src[:, :, b])
    map_ds = None
    


def sobel_filter(img):
    Gx = np.array([[1.0, 0.0, -1.0], [2.0, 0.0, -2.0], [1.0, 0.0, -1.0]])
    Gy = np.array([[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]])

    rows, columns = np.shape(img)  # we need to know the shape of the input grayscale image
    sobel_filtered_image = np.zeros(shape=(rows, columns))  # initialization of the output image array (all elements are 0)

    # Now we "sweep" the image in both x and y directions and compute the output

    gx = conv2(img, Gx, boundary='symm', mode='same')
    gy = conv2(img, Gy, boundary='symm', mode='same')
    sobel_filtered_image = np.sqrt(gx ** 2 + gy ** 2)

    return sobel_filtered_image


def scipy_interpolation(img, METHOD):
    x = np.arange(0, img.shape[1])
    y = np.arange(0, img.shape[0])
    # mask invalid values
    img = np.ma.masked_invalid(img)
    xx, yy = np.meshgrid(x, y)
    # get only the valid values
    x1 = xx[~img.mask]
    y1 = yy[~img.mask]
    newarr = img[~img.mask]

    interpolated_img = interpolate.griddata((x1, y1), newarr.ravel(), (xx, yy), method=METHOD)

    return interpolated_img


def interpolation(img, SCALE=5, interpolation_method='linear'):

    dtm_temp = scipy_interpolation(img[::SCALE,::SCALE], METHOD=interpolation_method)
    dtm_temp = scipy.ndimage.zoom(dtm_temp, SCALE, order=0)
    NEW_VALUE_FOR_NAN = np.multiply(np.isnan(img),dtm_temp)

    REPLACE_NAN_WITH_ZERO = copy.deepcopy(img)
    REPLACE_NAN_WITH_ZERO[np.isnan(img)]=0

    interpolated_img = REPLACE_NAN_WITH_ZERO+NEW_VALUE_FOR_NAN
    return interpolated_img




def define_kernel(kernel_size):
    
    if kernel_size == 3:
        kernel = np.ones((3,3))
        kernel[0,0]=0
        kernel[-1,0]=0
        kernel[0,-1]=0
        kernel[-1,-1]=0
    elif kernel_size == 5:
        kernel = np.ones((5,5))
        kernel[0,0]=0
        kernel[-1,0]=0
        kernel[0,-1]=0
        kernel[-1,-1]=0
    elif kernel_size==7:
        kernel = np.ones((7,7))
        kernel[0,0]=0
        kernel[-1,0]=0
        kernel[0,-1]=0
        kernel[-1,-1]=0
        kernel[0,1]=0
        kernel[1,0]=0
        kernel[-1,-2]=0
        kernel[-1,1]=0
        kernel[1,-1]=0
        kernel[0,-2]=0
        kernel[-2,0]=0
        kernel[-2,-1]=0
    elif kernel_size==9:
        kernel = np.ones((9,9))
        kernel[0,:3]=0
        kernel[:3,0]=0
        kernel[0,-3:]=0
        kernel[-1,:3]=0
        kernel[:3,-1]=0
        kernel[-3:,0]=0
        kernel[-1,-3:]=0
        kernel[-3:,-1]=0
    elif kernel_size==15:
        kernel = np.ones((15,15))
        kernel[0,:4]=0
        kernel[:4,0]=0
        kernel[:2,:2]=0
        kernel[0,-4:]=0
        kernel[:4,-1]=0
        kernel[:2,-2:]=0
        kernel[-1,:4]=0
        kernel[-4:,0]=0
        kernel[-2:,:2]=0
        kernel[-1,-4:]=0
        kernel[-4:,-1]=0
        kernel[-2:,-2:]=0

    return kernel



def get_intersect_image(img1_fn, img2_fn, grayscale=True, extent=False):

    img_1 = LightImage(img1_fn)
    img_2 = LightImage(img2_fn)

    # get reference image extent
    ext_left = [img_1.ext_left, img_2.ext_left]
    ext_right = [img_1.ext_right, img_2.ext_right]
    ext_up = [img_1.ext_up, img_2.ext_up]
    ext_down = [img_1.ext_down, img_2.ext_down]

    # set intersection boundary
    inter_left = max(ext_left)
    inter_right = min(ext_right)
    inter_up = min(ext_up)
    inter_down = max(ext_down)
    
    # clip data with reference image extent
    #get pixel boundary
    col_start, row_start = world2Pixel(img_1.geotransform, inter_left, inter_up)
    col_end, row_end = world2Pixel(img_1.geotransform, inter_right, inter_down)
    if (col_end-col_start)<=0 or (row_end-row_start)<=0:
        if extent:
            return None, None, None
        else:
            return None, None
    # image clipping
    if grayscale:
        img1_clip = img_1.get_box(col_start,col_end-1,row_start,row_end-1)
    else:
        img1_clip,_ = img_1.get_box_all(col_start,col_end-1,row_start,row_end-1)
    # img1_clip = img_1.img[0,row_start:row_end,col_start:col_end]
    #get pixel boundary
    col_start, row_start = world2Pixel(img_2.geotransform, inter_left, inter_up)
    col_end, row_end = world2Pixel(img_2.geotransform, inter_right, inter_down)
    if (col_end-col_start)<=0 or (row_end-row_start)<=0:
        if extent:
            return None, None, None
        else:
            return None, None
    # image clipping
    if grayscale:
        img2_clip = img_2.get_box(col_start,col_end-1,row_start,row_end-1)
    else:
        img2_clip,_ = img_2.get_box_all(col_start,col_end-1,row_start,row_end-1)
    # img2_clip = img_2.img[0,row_start:row_end,col_start:col_end]
    
    if extent:
        return img1_clip, img2_clip, [inter_left, inter_up, inter_right, inter_down]
    else:
        return img1_clip, img2_clip



def istarmap(self, func, iterable, chunksize=1):
    """starmap-version of imap
    """
    self._check_running()
    if chunksize < 1:
        raise ValueError(
            "Chunksize must be 1+, not {0:n}".format(
                chunksize))

    task_batches = mpp.Pool._get_tasks(func, iterable, chunksize)
    result = mpp.IMapIterator(self)
    self._taskqueue.put(
        (
            self._guarded_task_generation(result._job,
                                          mpp.starmapstar,
                                          task_batches),
            result._set_length
        ))
    
    return (item for chunk in result for item in chunk)
    
    
# def imclose(self):
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    