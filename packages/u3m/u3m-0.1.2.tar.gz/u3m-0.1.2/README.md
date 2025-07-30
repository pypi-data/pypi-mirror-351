# urban_3d_mapping

## Install

```bash
conda create -n u3m -c conda-forge gdal pdal python=3.10 -y
conda activate u3m
pip install u3m

# install dependencies
pip install openrs-python
```

## Usage

5. sample usage of main function

    add arguments (-dsm, --dtm, --ndhm, --water, --bldg, --tree, -all) you would like to map

    ex) if you would like to map dsm, dtm, and ndhm
    ```
    python main.py -w {path}/{to}/{your_data} --dsm --dtm --ndhm 
    ```

    ex) if you would like to map all
    ```
    python main.py -w {path}/{to}/{your_data} --all
    ```

6. parameter setting

    --extent: dtm tile extent in pixel (default: 10000)
    --buffer: dtm buffer in pixel (default: 2000)
    --num-thread: multi-processing threads (default: 1)
    --slope-threshold: dtm generation slope threshold (default: 45)


7. If you would like to use slurm,
```
sbatch slurm_main.sh
```



## Data convention

```
data
    laz (input)
        *.laz
        *.las
    ortho (input)
        *.tif
    out (output)
        DSM_FRST
            ALL_DSM_FRST.vrt
            DSM_FRST_*.tif
        DSM_LAST
            ALL_DSM_LAST.vrt
            DSM_LAST_*.tif
        DTM_LAST
            ALL_DTM_LAST.vrt
            DTM_LAST_*.tif
        OCC_LAST
            ALL_OCC_LAST.tif
            OCC_*.tif
        NDHM_FRST
            ALL_NDHM_FRST.vrt
            NDHM_FRST_*.tif
        NDHM_LAST
            ALL_NDHM_LAST.vrt
            NDHM_LAST_*.tif
        WATER_MAP
            ALL_TOTAL_WATER.vrt
            ALL_BIG_WATER.vrt
            TOTAL_WATER_*.tif
            BIG_WATER_*.tif
        BUILDING_MAP
            ALL_BUILDING_MAP.vrt
            ALL_BUILDING_MAP_3D.vrt
            BUILDING_MAP_*.tif
            BUILDING_MAP_3D_*.tif
        TREE_MAP
            ALL_TREE_MAP.vrt
            ALL_TREE_MAP_3D.vrt
            TREE_MAP_*.tif
            TREE_MAP_3D_*.tif

    cog (output)
        data_DSM_FRST.tif
        data_DSM_LAST.tif
        data_NDHM_FRST.tif
        data_NDHM_LAST.tif
        data_BUILDING_MAP.tif
        ...
        
```
