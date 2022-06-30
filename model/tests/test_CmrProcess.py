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
    dateRange = '2001-01-01T00:00:00Z,2001-12-30T23:59:59Z'

    # -------------------------------------------------------------------------
    # testRun
    # -------------------------------------------------------------------------
    def testRun(self):
        cmrRequestViirs = CmrProcess(mission=self.mission,
                                     dateTime=self.dateRange,
                                     lonLat=self.bbox)
        cmrRequestViirs.run()
