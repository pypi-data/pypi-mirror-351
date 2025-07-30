import numpy as np
from d2spy.extras.utils import clip_by_mask
from shapely.geometry import mapping
from pystac_client import Client
import geopandas as gpd
import os
import argparse
import json

# Connect to STAC API
client = Client.open("https://stac-api.d2s.org")


def download_naip(grid_geojson, tag, datetime):

    with open(grid_geojson) as f:
        project_grid = json.load(f)
        
    poly = gpd.GeoDataFrame.from_features(project_grid)
    if len(poly) > 1:
        project_boundary = poly.union_all().convex_hull
    else:
        project_boundary = project_grid['geometry'][0]

    os.makedirs(f'data/{tag}/ortho/', exist_ok=True)
    for i in range(len(poly)):
        
        downloaded_items = [os.path.splitext(fn)[0] for fn in os.listdir(f'data/{tag}/ortho/')]
        print(f"Processing polygon {i+1}/{len(poly)}")
        x = np.array(poly.geometry[i].exterior.coords.xy[0])
        y = np.array(poly.geometry[i].exterior.coords.xy[1])
        boundary_arr = np.array([x, y]).T

        # Create a bounding box for the project
        bounding_box = [
            boundary_arr[:, 0].min(),
            boundary_arr[:, 1].min(),
            boundary_arr[:, 0].max(),
            boundary_arr[:, 1].max()
        ]

        
        # Search 3DEP collection
        search = client.search(
            max_items=10,
            collections=["naip"],
            bbox=bounding_box,
            datetime=datetime,
        )

        items = []
        items_id = []
        for item in search.items():
            # print(f"ID: {item.id}, URL: {stac_browser_base_item_url}/{item.id}")
            items.append(item)
            items_id.append(item.id)
        
        if len(items) == 0:
            print(f"No items found for polygon {i+1}/{len(poly)}")
            continue
        
        item = items[0]
        print(items_id)

        feature = {
            "type": "Feature",
            "geometry": mapping(project_boundary),
            "properties": {
                "name": "Project Boundary"
            }
        }

        if all(item not in items_id for item in downloaded_items):
            print(f"Downloading item {item.id}...")
            # The URL for the NAIP raster is in the "image" asset
            naip_url = item.assets["image"].href
            # print(naip_url)

            # Desired location and name for clipped raster
            out_filename = f"data/{tag}/ortho/{item.id}.tif"

            # Clip the raster
            clip_by_mask(in_raster=naip_url, geojson=feature, out_raster=out_filename)
            downloaded_items.append(item.id)
        else:
            print(f"Item {item.id} already downloaded, skipping.")
            continue


def get_args():
    
    argparser = argparse.ArgumentParser(description=__doc__)
    
    argparser.add_argument(
        '--grid-fn',
        type=str,
        help='project grid filename')
    
    argparser.add_argument(
        '--tag',
        type=str,
        help='tag for the project')
      
    argparser.add_argument(
        '--date',
        nargs=2,
        type=str,
        metavar=('START','END'),
        help='date range in format YYYY-MM-DD,YYYY-MM-DD (no spaces)'
    )
    
    args = argparser.parse_args()
    
    return args
        
        
if __name__ == "__main__":
    # Example usage
    args = get_args()
        
    download_naip(
        grid_geojson=args.grid_fn,
        tag=args.tag, 
        datetime=args.date
        )