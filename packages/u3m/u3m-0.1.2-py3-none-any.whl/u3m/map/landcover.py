import numpy as np
from rs_tools import LightImage, world2Pixel
import glob
import os
from u3m.utils.utils import get_intersect_image, save_map
from osgeo import gdal
import argparse
from skimage.transform import resize

def landcover(bldg_fn, wsdir, outdir, target_epsg, VEGET_CRITERIA=0.0, out_format='GTiff'):

    water_list = glob.glob(os.path.join(outdir,'WATER_MAP','*.vrt'))
    ortho_list = glob.glob(os.path.join(wsdir,'ortho','*.vrt'))
    tree_list = glob.glob(os.path.join(outdir,'TREE_MAP','*.vrt'))

    # compute NDVI
    ortho_fn = ortho_list[0]
    # tree
    tree_fn = tree_list[0]
    # water
    water_fn = water_list[0]    
    
    _,_,ext1 = get_intersect_image(bldg_fn, ortho_fn, extent=True)
    _,_,ext2 = get_intersect_image(bldg_fn, tree_fn, extent=True)
    _,_,ext3 = get_intersect_image(bldg_fn, water_fn, extent=True)

    if ext1 is None or ext2 is None or ext3 is None:
        print('No intersection found with the provided files.')
        return
    ext = np.array([ext1,ext2,ext3])
    ext_left,ext_up,ext_right,ext_down = np.max(ext[:,0]), np.min(ext[:,1]), np.min(ext[:,2]), np.max(ext[:,3])

    BLDG = LightImage(bldg_fn)
    ORTHO = LightImage(ortho_fn)  
    TREE = LightImage(tree_fn)
    TW = LightImage(water_fn)
    
    minx,miny = world2Pixel(TW.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(TW.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('Water map is out of bounds.')
        return
    water,_ = TW.get_box_all(minx,maxx,miny,maxy)
    water = water[0,:,:]
    
    minx,miny = world2Pixel(BLDG.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(BLDG.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('Building map is out of bounds.')
        return
    bldg,_ = BLDG.get_box_all(minx,maxx,miny,maxy)
    bldg = bldg[0,:,:]
    
    minx,miny = world2Pixel(ORTHO.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(ORTHO.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('Ortho image is out of bounds.')
        return
    ortho,_ = ORTHO.get_box_all(minx,maxx,miny,maxy)
    
    minx,miny = world2Pixel(TREE.geotransform, ext_left, ext_up)
    maxx,maxy = world2Pixel(TREE.geotransform, ext_right, ext_down)
    if minx < 0 or miny <0:
        print('Tree map is out of bounds.')
        return
    tree,_ = TREE.get_box_all(minx,maxx,miny,maxy)
    tree = tree[0,:,:]
    
    # print('Building:', bldg.shape)
    # print('Tree:', tree.shape)
    # print('Water:', water.shape)
    # print('Ortho:', ortho.shape)
    
    R = ortho[0,:,:].astype(np.float32)
    R[R==0]=np.nan
    NIR = ortho[3,:,:].astype(np.float32)
    NIR[NIR==0]=np.nan
    NDVI = (NIR-R)/(NIR+R)
    
    # Resample NDVI to match the shape of bldg
    if NDVI.shape != bldg.shape:
        NDVI = resize(NDVI, bldg.shape, order=0, mode='reflect', preserve_range=True)
    
    if tree.shape != bldg.shape:
        tree = resize(tree, bldg.shape, order=0, mode='reflect', preserve_range=True)
        
    if water.shape != bldg.shape:
        water = resize(water, bldg.shape, order=0, mode='reflect', preserve_range=True)

    IMPV = NDVI<=VEGET_CRITERIA
    VEGT = NDVI>VEGET_CRITERIA

    LC_2D = np.zeros(np.shape(bldg))

    # order should be changed to superimpose
    LC_2D[np.int16(IMPV)>0]=5 # IMPERV
    LC_2D[np.int16(VEGT)>0]=4 # VEGET
    LC_2D[np.int16(tree)>0]=2 # TREE
    LC_2D[np.int16(water)>0]=3 # WATER    
    LC_2D[np.int16(bldg)>0]=1 # BLDG

    LC_2D = np.uint8(LC_2D)

    color_map = np.array([
        [0, 0, 0],
        [255, 0, 0],
        [34, 139, 34],
        [0, 0, 255],
        [124, 252, 0],
        [170, 170, 170],
    ])

    # Assuming LC_2D is a NumPy array
    # Use the color_map to replace values in LC_2D with their corresponding colors
    data_3d = color_map[LC_2D]
    
    fid = '_'.join(os.path.basename(bldg_fn).split('_')[3:])[:-4]
    map_fn = f'{outdir}/LC/LAND_COVER_MAP_{fid}.tif'
    
    # Assuming data_3d is a NumPy array with shape (height, width, 3)
    nrow_out, ncol_out, bands = data_3d.shape
    geotransform = (ext_left, BLDG.x_spacing, 0.0, ext_up, 0.0, BLDG.y_spacing)

    save_map(map_fn, data_3d, ncol_out, nrow_out,
                target_epsg, geotransform, bands=bands, format=out_format, eType=gdal.GDT_Byte)


def get_args():
    
    parser = argparse.ArgumentParser(description='Landcover classification')
    parser.add_argument('--bldg-fn', type=str, required=True, help='Building map file name')
    parser.add_argument('--wsdir', type=str, required=True, help='Workspace directory')
    parser.add_argument('--outdir', type=str, required=True, help='Output directory')
    parser.add_argument('--target-epsg', type=int, required=True, help='Target EPSG code')
    parser.add_argument('--VEGET_CRITERIA', type=float, default=0.0, help='Vegetation criteria for NDVI')
    parser.add_argument('--out-format', type=str, default='GTiff', help='Output format (default: GTiff)')
    
    return parser.parse_args()


if __name__ == "__main__":
    
    args = get_args()
    landcover(args.bldg_fn, args.wsdir, args.outdir, args.target_epsg, args.VEGET_CRITERIA, args.out_format)