#!/usr/bin/env python
# coding=utf-8
#
# build.py - Amiri font build utility
#
# Written in 2010-2012 by Khaled Hosny <khaledhosny@eglug.org>
#
# To the extent possible under law, the author have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

script_lang = (('latn', ('dflt', 'TRK ')), ('arab', ('dflt', 'ARA ', 'URD ', 'SND ')), ('DFLT', ('dflt',)))

from sortsmill import ffcompat as fontforge
from sortsmill import psMat
import sys
import os
from tempfile import mkstemp
from string import Template
import defcon
from booleanOperations.booleanGlyph import BooleanGlyph
from fontTools.ttLib import TTFont
from ufoLib import UFOReader
from robofab.pens.boundsPen import ControlBoundsPen


def cleanAnchors(font):
    """Removes anchor classes (and associated lookups) that are used only
    internally for building composite glyph."""

    klasses = (
            "Dash",
            "DigitAbove",
            "DigitBelow",
            "DotAbove",
            "DotAlt",
            "DotBelow",
            "DotBelowAlt",
            "DotHmaza",
            "HighHamza",
            "MarkDotAbove",
            "MarkDotBelow",
            "RingBelow",
            "RingDash",
            "Stroke",
            "TaaAbove",
            "TaaBelow",
            "Tail",
            "TashkilAboveDot",
            "TashkilBelowDot",
            "TwoDotsAbove",
            "TwoDotsBelow",
            "TwoDotsBelowAlt",
            "VAbove",
            )

    for klass in klasses:
        subtable = font.getSubtableOfAnchor(klass)
        lookup = font.getLookupOfSubtable(subtable)
        font.removeLookup(lookup)

def flattenNestedReferences(font, ref, new_transform=(1, 0, 0, 1, 0, 0)):
    """Flattens nested references by replacing them with the ultimate reference
    and applying any transformation matrices involved, so that the final font
    has only simple composite glyphs. This to work around what seems to be an
    Apple bug that results in ignoring transformation matrix of nested
    references."""

    name = ref[0]
    transform = ref[1]
    glyph = font[name]
    new_ref = []
    if glyph.references and glyph.foreground.isEmpty():
        for nested_ref in glyph.references:
            for i in flattenNestedReferences(font, nested_ref, transform):
                matrix = psMat.compose(i[1], new_transform)
                new_ref.append((i[0], matrix))
    else:
        matrix = psMat.compose(transform, new_transform)
        new_ref.append((name, matrix))

    return new_ref

def validateGlyphs(font):
    """Fixes some common FontForge validation warnings, currently handles:
        * wrong direction
        * flipped references
    In addition to flattening nested references."""

    wrong_dir = 0x8
    flipped_ref = 0x10
    for glyph in font.glyphs():
        state = glyph.validate(True)
        refs = []

        if state & flipped_ref:
            glyph.unlinkRef()
            glyph.correctDirection()
        if state & wrong_dir:
            glyph.correctDirection()

        for ref in glyph.references:
            for i in flattenNestedReferences(font, ref):
                refs.append(i)
        if refs:
            glyph.references = refs

        glyph.round()

        # Hack, OTS rejects ligature carets!
        glyph.lcarets = ()

def setVersion(font, version):
    font.version = '{0:.4f}'.format(float(version))
    for name in font.sfnt_names:
        if name[0] == "Arabic (Egypt)" and name[1] == "Version":
            font.appendSFNTName(name[0], name[1],
                                name[2].replace("VERSION", font.version.replace(".", "\xD9\xAB")))


def extractGPOSData(font):
    """extracts and removes feature data from the fontforge file
       returns the extracted fea string
    """
    oldfea = font.generateFeatureString()

    # clean up, we will insert this into the new feature file
    for lookup in font.gpos_lookups:
        font.removeLookup(lookup)

    for lookup in font.gsub_lookups:
        font.removeLookup(lookup)

    return oldfea

