import json
from typing import Tuple
import warnings

import certifi
import urllib3
from urllib.parse import urlencode


# -----------------------------------------------------------------------------
# class CmrProcess
#
# @author: Caleb Spradlin, caleb.s.spradlin@nasa.gov
# @version: 12.30.2021
#
# https://cmr.earthdata.nasa.gov/search/
# https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
# -----------------------------------------------------------------------------
class CmrProcess(object):

    CMR_BASE_URL = 'https://cmr.earthdata.nasa.gov' +\
        '/search/granules.umm_json_v1_4?'

    # Range for valid lon/lat
    LATITUDE_RANGE = (-90, 90)
    LONGITUDE_RANGE = (-180, 180)

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self,
                 mission,
                 dateTime,
                 lonLat=None,
                 error=False,
                 dayNightFlag='',
                 logger=None) -> None:

        self._error = error
        self._dateTime = dateTime
        self._mission = mission
        self._pageSize = 150
        self._maxPages = 50
        self._logger = logger

        self._lonLat = lonLat
        self._dayNightFlag = dayNightFlag

    # -------------------------------------------------------------------------
    # run()
    # -------------------------------------------------------------------------
    def run(self) -> list:
        """
        Given a set of parameters on init (time, location, mission), search for
        the most relevant file. This uses CMR to search metadata for
        relevant matches.
        """
        if self._logger:
            self._logger.debug('Starting CMR query')
        outout = set()
        for i in range(self._maxPages):

            d, e = self._cmrQuery(pageNum=i+1)

            if e and i > 1:
                return sorted(list(outout))

            if not e:
                if self._logger:
                    self._logger.debug('Results found on page: {}'.format(i+1))
                out = [r['file_url'] for r in d.values()]
                outout.update(out)

        outout = sorted(list(outout))
        return outout

    # -------------------------------------------------------------------------
    # cmrQuery()
    # -------------------------------------------------------------------------
    def _cmrQuery(self, pageNum: int = 1) -> Tuple[dict, bool]:
        """
        Search the Common Metadata Repository(CMR) for a file that
        is a temporal and spatial match.
        """
        requestDictionary = self._buildRequest(pageNum=pageNum)
        totalHits, resultDictionary = self._sendRequest(requestDictionary)

        if self._error:
            return None, self._error

        if totalHits <= 0:
            if self._logger:
                self._logger.debug('No hits on page number:' +
                                   ' {}, ending search.'.format(pageNum))
            return None, True

        resultDictionaryProcessed = self._processRequest(resultDictionary)
        return resultDictionaryProcessed, self._error

    # -------------------------------------------------------------------------
    # buildRequest()
    # -------------------------------------------------------------------------
    def _buildRequest(self, pageNum: int = 1) -> dict:
        """
        Build a dictionary based off of parameters given on init.
        This dictionary will be used to encode the http request to search CMR.
        """
        requestDict = dict()
        requestDict['page_num'] = pageNum
        requestDict['page_size'] = self._pageSize
        requestDict['short_name'] = self._mission
        requestDict['bounding_box'] = self._lonLat
        requestDict['day_night_flag'] = self._dayNightFlag
        requestDict['temporal'] = self._dateTime
        return requestDict

    # -------------------------------------------------------------------------
    # _sendRequest
    # -------------------------------------------------------------------------
    def _sendRequest(self, requestDictionary: dict) -> Tuple[int, bool]:
        """
        Send an http request to the CMR server.
        Decode data and count number of hits from request.
        """
        with urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                 ca_certs=certifi.where()) as httpPoolManager:
            encodedParameters = urlencode(requestDictionary, doseq=True)
            requestUrl = self.CMR_BASE_URL + encodedParameters
            if self._logger:
                self._logger.debug(requestUrl)
            try:
                requestResultPackage = httpPoolManager.request('GET',
                                                               requestUrl)
            except urllib3.exceptions.MaxRetryError:
                self._error = True
                return 0, None

            requestResultData = json.loads(
                requestResultPackage.data.decode('utf-8'))
            status = int(requestResultPackage.status)

            if not status == 400:
                totalHits = len(requestResultData['items'])
                return totalHits, requestResultData

            else:
                msg = 'CMR Query: Client or server error: ' + \
                    'Status: {}, Request URL: {}, Params: {}'.format(
                        str(status), requestUrl, encodedParameters)
                warnings.warn(msg)
                return 0, None

    # -------------------------------------------------------------------------
    # _processRequest
    # -------------------------------------------------------------------------
    def _processRequest(self, resultDict: dict) -> dict:
        """
        For each result in the CMR query, unpackage relevant information to
        a dictionary. While doing so set flags if data is not desirable (too
        close to edge of dataset).
        """
        resultDictProcessed = dict()

        for hit in resultDict['items']:

            fileName = hit['umm']['RelatedUrls'][0]['URL'].split(
                '/')[-1]

            # ---
            # These are hardcoded here because the only time these names will
            # ever change is if we changed which format of metadata we wanted
            # the CMR results back in.
            #
            # These could be placed as class constants in the future.
            # ---
            fileUrl = hit['umm']['RelatedUrls'][0]['URL']
            temporalRange = hit['umm']['TemporalExtent']['RangeDateTime']
            dayNight = hit['umm']['DataGranule']['DayNightFlag']

            spatialExtent = hit['umm']['SpatialExten' +
                                       't']['HorizontalSpatialDom' +
                                            'ain']

            key = fileName

            resultDictProcessed[key] = {
                'file_name': fileName,
                'file_url': fileUrl,
                'temporal_range': temporalRange,
                'spatial_extent': spatialExtent,
                'day_night_flag': dayNight}

        return resultDictProcessed
