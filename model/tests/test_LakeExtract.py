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

    # -------------------------------------------------------------------------
    # testInit
    # -------------------------------------------------------------------------
    def testInit(self):
        with self.assertRaises(RuntimeError):
            LakeExtract(outDir='doesnotexistdir',
                        bbox=['12', '20', '12.5', '20.5'],
                        lakeNumber='772',
                        startYear=2001,
                        endYear=2015)