def makeCollisionPrevention():
    """
    In order to prevent collisions we insert a widening glyph between
    glyphs where collisions happen.

    This is done by first spotting the colliding pair and then, in the
    actual substitution we can decompose the first glyph into the first
    glyph plus the widening glyph, using a "[GSUB LookupType 2] Multiple substitution".
    """
    firstBelow = [
        'uni0680.init'
      , 'uni0776.init'
      , 'uni06CE.init'
      , 'uni0775.init'
      , 'uni06BD.init'
      , 'uni064A.init'
      , 'uni067E.init'
      , 'uni0753.init'
      , 'uni0752.init'
      , 'uni063D.init'
      , 'uni0754.init'
      , 'uni06D1.init'
      , 'uni06CC.init'
      , 'uni0767.init'
      , 'uni0680.medi'
      , 'uni0776.medi'
      , 'uni0750.medi'
      , 'uni06CE.medi'
      , 'uni0775.medi'
      , 'uni06BD.medi'
      , 'uni064A.medi'
      , 'uni067E.medi'
      , 'uni0753.medi'
      , 'uni0752.medi'
      , 'uni063D.medi'
      , 'uni0754.medi'
      , 'uni06D1.medi'
      , 'uni06CC.medi'
      , 'uni0767.medi'
      , 'uni0680.init_High'
      , 'uni0776.init_High'
      , 'uni0750.init_High'
      , 'uni06CE.init_High'
      , 'uni0775.init_High'
      , 'uni06BD.init_High'
      , 'uni064A.init_High'
      , 'uni067E.init_High'
      , 'uni0753.init_High'
      , 'uni0752.init_High'
      , 'uni063D.init_High'
      , 'uni0754.init_High'
      , 'uni06D1.init_High'
      , 'uni06CC.init_High'
      , 'uni0767.init_High'
      , 'uni0680.medi_High'
      , 'uni0776.medi_High'
      , 'uni0750.medi_High'
      , 'uni06CE.medi_High'
      , 'uni0775.medi_High'
      , 'uni06BD.medi_High'
      , 'uni064A.medi_High'
      , 'uni067E.medi_High'
      , 'uni0753.medi_High'
      , 'uni0752.medi_High'
      , 'uni063D.medi_High'
      , 'uni0754.medi_High'
      , 'uni06D1.medi_High'
      , 'uni06CC.medi_High'
      , 'uni0767.medi_High'
      , 'uni064A.init_BaaYaaIsol'
      , 'u1EE29'
    ]
    firstAbove = [
        'uni0753.init'
      , 'uni0751.init'
      , 'uni067D.init'
      , 'uni067F.init'
      , 'uni067C.init'
      , 'uni062B.init'
      , 'uni062A.init'
    ]

    firstAboveQaf = [
        'uni0642.init'
      , 'uni06A8.init'
      , 'uni06A4.init'
      , 'uni06A6.init'
    ]

    widener = 'uni0640.1'
    multipleSubstitution = 'sub {name} by {name} {widener};'
    decompositions = []
    seen = set()
    for name in firstBelow + firstAbove + firstAboveQaf:
        if name in seen:
            continue
        seen.add(name)
        decompositions.append(multipleSubstitution.format(name=name, widener=widener))

    template = Template("""
@colisionsBelowFirst = [ $firstBelow ];
@colisionsAboveFirst = [ $firstAbove ];
@colisionsAboveFirstQaf = [ $firstAboveQaf ];

lookup decompCollisions {
  lookupflag IgnoreMarks;
  $decompositions
} decompCollisions;
""")

    return '\n'.join([
        template.substitute(
            firstBelow=' '.join(firstBelow)
          , firstAbove=' '.join(firstAbove)
          , firstAboveQaf=' '.join(firstAboveQaf)
          , decompositions='\n  '.join(decompositions)
        )
      , preventCollisionsBelow()
      , preventCollisionsBelowAlefMark()
      , preventCollisionsAbove()
      , preventCollisionsAboveLamMediAlfFina()
      , preventCollisionsAboveQafIniAlfMaddaFina()
    ])

