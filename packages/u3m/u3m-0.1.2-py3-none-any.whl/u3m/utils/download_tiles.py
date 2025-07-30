from pyexpat import features
import numpy as np
import pdal
import json
import argparse
import geopandas as gpd
import os
from pystac_client import Client


def get_params(grid_fn, num_threads_ept = 4):
    
    poly = gpd.GeoDataFrame.from_file(grid_fn)
    poly = poly.sort_values(by='id')
    # poly.to_crs('EPSG:4326', inplace=True)

    # # Compute UTM zone
    x = np.array(poly.geometry.union_all().convex_hull.exterior.coords.xy[0])
    y = np.array(poly.geometry.union_all().convex_hull.exterior.coords.xy[1])
    boundary_arr = np.array([x, y]).T

    # Create a bounding box for the project
    bounding_box = [
        boundary_arr[:, 0].min(),
        boundary_arr[:, 1].min(),
        boundary_arr[:, 0].max(),
        boundary_arr[:, 1].max()
    ]
    # print(bounding_box)

    lon, lat = np.float64(poly.geometry.union_all().convex_hull.centroid.x), np.float64(poly.geometry.union_all().convex_hull.centroid.y)
    zone_number = int((lon + 180) / 6) + 1
    hemisphere = 'north' if lat >= 0 else 'south'
    utm_epsg_code = 32600 + zone_number if hemisphere == 'north' else 32700 + zone_number
    # print(f"UTM EPSG:{utm_epsg_code}")

    # Connect to STAC API
    client = Client.open("https://stac-api.d2s.org")

    # Search 3DEP collection
    search = client.search(
        max_items=10,
        collections=["3dep"],
        bbox=bounding_box,
    )

    # Print STAC Item ID and STAC Browser URL for search results
    stac_browser_base_item_url = "https://stac.d2s.org/collections/3dep/items"
    url_list = []
    for item in search.items():
        # print(f"ID: {item.id}, URL: {stac_browser_base_item_url}/{item.id}")
        # You can also directly access the asset URL from the item
        url_list.append(item.assets["ept.json"].href)

    # print(url_list)
    asset_url = url_list[4]
    print(asset_url)

    epsg_code = 'EPSG:3857'
    poly = poly.to_crs(epsg_code)
    bbox = poly.total_bounds.tolist()
    
    features = poly["geometry"]
    features = list(enumerate(features))

    return features, asset_url, utm_epsg_code, num_threads_ept

def download_tile(features, tag, asset_url, num_threads_ept, utm_epsg_code):
    
    try:
        i, feature = features
        x = np.array(feature.exterior.coords.xy[0])
        y = np.array(feature.exterior.coords.xy[1])
        boundary_arr = np.array([x, y]).T

        # Create a bounding box for the project
        bbox = [
            boundary_arr[:, 0].min(), 
            boundary_arr[:, 1].min(), 
            boundary_arr[:, 0].max(),
            boundary_arr[:, 1].max()
        ]
        
        out_laz = f"./data/{tag}/laz/{tag}_tile_{i:04d}.laz"

        pipeline_json = {
            "pipeline": [
                {
                    "type": "readers.ept",
                    "filename": asset_url,
                    "bounds": f"([{bbox[0]}, {bbox[2]}], [{bbox[1]}, {bbox[3]}])",
                    "threads": num_threads_ept,
                    "tag": "readEpt"
                },
                {
                    "type": "filters.reprojection",
                    "out_srs": f"EPSG:{utm_epsg_code}",
                    "tag": "reproject"
                },
                {
                    "type": "writers.las",
                    "filename": out_laz,
                    "compression": "laszip",
                    "tag": "writeLas"
                }
            ]
        }

        pipe = pdal.Pipeline(json.dumps(pipeline_json))
        count = pipe.execute()
        del pipe
        import gc; gc.collect()
        
        return out_laz, count
    
    except Exception as e:
        print(f"Tile {features[0]} failed: {e}")
        return None, 0


def get_args():
    
    parser = argparse.ArgumentParser(description="Download tiles from EPT")
    parser.add_argument("--grid-fn", type=str, required=True, help="Path to the grid file")
    parser.add_argument("--tile-idx", type=int, required=True, help="Tile index to download")
    parser.add_argument("--tag", type=str, required=True, help="Tag for the output files")
    
    return parser.parse_args()



if __name__ == "__main__":
    
    args = get_args()
    
    features, asset_url, utm_epsg_code, num_threads_ept = get_params(args.grid_fn)
    
    os.makedirs(f'./data/{args.tag}/laz/', exist_ok=True)

    download_tile(
        features=features[args.tile_idx],
        tag = args.tag,
        asset_url = asset_url,
        num_threads_ept = num_threads_ept,
        utm_epsg_code = utm_epsg_code
    )