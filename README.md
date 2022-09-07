<div style="font-size:14px; font-family:verdana;">

# <b>Birkett Water - Birkett Lake Extraction</b>

Version 2.0.0

<b>Primary Contact:</b> Mark Carroll Mark.Carroll@nasa.gov

<b>Developers:</b> Caleb Spradlin, Zach Williams

<br/>

- [<b>Birkett Water - Birkett Lake Extraction</b>](#bbirkett-water---birkett-lake-extractionb)
  - [<b>Overview</b>](#boverviewb)
    - [<b>Installing with a singularity container</b>](#binstalling-with-a-singularity-containerb)
  - [<b> User Guide </b>](#b-user-guide-b)
    - [<b> Birkett lake extract application command line invocations</b>](#b-birkett-lake-extract-application-command-line-invocationsb)
    - [<b> Running birkett lake extract application with a container </b>](#b-running-birkett-lake-extract-application-with-a-container-b)
    - [<b> Partial Run </b>](#b-partial-run-b)

## <b>Overview</b>

This documentation shows how to run the Birkett Lake Extraction application.


<br/>

### <b>Installing with a singularity container</b>

Installing the singularity software is out of scope of this documentation. See <https://singularity-docs.readthedocs.io/en/latest/> for guidance on installing singularity.

<b> Pulling the singularity container </b>


Note: The version number is subject to change.


```shell
singularity pull oras://gitlab.nccs.nasa.gov:5050/cisto-ilab/containers/floodmap:4.1.4
```

```
INFO:    Downloading oras image
```

A `.sif` file should have been downloaded:

```shell
ls
```

```
floodmap_4.1.4.sif
```

<br/>

## <b> User Guide </b>

### <b> Birkett lake extract application command line invocations</b>

```shell
$ python /usr/local/ilab/birkett_lake_extract/view/lakeExtractCLV.py \
    -bbox <BOUNDING BOX OF LAKE IN DECIMAL LAT LON FORM> \
    -lakenumber <LAKE NUMBER TO USE FOR OUTPUT FILE NAMES> \
    -start <START YEAR TO USE FOR MOD44W PRODUCT SEARCH> \
    -end <END YEAR TO USE FOR MOD44W PRODUCT SEARCH>
    [-o .]
```

| Command-line-argument | Description                                         |Required/Optional/Flag | Default  | Example                  |
| --------------------- |:----------------------------------------------------|:---------|:---------|:--------------------------------------|
| `-bbox`               | Bounding box of the lake to extract. Must be the largest water body in bounding box. LON_MIN LAT_MIN LON_MAX LAT_MAX                          | Required | N/a      |`-bbox -122.52 42.8 -121.69 43.05`                      |
| `-lakenumber`             | The lake number to use for output naming convention.    | Required     | N/a       |`-lakeNumber 366`         |
| `-start`                  | Start year to use for MOD44W product search. (Min 2001) | Optional     | 2001      |`-start 2001`             |
| `-end`                  | End year to use for MOD44W product search. (Max 2015)     | Optional     | 2015      |`-end 2015`               |
| `-o`                  | Output directory.                                   | Optional | `.`      |`-o /path/to/output/directory`         |

Example

```shell
$ python /usr/local/ilab/birkett_lake_extract/view/lakeExtractCLV.py \
    -o output \
    -start 2001 \
    -end 2015 \
    -lakenumber 366 \
    -bbox -122.52 42.8 -121.69 43.05
```

### <b> Running birkett lake extract application with a container </b>

To execute the birkett lake extract application with a container, you can use the `singularity exec`. Any singularity execution, you need to list the drives to mount to the container.

```shell
$ singularity exec -B <DRIVE-TO-MOUNT-0>,<DRIVE-TO-MOUNT-1> <PATH-TO-CONTAINER> COMMAND
```

For example, in NCCS ADAPT, we need to mount our central storage

```shell
$ singularity exec -B /adapt,/gpfsm,/explore,/panfs,/css,/nfs4m floodmap_4.1.4.sif COMMAND
```

Executing the birkett lake extract application follow these conventions:

```shell
$ singularity exec -B <DRIVE-TO-MOUNT-0>,<DRIVE-TO-MOUNT-1> <PATH-TO-CONTAINER> \ 
    python birkett_lake_extract/view/lakeExtractCLV.py \
    -bbox <BOUNDING BOX OF LAKE IN DECIMAL LAT LON FORM> \
    -lakenumber <LAKE NUMBER TO USE FOR OUTPUT FILE NAMES> \
    -start <START YEAR TO USE FOR MOD44W PRODUCT SEARCH> \
    -end <END YEAR TO USE FOR MOD44W PRODUCT SEARCH>
    [-o .]
```

An example:

```shell
$ singularity exec -B /adapt,/gpfsm,/explore,/panfs,/css,/nfs4m floodmap_4.1.4.sif \
    python /usr/local/ilab/birkett_lake_extract/view/lakeExtractCLV.py \
    -o output \
    -start 2001 \
    -end 2015 \
    -lakenumber 366 \
    -bbox -122.52 42.8 -121.69 43.05
```

### <b> Partial Run </b>

```shell
$ singularity exec -B /adapt,/gpfsm,/explore,/panfs,/css,/nfs4m \
    <path-to-container>/floodmap_4.1.4.sif \
    python /usr/local/ilab/birkett_lake_extract/view/lakeExtractCLV.py -o output -start 2001 -end 2015 -lakenumber 366 -bbox -122.52 42.8 -121.69 43.05 
```

Expected output messages:


```shell
/home/cssprad1/.local/lib/python3.8/site-packages/geopandas/_compat.py:106: UserWarning: The Shapely GEOS version (3.8.0-CAPI-1.13.1 ) is incompatible with the GEOS version PyGEOS was compiled with (3.10.1-CAPI-1.16.0). Conversions between both will be slow.
  warnings.warn(
/gpfsm/ccds01/nobackup/people/cssprad1/projects/LakeExtract/testing/07.11.22.develop/birkett_lake_extract/model/LakeExtract.py:192: UserWarning: More than one results in CMR query. Num of results: 2
  warnings.warn(
2022-07-11 10:47:14; INFO; gdal_translate -projwin -122.52 43.05 -121.69 42.8 -projwin_srs EPSG:4326 -epo -eco -of GTiff output/2-maxextent/MOD44W.h08v04.MaxExtent.2001.2015.20221921046.tif output/2-maxextent/Lake.366.MOD44W.MaxExtentClipped.2001.2015.20221921046.tif
2022-07-11 10:47:14; INFO; Return code: None
2022-07-11 10:47:14; INFO; Message: b'ERROR 1: Computed -srcwin 5024 3336 118 120 falls completely outside raster extent.\n'
2022-07-11 10:47:44; INFO; gdal_translate -projwin -122.52 43.05 -121.69 42.8 -projwin_srs EPSG:4326 -epo -eco -of GTiff output/2-maxextent/MOD44W.h09v04.MaxExtent.2001.2015.20221921046.tif output/2-maxextent/Lake.366.MOD44W.MaxExtentClipped.2001.2015.20221921046.tif
2022-07-11 10:47:44; INFO; Return code: None
2022-07-11 10:47:44; INFO; Message: b''
2022-07-11 10:47:44; INFO; gdal_polygonize.py output/2-maxextent/Lake.366.MOD44W.MaxExtentClipped.2001.2015.20221921046.tif output/3-polygons/Lake.366.Polygonized.20221921046.shp -b 1 -f "ESRI Shapefile" DN
2022-07-11 10:47:44; INFO; Return code: None
2022-07-11 10:47:44; INFO; Message: b''
2022-07-11 10:47:44; INFO; Failed to auto identify EPSG: 7
/home/cssprad1/.local/lib/python3.8/site-packages/geopandas/io/file.py:299: FutureWarning: pandas.Int64Index is deprecated and will be removed from pandas in a future version. Use pandas.Index with the appropriate dtype instead.
  pd.Int64Index,
/home/cssprad1/.local/lib/python3.8/site-packages/geopandas/io/file.py:299: FutureWarning: pandas.Int64Index is deprecated and will be removed from pandas in a future version. Use pandas.Index with the appropriate dtype instead.
  pd.Int64Index,
/home/cssprad1/.local/lib/python3.8/site-packages/geopandas/io/file.py:299: FutureWarning: pandas.Int64Index is deprecated and will be removed from pandas in a future version. Use pandas.Index with the appropriate dtype instead.
  pd.Int64Index,
2022-07-11 10:47:45; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2001.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2001_C6.tif
2022-07-11 10:47:45; INFO; Return code: None
2022-07-11 10:47:45; INFO; Message: b''
2022-07-11 10:47:45; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2001_C6.tif
2022-07-11 10:47:45; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2002.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2002_C6.tif
2022-07-11 10:47:46; INFO; Return code: None
2022-07-11 10:47:46; INFO; Message: b''
2022-07-11 10:47:46; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2002_C6.tif
2022-07-11 10:47:46; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2003.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2003_C6.tif
2022-07-11 10:47:46; INFO; Return code: None
2022-07-11 10:47:46; INFO; Message: b''
2022-07-11 10:47:46; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2003_C6.tif
2022-07-11 10:47:46; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2004.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2004_C6.tif
2022-07-11 10:47:46; INFO; Return code: None
2022-07-11 10:47:46; INFO; Message: b''
2022-07-11 10:47:46; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2004_C6.tif
2022-07-11 10:47:47; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2005.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2005_C6.tif
2022-07-11 10:47:47; INFO; Return code: None
2022-07-11 10:47:47; INFO; Message: b''
2022-07-11 10:47:47; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2005_C6.tif
2022-07-11 10:47:47; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2006.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2006_C6.tif
2022-07-11 10:47:47; INFO; Return code: None
2022-07-11 10:47:47; INFO; Message: b''
2022-07-11 10:47:47; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2006_C6.tif
2022-07-11 10:47:47; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2007.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2007_C6.tif
2022-07-11 10:47:48; INFO; Return code: None
2022-07-11 10:47:48; INFO; Message: b''
2022-07-11 10:47:48; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2007_C6.tif
2022-07-11 10:47:48; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2008.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2008_C6.tif
2022-07-11 10:47:48; INFO; Return code: None
2022-07-11 10:47:48; INFO; Message: b''
2022-07-11 10:47:48; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2008_C6.tif
2022-07-11 10:47:48; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2009.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2009_C6.tif
2022-07-11 10:47:48; INFO; Return code: None
2022-07-11 10:47:48; INFO; Message: b''
2022-07-11 10:47:48; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2009_C6.tif
2022-07-11 10:47:49; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2010.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2010_C6.tif
2022-07-11 10:47:49; INFO; Return code: None
2022-07-11 10:47:49; INFO; Message: b''
2022-07-11 10:47:49; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2010_C6.tif
2022-07-11 10:47:49; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2011.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2011_C6.tif
2022-07-11 10:47:49; INFO; Return code: None
2022-07-11 10:47:49; INFO; Message: b''
2022-07-11 10:47:49; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2011_C6.tif
2022-07-11 10:47:50; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2012.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2012_C6.tif
2022-07-11 10:47:50; INFO; Return code: None
2022-07-11 10:47:50; INFO; Message: b''
2022-07-11 10:47:50; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2012_C6.tif
2022-07-11 10:47:50; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2013.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2013_C6.tif
2022-07-11 10:47:50; INFO; Return code: None
2022-07-11 10:47:50; INFO; Message: b''
2022-07-11 10:47:50; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2013_C6.tif
2022-07-11 10:47:50; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2014.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2014_C6.tif
2022-07-11 10:47:51; INFO; Return code: None
2022-07-11 10:47:51; INFO; Message: b''
2022-07-11 10:47:51; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2014_C6.tif
2022-07-11 10:47:51; INFO; gdalwarp -overwrite -of GTiff -te  -122.52 42.8 -121.69 43.05 -te_srs EPSG:4326 -t_srs ESRI:53008 -tr 231.656345 -231.656345 -dstnodata 3.0 output/4-buffered-rasters/Lake.366.2015.20221921046.tif output/5-final-buffered-rasters/lake_366_MOD44W_2015_C6.tif
2022-07-11 10:47:51; INFO; Return code: None
2022-07-11 10:47:51; INFO; Message: b''
2022-07-11 10:47:51; INFO; Generated output/5-final-buffered-rasters/lake_366_MOD44W_2015_C6.tif
```

Expected final output files:
```shell
[cssprad1@ilab109 08.04.22.main.production]$ ls output/final-buffered-rasters/
lake_366_MOD44W_2001_C6.tif  lake_366_MOD44W_2009_C6.tif
lake_366_MOD44W_2002_C6.tif  lake_366_MOD44W_2010_C6.tif
lake_366_MOD44W_2003_C6.tif  lake_366_MOD44W_2011_C6.tif
lake_366_MOD44W_2004_C6.tif  lake_366_MOD44W_2012_C6.tif
lake_366_MOD44W_2005_C6.tif  lake_366_MOD44W_2013_C6.tif
lake_366_MOD44W_2006_C6.tif  lake_366_MOD44W_2014_C6.tif
lake_366_MOD44W_2007_C6.tif  lake_366_MOD44W_2015_C6.tif
lake_366_MOD44W_2008_C6.tif
```
</div>