def preventCollisionsBelow():
    template = Template("""
@colisionsBelowSecond =[ $second ];

feature calt {
  lookup comp {
    lookupflag IgnoreMarks;
    sub @colisionsBelowFirst' lookup decompCollisions @colisionsBelowSecond;
  } comp;
} calt;
""")

    second = [
        'uni0647.medi'
      , 'uni06C1.medi'
      , 'uni0777.fina'
      , 'uni06D1.fina'
      , 'uni0775.fina'
      , 'uni063F.fina'
      , 'uni0678.fina'
      , 'uni063D.fina'
      , 'uni063E.fina'
      , 'uni06D0.fina'
      , 'uni0649.fina'
      , 'uni0776.fina'
      , 'uni06CD.fina'
      , 'uni06CC.fina'
      , 'uni0626.fina'
      , 'uni0620.fina'
      , 'uni064A.fina'
      , 'uni06CE.fina'
      , 'uni077B.fina'
      , 'uni077A.fina'
      , 'uni06D2.fina'
      , 'uni06FF.medi'
      , 'uni077B.fina_PostToothFina'
      , 'uni077A.fina_PostToothFina'
      , 'uni06D2.fina_PostToothFina'
      , 'uni0625.fina'
      , 'uni0673.fina'
    ]

    return template.substitute(second=' '.join(second));

def preventCollisionsBelowAlefMark():
    # TODO: instead of @colisionsBelowMarks could we use @tashkilBelow???
    template = Template("""
@colisionsBelowSecondAlefs =[ $alefs ];
@colisionsBelowMarks =[ $marks ];

feature calt {
  lookup comp {
    sub @colisionsBelowFirst' lookup decompCollisions @colisionsBelowSecondAlefs @colisionsBelowMarks;
  } comp;
} calt;
""")
    alefs = [
        'uni0627.fina' # ARABIC LETTER ALEF the normal alef.fina as used in kashida.fea we get there we are done
          # several alef combinations
      , 'uni0625.fina' # ARABIC LETTER ALEF WITH HAMZA BELOW ≡ 0627 0655    basics.fea sub uni0625 by uni0627.fina uni0655;
      , 'uni0774.fina' # ARABIC LETTER ALEF WITH EXTENDED ARABIC-INDIC DIGIT THREE ABOVE
      , 'uni0773.fina' # ARABIC LETTER ALEF WITH EXTENDED ARABIC-INDIC DIGIT TWO ABOVE
      , 'uni0623.fina' # ARABIC LETTER ALEF WITH HAMZA ABOVE ≡ 0627 0654
      , 'uni0622.fina' # ARABIC LETTER ALEF WITH MADDA ABOVE ≡ 0627 0653
      , 'uni0675.fina' # ARABIC LETTER HIGH HAMZA ALE ≈ 0627 + 0674
      , 'uni0672.fina' # ARABIC LETTER ALEF WITH WAVY HAMZA ABOVE

          # should be entered as \u0627 \u065F. if I enter this directly
          # \u0673 (which is discouraged by unicode, wwhbd what will harfbuzz do?)
          # "this character is deprecated and its use is strongly discouraged"
          # if it is normalized to \u0627 \u065F this will be easy
      , 'uni0673.fina' # ARABIC LETTER ALEF WITH WAVY HAMZA BELOW
      , 'uni0671.fina' # ARABIC LETTER ALEF WASLA with an alef above, Koranic Arabic

      , 'u1EE6F'
    ]
    marks = [
        'uni0655'
      , 'uni064D', 'uni08F2', 'uni064D.small' # TODO: remove .small ?
      , 'uni065F'
      , 'uni0650' , 'uni0650.small' , 'uni0650.small2'# TODO: remove .small .small2 ?
      , 'uni0656'
      , 'uni061A'
      , 'uni06ED'
      , 'uni065C'
      , 'uni0325'
      , 'uni08E6'
      , 'uni08E9'
    ]

    alefs = ' '.join(alefs)
    marks = ' '.join(marks)
    return template.substitute(alefs=alefs, marks=marks);

