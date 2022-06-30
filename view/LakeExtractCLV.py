#!/usr/bin/python
import argparse
import logging
import sys

from birkett_lake_extract.model.LakeExtract import LakeExtract


# -------------------------------------------------------------------------
# main()
#
# Use this application to generate buffered lake water masks from bounding
# boxes and MOD44W products.
#
# Ex.
# python -o . -start 2001 -end 2015 -lakename Nzilo \
#   -bbox 5.3 -11.15 26.22 -10.32
# -------------------------------------------------------------------------
def main() -> None:

    desc = 'Use this application to generate buffered ' + \
        'lake water masks from bounding boxes and MOD44W products.'

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')

    parser.add_argument('-start',
                        default=2001,
                        type=int,
                        help='Starting year.')

    parser.add_argument('-end',
                        default=2015,
                        type=int,
                        help='Ending year.')

    parser.add_argument('-lakename',
                        required=True,
                        type=str,
                        help='Name of the lake to process. ' +
                        'One word, no special characters.')

    parser.add_argument('-bbox',
                        required=True,
                        nargs='+',
                        help='Space separated bbox values following format' +
                        ' <lon min> <lat min> <lon max> <lat max>\n' +
                        'Ex. 13.2 46.1 14.0 47.0',)

    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s; %(levelname)s; %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    lakeExtract = LakeExtract(outDir=args.o,
                              bbox=args.bbox,
                              lakeName=args.lakename,
                              startYear=args.start,
                              endYear=args.end,
                              logger=logger)

    lakeExtract.extractLakes()


# -----------------------------------------------------------------------------
# Invoke the main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
