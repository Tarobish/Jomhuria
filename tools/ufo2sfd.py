#! /usr/bin/env python

import sys
import fontforge
font = fontforge.open(sys.argv[1])
font.save(sys.argv[2])