def preventCollisionsAbove():
    template = Template("""
@colisionsAboveSecond =[ $second ];

feature calt {
  lookup comp {
    lookupflag IgnoreMarks;
    sub @colisionsAboveFirst' lookup decompCollisions @colisionsAboveSecond;
  } comp;
} calt;
""")

    second = [
        'uni0625.fina'
      , 'uni0627.fina'
      , 'uni0774.fina'
      , 'uni0773.fina'
      , 'uni0623.fina'
      , 'uni0622.fina'
      , 'uni0675.fina'
      , 'uni0672.fina'
      , 'uni0673.fina'
      , 'uni0671.fina'
    ]
    return template.substitute(second=' '.join(second));


def preventCollisionsAboveLamMediAlfFina():

    template = Template("""
feature calt {
  lookup comp {
    lookupflag IgnoreMarks;
    sub @colisionsAboveFirst' lookup decompCollisions @aLam.medi_LamAlfFina;
  } comp;
} calt;
""")
    # this is the same group as @aLam.medi_LamAlfFina
    # we use that name and don't recreate it below
    #second = [
    #    'uni076A.medi_LamAlfFina'
    #  , 'uni06B6.medi_LamAlfFina'
    #  , 'uni06B8.medi_LamAlfFina'
    #  , 'uni0644.medi_LamAlfFina'
    #  , 'uni06B7.medi_LamAlfFina'
    #  , 'uni06B5.medi_LamAlfFina'
    #]
    # second=' '.join(second)
    return template.substitute();

def preventCollisionsAboveQafIniAlfMaddaFina():

    # uni0622.fina ARABIC LETTER ALEF WITH MADDA ABOVE

    template = Template("""
feature calt {
  lookup comp {
    lookupflag IgnoreMarks;
    sub @colisionsAboveFirstQaf' lookup decompCollisions uni0622.fina;
  } comp;
} calt;
""")
    return template.substitute();


def prepareFeatures(font, feafile):
    """Merges feature file into the font while making sure mark positioning
    lookups (already in the font) come after kerning lookups (from the feature
    file), which is required by Uniscribe to get correct mark positioning for
    kerned glyphs."""

    # open feature file
    fea = open(feafile)
    fea_text = fea.read()
    fea.close()


    # insert the generated GPOS features in place of the placeholder text
    anchors = extractGPOSData(font)
    fea_text = fea_text.replace("{%anchors%}", anchors)

    collisonPrevention = makeCollisionPrevention()
    fea_text = fea_text.replace("{%collison-prevention%}", collisonPrevention)

    with open(feafile, 'w') as f:
        f.write(fea_text);

    # now merge it into the font
    font.mergeFeatureString(fea_text)

def mergeContours(glyph):
    # remember stuff that get's lost when drawing to a fontforge glyph
    width = glyph.width
    vwidth = glyph.vwidth
    anchorPoints = tuple(glyph.anchorPoints)

    # make a defcon glyph
    dcGlyph = defcon.Glyph()
    dcGlyphPen = dcGlyph.getPen()

    # draw to dcGlyph
    glyph.draw(dcGlyphPen)

    # union of dcGlyph
    result = BooleanGlyph(dcGlyph).removeOverlap()
    targetPen = glyph.glyphPen()
    result.draw(targetPen)

    # restore stuff that a pen should rather not change automagically
    # in fact, the pen should not reset anything besides outline and components.
    glyph.width = width
    glyph.vwidth = vwidth
    [glyph.addAnchorPoint(*p) for p in anchorPoints]

