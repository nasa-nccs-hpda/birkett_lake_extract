import datetime
import logging
import os
import shutil
from typing import Tuple
import warnings

import geopandas as gpd
import numpy as np
from osgeo import gdal
from osgeo import ogr
from osgeo import osr

from birkett_lake_extract.model.CmrProcess import CmrProcess
from birkett_lake_extract.model.libraries.daac_download import httpdl

from core.model.BaseFile import BaseFile
from core.model.Envelope import Envelope
from core.model.SystemCommand import SystemCommand
from core.model.GeospatialImageFile import GeospatialImageFile


class LakeExtract(object):

    MODSHORT = 'MOD44W'
    MOD44_SHAPE = (4800, 4800)
    BBOX_SRS_EPSG = 'EPSG:4326'
    MOD_SRS = 'ESRI:53008'
    BUFFER_1PX = 231.656
    BUFFER_6PX = 1621.59
    TR_P = 231.656345
    TR_N = -231.656345

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self,
                 bbox: list,
                 outDir: str,
                 lakeNumber: str,
                 startYear: int,
                 endYear: int,
                 logger: logging.Logger or None = None) -> None:

        self._logger = logger
        self._bbox = bbox
        self._lakeNumber = lakeNumber
        self._startYear = startYear
        self._endYear = endYear
        self._outDir = BaseFile(outDir).fileName()

        self._mod44wDir = os.path.join(self._outDir, 'MOD44W')
        self._maxExtentDir = os.path.join(self._outDir, 'maxextent')
        self._polygonDir = os.path.join(self._outDir, 'polygons')
        self._bufferedDir = os.path.join(self._outDir, 'buffered-rasters')
        self._finalBufferedDir = os.path.join(self._outDir,
                                              'final-buffered-rasters')
        self._makeOutputDirs()
        if self._endYear > 2015:
            msg = \
                '{} is outside the'.format(self._endYear) + \
                ' temporal bound (2001 - 2015)' + \
                ' of available MOD44W products. Setting upper bound' + \
                'to 2015.'
            warnings.warn(msg)
            if self._logger:
                self._logger.info(msg)
            self._endYear = 2015

        if self._startYear < 2001:
            msg = '{} is outside the'.format(self._startYear) + \
                ' temporal bound (2001 - 2015)' + \
                ' of available MOD44W products. Setting lower bound' + \
                'to 2001.'
            warnings.warn(msg)
            if self._logger:
                self._logger.info(msg)
            self._startYear = 2001

        self._yearRange = np.arange(self._startYear, self._endYear+1)
        self._createStr = LakeExtract._getPostStr()
        self._envelope = self._createEnvelope()

    # -------------------------------------------------------------------------
    # _makeOutputDirs()
    # -------------------------------------------------------------------------
    def _makeOutputDirs(self) -> None:
        """
        Creates the output directories.
        """
        os.makedirs(self._mod44wDir, exist_ok=True)
        os.makedirs(self._maxExtentDir, exist_ok=True)
        os.makedirs(self._polygonDir, exist_ok=True)
        os.makedirs(self._bufferedDir, exist_ok=True)
        os.makedirs(self._finalBufferedDir, exist_ok=True)

    # -------------------------------------------------------------------------
    # _createEnvelope()
    # -------------------------------------------------------------------------
    def _createEnvelope(self) -> Envelope:
        """
        Creates spatial envelope.
        """
        envelope = Envelope()

        ulx = self._bbox[0]
        uly = self._bbox[3]
        lrx = self._bbox[2]
        lry = self._bbox[1]

        outRasterSRS = osr.SpatialReference()
        outRasterSRS.ImportFromEPSG(4326)

        envelope.addPoint(float(ulx), float(uly), 0.0, outRasterSRS)
        envelope.addPoint(float(lrx), float(lry), 0.0, outRasterSRS)

        return envelope

    # -------------------------------------------------------------------------
    # extractLakes()
    # -------------------------------------------------------------------------
    def extractLakes(self) -> None:
        """
        Main processing function used to run LakeExtract.
        """
        if self._logger:
            self._logger.debug('In extractLakes')

        try:
            mod44w_list = self._getMOD44W()
            tile = os.path.basename(mod44w_list[0]).split('.')[2]
            maxExtentFilePath = self._makeMaxExtent(mod44w_list, tile)
            maxExtentFilePathClipped = self._clipMaxExtent(maxExtentFilePath)
        except RuntimeError:

            # ---
            # If there are more than one tile, try one that isn't outside of
            # extent.
            # ---
            mod44w_list = self._getMOD44W(index=1)
            tile = os.path.basename(mod44w_list[0]).split('.')[2]
            maxExtentFilePath = self._makeMaxExtent(mod44w_list, tile)
            maxExtentFilePathClipped = self._clipMaxExtent(maxExtentFilePath)

        polygonizedLakeFilePath = \
            self._polygonizeLake(maxExtentFilePathClipped)
        cleanedPolygonLakeFilePath = \
            self._cleanPolygon(polygonizedLakeFilePath)

        bufferedPolygonFilePath = \
            os.path.join(self._polygonDir,
                         'Lake.{}.InitialBuffered.{}.shp'.format(
                             self._lakeNumber,
                             self._createStr))

        bufferedPolygonFilePath = self._createBuffer(
            cleanedPolygonLakeFilePath,
            bufferedPolygonFilePath,
            LakeExtract.BUFFER_1PX)

        dissolvedPolygonOutputPath = \
            self._dissolveBuffered(bufferedPolygonFilePath)

        targetLakeFilePath = self._getTargetLake(dissolvedPolygonOutputPath)

        bufferedFullFilePath = os.path.join(
            self._polygonDir,
            'Lake.{}.Buffered.{}.shp'.format(self._lakeNumber,
                                             self._createStr))

        bufferedFullFilePath = self._createBuffer(targetLakeFilePath,
                                                  bufferedFullFilePath,
                                                  LakeExtract.BUFFER_6PX)

        self._extractLakePerYear(mod44w_list, bufferedFullFilePath)
        self._rmOutputDirs()

    # -------------------------------------------------------------------------
    # _getMOD44W()
    # -------------------------------------------------------------------------
    def _getMOD44W(self, index: int = 0) -> list:
        """
        For a given range of years and a bounding box, find and download
        the corresponding MOD44W tile.
        """
        mod44List = []
        for year in self._yearRange:
            temporalStr = LakeExtract._getTemporalWindow(year=year)
            cmrProcessor = CmrProcess(mission=LakeExtract.MODSHORT,
                                      dateTime=temporalStr,
                                      lonLat=','.join(self._bbox))
            mod44DownloadURLList = cmrProcessor.run()
            if len(mod44DownloadURLList) > 1:
                warnings.warn(
                    'More than one results in CMR query.' +
                    ' Num of results: {}'.format(len(mod44DownloadURLList)))
            try:
                mod44DownloadURL = mod44DownloadURLList[index]
            except IndexError:
                msg = 'No results from CMR'
                raise IndexError(msg)
            fileName = os.path.basename(mod44DownloadURL.rstrip())
            filePath = os.path.join(self._mod44wDir, fileName)
            if os.path.exists(filePath):
                mod44List.append(filePath)
                continue
            request_status = httpdl(urlStr=mod44DownloadURL,
                                    localpath=self._mod44wDir,
                                    uncompress=True)
            if request_status == 0 or request_status == 200 \
                    or request_status == 304:
                if not os.path.exists(filePath):
                    msg = '{} was now downloaded from {}'.format(
                        filePath, mod44DownloadURL)
                    raise FileNotFoundError(msg)
                mod44List.append(filePath)
        return mod44List

    # -------------------------------------------------------------------------
    # getTemporalWindow()
    # -------------------------------------------------------------------------
    @staticmethod
    def _getTemporalWindow(year: str) -> str:
        """
        Given a year, return a ISO 8601 temporal range.
        """
        yearStart = datetime.datetime(year, 1, 1)
        yearEnd = datetime.datetime(year, 12, 31)
        temporalStr = '{}Z,{}Z'.format(
            yearStart.isoformat(), yearEnd.isoformat())
        return temporalStr

    # -------------------------------------------------------------------------
    # _makeMaxExtent()
    # -------------------------------------------------------------------------
    def _makeMaxExtent(self, mod44wFileList: list, tile: str) -> str:
        """
        Given a list of MOD44W products, create a max extent product from that
        list.
        """
        transform = None
        projection = None
        maxExtent = np.zeros(LakeExtract.MOD44_SHAPE, dtype=np.int64)
        for i, mod44File in enumerate(mod44wFileList):
            if i == 0:
                transform, projection = LakeExtract._getProjectionTransform(
                    mod44File)
            maxExtent = LakeExtract._getOneYear(mod44File, maxExtent)
        maxExtent = np.where(maxExtent > 0, 1, 0)
        maxExtentOutFilePath = os.path.join(
            self._maxExtentDir,
            'MOD44W.{}.MaxExtent.{}.{}.{}.tif'.format(
                tile, self._startYear, self._endYear, self._createStr)
        )
        driver = gdal.GetDriverByName('GTiff')
        maxExtentOutDS = driver.Create(maxExtentOutFilePath,
                                       LakeExtract.MOD44_SHAPE[0],
                                       LakeExtract.MOD44_SHAPE[1],
                                       gdal.GDT_Int16,
                                       options=['COMPRESS=LZW'])
        maxExtentOutDS.SetGeoTransform(transform)
        maxExtentOutDS.SetProjection(projection)
        maxExtentOutBand = maxExtentOutDS.GetRasterBand(1)
        maxExtentOutBand.WriteArray(maxExtent)
        maxExtentOutBand.SetNoDataValue(250)
        maxExtentOutDS = None
        maxExtentOutBand = None
        driver = None
        return maxExtentOutFilePath

    # -------------------------------------------------------------------------
    # _getOneYear()
    # -------------------------------------------------------------------------
    @staticmethod
    def _getOneYear(fileName: str, maxExtent: np.ndarray) -> np.ndarray:
        """
        Open the MOD44W subdataset and read as array, add to max extent.
        """
        subdatasetFilePath = gdal.Open(fileName).GetSubDatasets()[0][0]
        subdatasetGeoDS = GeospatialImageFile(fileName,
                                              subdataset=subdatasetFilePath)
        subdataset = subdatasetGeoDS.getDataset()
        image = subdataset.GetRasterBand(1).ReadAsArray()
        maxExtent += np.where(image == 1, 1, 0)
        return maxExtent

    # -------------------------------------------------------------------------
    # _getProjectionTransform()
    # -------------------------------------------------------------------------
    @staticmethod
    def _getProjectionTransform(fileName: str) -> Tuple[str, str]:
        """
        Get transform and projection from a MOD44W product.
        """
        subdatasetFilePath = gdal.Open(fileName).GetSubDatasets()[0][0]
        subdatasetGeoDS = GeospatialImageFile(fileName,
                                              subdataset=subdatasetFilePath)
        subdataset = subdatasetGeoDS.getDataset()
        transform = subdataset.GetGeoTransform()
        projection = subdataset.GetProjection()
        return transform, projection

    # -------------------------------------------------------------------------
    # _clipMaxExtent()
    # -------------------------------------------------------------------------
    def _clipMaxExtent(self, maxExtentFilePath: str) -> str:
        """
        Clip a max extent product to the bounding box.
        """
        maxExtentClippedFilename = \
            'Lake.{}.MOD44W.MaxExtentClipped.{}.{}.{}.tif'.format(
                self._lakeNumber,
                self._startYear,
                self._endYear,
                self._createStr)

        maxExtentClippedFilePath = os.path.join(
            self._maxExtentDir, maxExtentClippedFilename)

        cmd = 'gdal_translate' + \
            ' -projwin' + \
            ' ' + str(self._envelope.ulx()) + \
            ' ' + str(self._envelope.uly()) + \
            ' ' + str(self._envelope.lrx()) + \
            ' ' + str(self._envelope.lry()) + \
            ' -projwin_srs' + \
            ' ' + LakeExtract.BBOX_SRS_EPSG + \
            ' -epo' + \
            ' -eco' + \
            ' -of GTiff' + \
            ' ' + maxExtentFilePath + \
            ' ' + maxExtentClippedFilePath

        SystemCommand(cmd, logger=self._logger, raiseException=True)

        return maxExtentClippedFilePath

    # -------------------------------------------------------------------------
    # _polygonizeLake()
    # -------------------------------------------------------------------------
    def _polygonizeLake(self, maxExtentClippedFilePath: str) -> str:
        """
        Take a clipped max extent and polygonize it.
        """
        polygonOutputFile = os.path.join(
            self._polygonDir,
            'Lake.{}.Polygonized.{}.shp'.format(self._lakeNumber,
                                                self._createStr))

        cmd = 'gdal_polygonize.py' + \
            ' ' + maxExtentClippedFilePath + \
            ' ' + polygonOutputFile + \
            ' -b 1' + \
            ' -f "ESRI Shapefile"' + \
            ' DN'

        SystemCommand(cmd, logger=self._logger, raiseException=True)

        return polygonOutputFile

    # -------------------------------------------------------------------------
    # _cleanPolygon()
    # -------------------------------------------------------------------------
    @staticmethod
    def _cleanPolygon(polygonOutputFile: str) -> str:
        """
        Clean polygons.
        """
        polygonLakesCleanedFilePath = polygonOutputFile.replace(
            'polygonized.shp', 'polygonized.cleaned.shp')
        polygonLakes = gpd.read_file(polygonOutputFile)
        polygonLakes = polygonLakes[polygonLakes['DN'] == 1]
        polygonLakes.to_file(polygonLakesCleanedFilePath)
        return polygonLakesCleanedFilePath

    # -------------------------------------------------------------------------
    # _createBuffer()
    # -------------------------------------------------------------------------
    def _createBuffer(self, polygonInputFile: str, outputBufferFilePath: str,
                      pixelResolution: str) -> str:
        """Creates a buffer of user defined extent around input shapefile."""
        inputds = ogr.Open(polygonInputFile)
        inputlyr = inputds.GetLayer()
        shpdriver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(outputBufferFilePath):
            shpdriver.DeleteDataSource(outputBufferFilePath)
        outputBufferds = shpdriver.CreateDataSource(outputBufferFilePath)
        bufferlyr = outputBufferds.CreateLayer(
            outputBufferFilePath, geom_type=ogr.wkbPolygon)
        featureDefn = bufferlyr.GetLayerDefn()

        for feature in inputlyr:
            ingeom = feature.GetGeometryRef()
            geomBuffer = ingeom.Buffer(pixelResolution)

            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(geomBuffer)
            bufferlyr.CreateFeature(outFeature)
            outFeature = None

        return outputBufferFilePath

    # -------------------------------------------------------------------------
    # dissolveBuffered()
    # -------------------------------------------------------------------------
    def _dissolveBuffered(self, inputBufferFilePath: str) -> str:
        """
        Dissolves polygonized water bodies based off of geometries if more
        than one water body present.
        """
        dissolvedPolygonOutputPath = os.path.join(
            self._polygonDir,
            'Lake.{}.Dissolved.{}.shp'.format(self._lakeNumber,
                                              self._createStr))
        initialBufferedPolygon = gpd.read_file(inputBufferFilePath)
        if len(initialBufferedPolygon) > 1:
            LakeExtract._dissolve(inputBufferFilePath,
                                  dissolvedPolygonOutputPath)
        else:
            initialBufferedPolygon.to_file(dissolvedPolygonOutputPath)
        return dissolvedPolygonOutputPath

    # -------------------------------------------------------------------------
    # _dissolve()
    # -------------------------------------------------------------------------
    @staticmethod
    def _dissolve(initialBufferedPolygonPath: str,
                  dissolvedPolygonOutputPath: str,
                  overwrite: bool = True) -> None:
        """
        Built to be used with createDS. Dissolves shapefile based on geometry.
        """
        ds = ogr.Open(initialBufferedPolygonPath)
        lyr = ds.GetLayer()
        out_ds, out_lyr = LakeExtract._createDS(dissolvedPolygonOutputPath,
                                                ds.GetDriver().GetName(),
                                                lyr.GetGeomType(),
                                                lyr.GetSpatialRef(),
                                                overwrite)
        defn = out_lyr.GetLayerDefn()
        multi = ogr.Geometry(ogr.wkbMultiPolygon)
        for feat in lyr:
            if feat.geometry():
                # This copies the first point to the end.
                feat.geometry().CloseRings()
                wkt = feat.geometry().ExportToWkt()
                multi.AddGeometryDirectly(ogr.CreateGeometryFromWkt(wkt))
        union = multi.UnionCascaded()
        if union.GetGeometryName() == 'MULTIPOLYGON':
            for geom in union:
                poly = ogr.CreateGeometryFromWkb(geom.ExportToWkb())
                feat = ogr.Feature(defn)
                feat.SetGeometry(poly)
                out_lyr.CreateFeature(feat)
        else:
            out_feat = ogr.Feature(defn)
            out_feat.SetGeometry(union)
            out_lyr.CreateFeature(out_feat)
            out_ds.Destroy()
        ds.Destroy()

    # -------------------------------------------------------------------------
    # createDS()
    # -------------------------------------------------------------------------
    @staticmethod
    def _createDS(ds_name, ds_format, geom_type, srs, overwrite=True) -> \
            Tuple[ogr.DataSource, ogr.Layer]:
        """
        Credit: s6hebern on StackExchange.
        Converts the polygon shapefile to an iterable DS.
        """
        drv = ogr.GetDriverByName(ds_format)
        if os.path.exists(ds_name) and overwrite is True:
            os.remove(ds_name)
        ds = drv.CreateDataSource(ds_name)
        lyr_name = os.path.splitext(os.path.basename(ds_name))[0]
        lyr = ds.CreateLayer(lyr_name, srs, geom_type)
        return ds, lyr

    # -------------------------------------------------------------------------
    # _getTargetLake()
    # -------------------------------------------------------------------------
    def _getTargetLake(self, dissolvedPolygonInput: str) -> str:
        """
        Get the largest water body in the dissolved polygon DF.
        """
        targetLakeFilePath = os.path.join(
            self._polygonDir,
            'Lake.{}.CenteredPolygon.{}.gpkg'.format(self._lakeNumber,
                                                     self._createStr)
        )
        targetLakeDF = gpd.read_file(dissolvedPolygonInput)
        targetLakeDF['area'] = targetLakeDF['geometry'].area
        if len(targetLakeDF) > 1:
            targetLakeDF = targetLakeDF[targetLakeDF['area']
                                        == targetLakeDF['area'].max()]
        targetLakeDF.to_file(targetLakeFilePath, driver='GPKG')
        return targetLakeFilePath

    # -------------------------------------------------------------------------
    # _extractLakePerYear()
    # -------------------------------------------------------------------------
    def _extractLakePerYear(self, mod44wList: list,
                            finalBufferedPolyInput: str) -> None:
        """
        For each MOD44W product in the year range, output the final buffered
        product.
        """
        outputList = []
        for mod44wFilePath in mod44wList:
            if self._logger:
                self._logger.debug(
                    'Extracting for ' +
                    '{}'.format(os.path.basename(mod44wFilePath)))
            year = os.path.basename(mod44wFilePath).split('.')[1][1:5]
            subdatasetName = gdal.Open(mod44wFilePath).GetSubDatasets()[0][0]
            bufferedLakeFilePath = os.path.join(
                self._bufferedDir,
                'Lake.{}.{}.{}.tif'.format(self._lakeNumber, year,
                                           self._createStr))
            cmd = 'gdalwarp' + \
                ' -overwrite' + \
                ' -of GTiff' + \
                ' -cutline' + \
                ' ' + finalBufferedPolyInput + \
                ' -crop_to_cutline' + \
                ' -dstnodata 3.0' + \
                ' ' + subdatasetName + \
                ' ' + bufferedLakeFilePath

            SystemCommand(cmd, raiseException=True)

            xmin = str(self._envelope.ulx())
            xmax = str(self._envelope.lrx())
            ymin = str(self._envelope.lry())
            ymax = str(self._envelope.uly())

            finalLakePath = os.path.join(
                self._finalBufferedDir,
                'lake_{}_MOD44W_{}_C6.tif'.format(self._lakeNumber,
                                                  year))

            cmd = 'gdalwarp' + \
                ' -overwrite' + \
                ' -of GTiff' + \
                ' -te ' + \
                ' ' + xmin + \
                ' ' + ymin + \
                ' ' + xmax + \
                ' ' + ymax + \
                ' -te_srs' + \
                ' ' + LakeExtract.BBOX_SRS_EPSG + \
                ' -t_srs' + \
                ' ' + LakeExtract.MOD_SRS + \
                ' -tr' + \
                ' ' + str(LakeExtract.TR_P) + \
                ' ' + str(LakeExtract.TR_N) + \
                ' -dstnodata 3.0' + \
                ' ' + bufferedLakeFilePath + \
                ' ' + finalLakePath

            SystemCommand(cmd, logger=self._logger, raiseException=True)

            outputList.append(finalLakePath)
            if self._logger:
                self._logger.info('Generated {}'.format(finalLakePath))

    # -------------------------------------------------------------------------
    # _rmOutputDirs()
    # -------------------------------------------------------------------------
    def _rmOutputDirs(self) -> None:
        """
        Creates the output directories.
        """
        shutil.rmtree(self._mod44wDir)
        shutil.rmtree(self._maxExtentDir)
        shutil.rmtree(self._polygonDir)
        shutil.rmtree(self._bufferedDir)

    # -------------------------------------------------------------------------
    # _getPostStr()
    # -------------------------------------------------------------------------
    @staticmethod
    def _getPostStr() -> str:
        sdtdate = datetime.datetime.now()
        year = sdtdate.year
        hm = sdtdate.strftime('%H%M')
        sdtdate = sdtdate.timetuple()
        jdate = sdtdate.tm_yday
        post_str = '{}{:03}{}'.format(year, jdate, hm)
        return post_str
