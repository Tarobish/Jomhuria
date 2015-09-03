#! /usr/bin/env python

# This is pretty much a one time script to subset a merged version of
# Jomhuria that I got from Eben. It separates the glyphs that belong to the
# latin design from the arabic stuff in that font.
# I make the filter work for this case, it may likely fail for other cases.
# with docker/fontbuilder:
# sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && ./tools/subsetLatinFromMergedUFO.py sources/merged-with-latin.ufo sources/jomhuria.sfdir"; sudo chown -R $USER:$USER .

import sys
import os
import re
#from sortsmill import ffcompat as fontforge
import fontforge

from ufoLib import UFOReader, UFOWriter
from ufoLib.glifLib import Glyph

def isValid(name):
    """ Return true if a name should remain in the latin font.

        This blocks have been removed from the existing font in the meantime:
        'Arabic Presentation Forms-A': From 	U+FB50 to U+FDFF
        'Arabic Presentation Forms-B': From 	U+FE70 To 	U+FEFF

        some names got created by the built process, they look like
        "uni076A.medi_KafLamAlf.ref1" we want to filter these
        'Arabic' From 	U+0600 To 	U+06FF
        'Arabic Supplement' From 	U+0750 To 	U+077F

        These are in both fonts but not desired in the arabic:
        'Arabic Extended-A' From 	U+08A0 To 	U+08FF
    """

    # we don't have these in our latin
    if re.match('^u[0-9a-f]{5}$', name, flags=re.IGNORECASE):
        return False
    for pre in ['aKaf', 'aHeh', 'aMem', 'aBaa', 'aYaa', 'aAlf'
              , 'aFaa', 'aLam', 'aTaa', 'hamza', 'aHaa', 'aWaw'
              , 'aSad', 'aAyn', 'aQaf', 'aNon', 'aGaf', 'aSen'
              , 'aRaa', 'aDal'
              , 'FourDots', 'hThreeDots', 'ThreeDots', 'dash.gaf.alt2'
              , 'Dot', 'TwoDots', 'vTwoDots', 'iThreeDots', 'dotbelowcomb'
              , 'dot.'
              , 'smallv', 'smalltaa', 'damma', 'ring.below', 'aTwo.above'
              , 'dash.gaf', 'twostrokes.below']:
        if name.startswith(pre):
            return False
        #we use 'fi' and 'fl' instead
        if name in ('f_i', 'f_l'):
            return False;
    if not name.startswith('uni'):
        return True;

    uni = fontforge.unicodeFromName(name[:len('uniXXXX')])

    if 0xFB50 <= uni <= 0xFDFF \
            or 0xFE70 <= uni <= 0xFEFF \
            or 0x0600 <= uni <= 0x06FF \
            or 0x0750 <= uni <= 0x077F \
            or 0x08A0 <= uni <= 0x08FF:
        return False

    # print 'kept uni name:', name;
    return True

if __name__ == '__main__':
    # opened with ufoLib
    sourceFontPath = sys.argv[1]
    # suppose this is a fontforge format, it will be opened with the
    # fontforge api
    existingFontPath = sys.argv[2]

    sourceReader = UFOReader(sourceFontPath)
    sourceGlyphSet = sourceReader.getGlyphSet()
    sourceGlyphNames = set(sourceGlyphSet.keys())

    existingFont = fontforge.open(existingFontPath)
    existingGlyphNames = set(existingFont.__iter__())

    justInSource = sourceGlyphNames - existingGlyphNames
    # print 'glyphs in both:', sourceGlyphNames & existingGlyphNames
    # print 'glyphs only in source:', justInSource

    filtered = [name for name in justInSource if isValid(name)]
    overlapping = [name for name in (sourceGlyphNames & existingGlyphNames) if isValid(name)]
    print 'from the latin and valid:', sorted(filtered)
    print '------------------'
    print 'overlapping and valid', sorted(overlapping)


    writer = UFOWriter('sources/jomhuria-latin.ufo', formatVersion=2)
    newGlypsSet = writer.getGlyphSet()


    for glyphName in filtered + overlapping:
        # note how incestuous Glyph and GlyphSet interact.
        glyph = Glyph(glyphName, sourceGlyphSet)
        # this reads just the attributes
        sourceGlyphSet.readGlyph(glyphName, glyph)
        newGlypsSet.writeGlyph(
                      glyphName
                    , glyphObject=glyph
                    , drawPointsFunc=glyph.drawPoints
                )

    # after writing glyphs write the contents.plist
    newGlypsSet.writeContents()
    # affects only ufo version >= 3
    writer.writeLayerContents()

    # let's also copy fontinfo.plist
    class Info(object):
        pass
    info = Info()
    sourceReader.readInfo(info)
    writer.writeInfo(info)