def generateTTF(font, outfile):
    flags  = ("opentype", "dummy-dsig", "round", "omit-instructions")
    font.generate(outfile, flags=flags)

def cleanTTF(ttfFile, outfile):
    # now open in fontTools
    ftfont = TTFont(ttfFile)

    # the ttf contains NAME table IDs with platformID="1", these should be removed
    name = ftfont['name']
    names = []
    for record in name.names:
        if record.platformID == 1:
            continue
        names.append(record)
    name.names = names

    # remove non-standard 'FFTM' the FontForge time stamp table
    del ftfont['FFTM'];

    # force compiling tables by fontTools, saves few tens of KBs
    for tag in ftfont.keys():
        if hasattr(ftfont[tag], "compile"):
            ftfont[tag].compile(ftfont)

    ftfont.save(outfile)
    ftfont.close()

def generateFont(font, outfile):
    font.selection.all()
    font.correctReferences()
    font.selection.none()

    # fix some common font issues
    validateGlyphs(font)

    for name in font:
        mergeContours(font[name])

    tmpfile = os.path.join(os.path.dirname(outfile), '~tmp.ttf')
    generateTTF(font, tmpfile)
    cleanTTF(tmpfile, outfile)
    os.unlink(tmpfile)

def centerGlyph(glyph):
    width = glyph.width
    glyph.right_side_bearing = glyph.left_side_bearing = (glyph.right_side_bearing + glyph.left_side_bearing)/2
    glyph.width = width

def subsetFont(font, glyphnames, similar=False):
    # keep any glyph with the same base name
    reported = []

    if similar:
        for name in glyphnames:
            for glyph in font.glyphs():
                if "." in glyph.glyphname and glyph.glyphname.split(".")[0] == name:
                    glyphnames.append(glyph.glyphname)

    # keep any glyph referenced requested glyphs
    for name in glyphnames:
        if name in font:
            glyph = font[name]
            for ref in glyph.references:
                glyphnames.append(ref[0])
        else:
            if name not in reported:
                print 'Font ‘%s’ is missing glyph: %s' %(font.fontname, name)
                reported.append(name)

    # remove everything else
    for glyph in font.glyphs():
        if glyph.glyphname not in glyphnames:
            font.removeGlyph(glyph)

def buildComposition(font, glyphnames):
    newnames = []

    #dirty fix
    try:
        font.removeLookup("Latin composition");
    except EnvironmentError:
        pass
    font.addLookup("Latin composition", 'gsub_ligature', (), (('ccmp', script_lang),))
    font.addLookupSubtable("Latin composition", "Latin composition subtable")

    import unicodedata
    for name in glyphnames:
        u = fontforge.unicodeFromName(name)
        if 0 < u < 0xfb00:
            decomp = unicodedata.decomposition(unichr(u))
            if decomp:
                base = decomp.split()[0]
                mark = decomp.split()[1]
                if not '<' in base:
                    nmark = None
                    nbase = None

                    for g in font.glyphs():
                        if g.unicode == int(base, 16):
                            nbase = g.glyphname
                        if g.unicode == int(mark, 16):
                            nmark = g.glyphname

                    if not nbase:
                        nbase = "uni%04X" % int(base, 16)
                    if not nmark:
                        nmark = "uni%04X" % int(mark, 16)

                    if nbase in font and nmark in font:
                        font[name].addPosSub("Latin composition subtable", (nbase, nmark))

                    if base not in glyphnames:
                        newnames.append(nbase)
                    if mark not in glyphnames:
                        newnames.append(nmark)

    return newnames

