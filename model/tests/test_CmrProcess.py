import unittest

from birkett_lake_extract.model.CmrProcess import CmrProcess


# -----------------------------------------------------------------------------
# class CmrProcessTestCase
#
# export PYTHONPATH="$PWD:$PWD/core:$PWD/lake_extract"
# python -m unittest discover model/tests/
# python -m unittest model.tests.test_CmrProcess.py
# -----------------------------------------------------------------------------
class CmrProcessTestCase(unittest.TestCase):

    mission = 'MOD44W'
    bbox = "-111.72,36.765,-109.97,38.079"
    bad_bbox_lon_min = "-181.72,36.765,-109.97,38.079"
    bad_bbox_lon_max = "-111.72,36.765,185.97,38.079"
    bad_bbox_lat_min = "-111.72,-96.765,-109.97,38.079"
    bad_bbox_lat_max = "-111.72,36.765,-109.97,97.079"
    dateRange = '2001-01-01T00:00:00Z,2001-12-30T23:59:59Z'

    # -------------------------------------------------------------------------
    # testLonMinValidate
    # -------------------------------------------------------------------------
    def testLonMinValidate(self):
        with self.assertRaises(RuntimeError):
            CmrProcess(mission=self.mission,
                       dateTime=self.dateRange,
                       lonLat=self.bad_bbox_lon_min)

    # -------------------------------------------------------------------------
    # testLonMaxValidate
    # -------------------------------------------------------------------------
    def testLonMaxValidate(self):
        with self.assertRaises(RuntimeError):
            CmrProcess(mission=self.mission,
                       dateTime=self.dateRange,
                       lonLat=self.bad_bbox_lon_max)

    # -------------------------------------------------------------------------
    # testLatMinValidate
    # -------------------------------------------------------------------------
    def testLatMinValidate(self):
        with self.assertRaises(RuntimeError):
            CmrProcess(mission=self.mission,
                       dateTime=self.dateRange,
                       lonLat=self.bad_bbox_lat_min)

    # -------------------------------------------------------------------------
    # testLatMaxValidate
    # -------------------------------------------------------------------------
    def testLatMaxValidate(self):
        with self.assertRaises(RuntimeError):
            CmrProcess(mission=self.mission,
                       dateTime=self.dateRange,
                       lonLat=self.bad_bbox_lat_max)

    # -------------------------------------------------------------------------
    # testRun
    # -------------------------------------------------------------------------
    def testRun(self):
        cmrRequestViirs = CmrProcess(mission=self.mission,
                                     dateTime=self.dateRange,
                                     lonLat=self.bbox)
        cmrRequestViirs.run()
