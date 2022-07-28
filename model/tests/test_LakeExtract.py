import os
import shutil
import unittest

from birkett_lake_extract.model.LakeExtract import LakeExtract


# -----------------------------------------------------------------------------
# class LakeExtractTestCase
#
# export PYTHONPATH="$PWD:$PWD/core:$PWD/lake_extract"
# python -m unittest discover lake_extract/model/tests/
# python -m unittest lake_extract.model.tests.test_LakeExtract
# -----------------------------------------------------------------------------
class LakeExtractTestCase(unittest.TestCase):

    def testCreateAndDelete(self):
        leTest = LakeExtract(outDir='.',
                             bbox=['12', '20', '12.5', '20.5'],
                             lakeNumber='772',
                             startYear=2001,
                             endYear=2015)
        self.assertTrue(os.path.exists(leTest._mod44wDir))
        self.assertTrue(os.path.exists(leTest._maxExtentDir))
        self.assertTrue(os.path.exists(leTest._polygonDir))
        self.assertTrue(os.path.exists(leTest._bufferedDir))
        self.assertTrue(os.path.exists(leTest._finalBufferedDir))
        leTest._rmOutputDirs()
        self.assertFalse(os.path.exists(leTest._mod44wDir))
        self.assertFalse(os.path.exists(leTest._maxExtentDir))
        self.assertFalse(os.path.exists(leTest._polygonDir))
        self.assertFalse(os.path.exists(leTest._bufferedDir))
        self.assertTrue(os.path.exists(leTest._finalBufferedDir))
        shutil.rmtree(leTest._finalBufferedDir)