def makeNumerators(font):
    digits = ("zero", "one", "two", "three", "four", "five", "six", "seven",
              "eight", "nine",
              "uni0660", "uni0661", "uni0662", "uni0663", "uni0664",
              "uni0665", "uni0666", "uni0667", "uni0668", "uni0669",
              "uni06F0", "uni06F1", "uni06F2", "uni06F3", "uni06F4",
              "uni06F5", "uni06F6", "uni06F7", "uni06F8", "uni06F9",
              "uni06F4.urd", "uni06F6.urd", "uni06F7.urd")
    for name in digits:
        numr = font.createChar(-1, name + ".numr")
        small = font[name + ".small"]
        if not numr.isWorthOutputting():
            numr.clear()
            numr.addReference(small.glyphname, psMat.translate(0, 550))
            numr.width = small.width

def simpleFontMerge(font, sourcefile):
    #sourcefont = fontforge.open(sourcefile)
    font.mergeFonts(sourcefile)


def copyAnchors(font, latinUFO):
    ufo = UFOReader(latinUFO)
    glyphset = ufo.getGlyphSet()
    # mark types are: "mark" "base" "ligature" "basemark" "entry" "exit"
    className2markType = {
            'MarkBelow': 'mark'
          , 'TashkilBelow': 'mark'
          , 'TashkilTashkilBelow': 'mark'
    }
    for name in glyphset.keys():
        if name not in font: continue
        glyph = glyphset[name]
        # need to draw to receive the data of the glyph and that ControlBoundsPen is harmless
        glyph.draw(ControlBoundsPen(glyphset))
        anchors = getattr(glyph,'anchors',None)
        if not anchors: continue
        ffglyph = font[name];
        for anchor in anchors:
            ffglyph.addAnchorPoint(anchor['name'], className2markType[anchor['name']],anchor['x'],anchor['y'])


def mergeLatin(font, latinfile, glyphs=None):
    tmpfont = mkstemp(suffix=os.path.basename(latinfile).replace("ufo", "sfd"))[1]
    latinfont = fontforge.open(latinfile)

    validateGlyphs(latinfont) # to flatten nested refs mainly
    latinglyphs = [name for name in latinfont]

    # The Latin font is already subsetted to only contain glyphs that take
    # precedence over glyphs in the Arabic if there are overlapping glyphs.
    # To give the glyphs of the latin precedence, we need to remove the
    # existing glyphs from the Arabic.
    overlapping = {name for name in font} & {name for name in latinfont}
    for name in overlapping:
        # Maybe font.removeGlyph(name) is the better strategy than font[name].clear()
        # As it seems that the newly merged glyphs don't set all properties
        # of the glyph new on font.mergeFonts(latin)
        # If there are no references, removeGlyph should be better (there
        # were none when writing this)
        font.removeGlyph(name)


    compositions = buildComposition(latinfont, latinglyphs)
    latinglyphs += compositions
    subsetFont(latinfont, latinglyphs)

    digits = ("zero", "one", "two", "three", "four", "five", "six", "seven",
              "eight", "nine")

    # copy kerning classes
    kern_lookups = {}
    for lookup in latinfont.gpos_lookups:
        kern_lookups[lookup] = {}
        kern_lookups[lookup]["subtables"] = []
        kern_lookups[lookup]["type"], kern_lookups[lookup]["flags"] = latinfont.getLookupInfo(lookup)[:2]
        for subtable in latinfont.getLookupSubtables(lookup):
            if latinfont.isKerningClass(subtable):
                kern_lookups[lookup]["subtables"].append((subtable, latinfont.getKerningClass(subtable)))

    for lookup in latinfont.gpos_lookups:
        latinfont.removeLookup(lookup)

    for lookup in latinfont.gsub_lookups:
        latinfont.removeLookup(lookup)

    latinfont.save(tmpfont)
    latinfont.close()

    font.mergeFonts(tmpfont)
    os.remove(tmpfont)

    copyAnchors(font, latinfile)

    buildComposition(font, latinglyphs)

    # add Latin small and medium digits
    for name in digits:
        refname = name
        small = font.createChar(-1, name + ".small")
        #if not small.isWorthOutputting():
        small.clear()
        small.addReference(refname, psMat.scale(0.6))
        small.transform(psMat.translate(0, 180))
        small.width = 650
        centerGlyph(small)

        medium = font.createChar(-1, name + ".medium")
        #if not medium.isWorthOutputting():
        medium.clear()
        medium.addReference(refname, psMat.scale(0.8))
        medium.transform(psMat.translate(0, 200))
        medium.width = 900
        centerGlyph(medium)

    for lookup in kern_lookups:
        font.addLookup(lookup,
                kern_lookups[lookup]["type"],
                kern_lookups[lookup]["flags"],
                (('kern', script_lang),)
                )

        for subtable in kern_lookups[lookup]["subtables"]:
            first = []
            second = []
            offsets = subtable[1][2]

            # drop non-existing glyphs
            for new_klasses, klasses in ((first, subtable[1][0]), (second, subtable[1][1])):
                for klass in klasses:
                    new_klass = []
                    if klass:
                        for name in klass:
                            if name in font:
                                new_klass.append(name)
                    new_klasses.append(new_klass)

            # if either of the classes is empty, don’t bother with the subtable
            if any(first) and any(second):
                font.addKerningClass(lookup, subtable[0], first, second, offsets)

