#! /usr/bin/env python
import sys
from defcon import Font
from ufo2fdk.kernFeatureWriter import KernFeatureWriter

font = Font(path=sys.argv[1])
kfw = KernFeatureWriter(font)
print kfw.write()