def scaleGlyph(glyph, amount):
    """Scales the glyph, but keeps it centered around its original bounding
    box.

    Logic copied (and simplified for our simple case) from code of FontForge
    transform dialog, since that logic is not exported to Python interface."""
    bbox = glyph.boundingBox()
    x = (bbox[0] + bbox[2]) / 2
    y = (bbox[1] + bbox[3]) / 2
    move = psMat.translate(-x, -y)
    scale = psMat.scale(amount)

    matrix = list(scale)
    matrix[4] = move[4] * scale[0] + x;
    matrix[5] = move[5] * scale[3] + y;

    glyph.transform(matrix)

def makeDesktop(infile, outfile, latinfile, feafile, version, generate=True):
    font = fontforge.open(infile)
    font.encoding = "UnicodeFull" # avoid a crash if compact was set

    if version:
        setVersion(font, version)

    # remove anchors that are not needed in the production font
    cleanAnchors(font)

    mergeLatin(font, latinfile)
    #simpleFontMerge(font, latinfile)
    makeNumerators(font)

    # we want to merge features after merging the latin font because many
    # referenced glyphs are in the latin font
    prepareFeatures(font, feafile)


    if generate:
        generateFont(font, outfile)
    else:
        return font

def usage(extramessage, code):
    if extramessage:
        print extramessage

    message = """Usage: %s OPTIONS...

Options:
  --input=FILE          file name of input font
  --output=FILE         file name of output font
  --features=FILE       file name of features file
  --version=VALUE       set font version to VALUE

  -h, --help            print this message and exit
""" % os.path.basename(sys.argv[0])

    print message
    sys.exit(code)

if __name__ == "__main__":
    #if fontforge.version() < min_ff_version:
    #    print "You need FontForge %s or newer to build Amiri fonts" %min_ff_version
    #    sys.exit(-1)
    import getopt
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:],
                "h",
                ["help", "input=", "output=", "latin=", "features=", "version="])
    except getopt.GetoptError, err:
        usage(str(err), -1)

    infile = None
    outfile = None
    latinfile = None
    feafile = None
    version = None
    slant = False
    quran = False

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage("", 0)
        elif opt == "--input": infile = arg
        elif opt == "--output": outfile = arg
        elif opt == "--latin": latinfile = arg
        elif opt == "--features": feafile = arg
        elif opt == "--version": version = arg

    if not infile:
        usage("No input file specified", -1)
    if not outfile:
        usage("No output file specified", -1)

    if not version:
        usage("No version specified", -1)
    if not feafile:
        usage("No features file specified", -1)

    makeDesktop(infile, outfile, latinfile, feafile, version)
