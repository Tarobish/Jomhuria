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
    font.version = "%07.3f" % float(version)
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

def makeShortName(name, maxLen):
    """
    example:

    >>> makeShortName("uni064A.init_BaaYaaIsol_uni0640.1", 31)
    'uni064A.init_BaaYaaIsol_uni_AF2'

    """
    checksum = '_{0:X}'.format(sum([ord(c) for c in name]))
    return name[:maxLen-len(checksum)] + checksum;


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
      , 'uniFEF3'
      , 'u1EE29'
      , 'uniFB58'
      , 'uniFB5C'
      , 'uniFBFE'
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

    widener = 'uni0640.1'
    multipleSubstitution = 'sub {name} by {name} {widener};'
    decompositions = []
    seen = set()
    for name in firstBelow + firstAbove:
        if name in seen:
            continue
        seen.add(name)
        decompositions.append(multipleSubstitution.format(name=name, widener=widener))

    template = Template("""
@colisionsBelowFirst = [ $firstBelow ];
@colisionsAboveFirst = [ $firstAbove ];

lookup decompCollisions {
  lookupflag IgnoreMarks;
  $decompositions
} decompCollisions;
""")

    return '\n'.join([
        template.substitute(
            firstBelow=' '.join(firstBelow)
          , firstAbove=' '.join(firstAbove)
          , decompositions='\n  '.join(decompositions)
        )
      , preventCollisionsBelow()
      , preventCollisionsBelowAlefMark()
      , preventCollisionsAbove()
      , preventCollisionsAboveLamMediAlfFina()
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
      , 'uniFBA9'
      , 'uniFBAF'
      , 'uniFBE5'
      , 'uniFBFD'
      , 'uniFC10'
      , 'uniFC90'
      , 'uniFD17'
      , 'uniFD18'
      , 'uniFE8A'
      , 'uniFEF0'
      , 'uniFEF2'
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

          # I don't care much about these. Where these codepoints are used
          # advanced typographical features are not known or not wanted.
          # maybe we should remove mentioning of these in the feature files,
          # it is rather over engineering to support these.
      , 'uniFB51'
      , 'uniFE82'
      , 'uniFE84'
      , 'uniFE88'
      , 'uniFE8E'
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

def generateFont(font, outfile):
    flags  = ("opentype", "dummy-dsig", "round", "omit-instructions")

    font.selection.all()
    font.correctReferences()
    font.selection.none()

    # fix some common font issues
    validateGlyphs(font)

    tmpfile = mkstemp(suffix=os.path.basename(outfile))[1]
    font.generate(tmpfile, flags=flags)
    font.close()

    # now open in fontTools
    from fontTools.ttLib import TTFont
    ftfont = TTFont(tmpfile)


    # the ttf contains NAME table IDs with platformID="1", these should be removed
    name = ftfont['name']
    names = []
    for record in name.names:
        if record.platformID == 1:
            continue;
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
    os.remove(tmpfile)

def drawOverUnderline(font, name, uni, glyphclass, pos, thickness, width):
    glyph = font.createChar(uni, name)
    glyph.width = 0
    glyph.glyphclass = glyphclass

    pen = glyph.glyphPen()

    pen.moveTo((-50, pos))
    pen.lineTo((-50, pos + thickness))
    pen.lineTo((width + 50, pos + thickness))
    pen.lineTo((width + 50, pos))
    pen.closePath()

    return glyph

def makeOverUnderline(font, over=True, under=True, o_pos=None, u_pos=None):
    # test string:
    # صِ̅فْ̅ ̅خَ̅ل̅قَ̅ ̅بًّ̅ صِ̲فْ̲ ̲خَ̲ل̲قَ̲ ̲بِ̲

    thickness = font.uwidth # underline width (thickness)
    minwidth = 100.0

    if not o_pos:
        o_pos = font.os2_typoascent

    if not u_pos:
        u_pos = font.upos - thickness # underline pos

    # collect glyphs grouped by their widths rounded by 100 units, we will use
    # them to decide the widths of over/underline glyphs we will draw
    widths = {}
    for glyph in font.glyphs():
        if glyph.glyphclass == 'baseglyph' and glyph.unicode != 0xFDFD:
            width = round(glyph.width/100) * 100
            width = width > minwidth and width or minwidth
            if not width in widths:
                widths[width] = []
            widths[width].append(glyph.glyphname)

    if over:
        o_base = drawOverUnderline(font, 'uni0305', 0x0305, 'mark', o_pos, thickness, 500)

    if under:
        u_base = drawOverUnderline(font, 'uni0332', 0x0332, 'mark', u_pos, thickness, 500)

    markset = "%s %s" %(over and o_base.glyphname or "", under and u_base.glyphname or "")

    font.addMarkSet("OverUnderSet", markset)

    context_lookup_name = 'OverUnderLine'
    font.addLookup(context_lookup_name, 'gsub_contextchain', ('OverUnderSet'), (('mark', script_lang),), font.gsub_lookups[-1])

    for width in sorted(widths.keys()):
        # for each width group we create an over/underline glyph with the same
        # width, and add a contextual substitution lookup to use it when an
        # over/underline follows any glyph in this group

        single_lookup_name = str(width)

        font.addLookup(single_lookup_name, 'gsub_single', (), (), font.gsub_lookups[-1])
        font.addLookupSubtable(single_lookup_name, single_lookup_name + '1')

        if over:
            o_name = 'uni0305.%d' % width
            o_glyph = drawOverUnderline(font, o_name, -1, 'mark', o_pos, thickness, width)
            o_base.addPosSub(single_lookup_name + '1', o_name)

        if under:
            u_name = 'uni0332.%d' % width
            u_glyph = drawOverUnderline(font, u_name, -1, 'mark', u_pos, thickness, width)
            u_base.addPosSub(single_lookup_name + '1', u_name)

        context = "%s %s" %(over and o_base.glyphname or "", under and u_base.glyphname or "")

        rule = '| [%s] [%s] @<%s> | ' %(" ".join(widths[width]), context, single_lookup_name)

        font.addContextualSubtable(context_lookup_name, context_lookup_name + str(width), 'coverage', rule)

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

def mergeLatin(font, latinfile, italic=False, glyphs=None, quran=False):
    styles = {"Regular": "regular",
              "Slanted": "italic",
              "Bold": "bold",
              "BoldSlanted": "bolditalic"}

    tmpfont = mkstemp(suffix=os.path.basename(latinfile).replace("sfdir", "sfd"))[1]
    latinfont = fontforge.open(latinfile)

    validateGlyphs(latinfont) # to flatten nested refs mainly

    if glyphs:
        latinglyphs = list(glyphs)
    else:
        # collect latin glyphs we want to keep
        latinglyphs = []

        # we want all glyphs in latin0-9 encodings
        for i in range(0, 9):
            latinfont.encoding = 'latin%d' %i
            for glyph in latinfont.glyphs("encoding"):
                if glyph.encoding <= 255:
                    if glyph.glyphname not in latinglyphs:
                        latinglyphs.append(glyph.glyphname)
                elif glyph.unicode != -1 and glyph.unicode <= 0x017F:
                    # keep also Unicode Latin Extended-A block
                    if glyph.glyphname not in latinglyphs:
                        latinglyphs.append(glyph.glyphname)
                elif glyph.unicode == -1 and '.prop' in glyph.glyphname:
                    # proportional digits
                    latinglyphs.append(glyph.glyphname)

        # keep ligatures too
        ligatures = ("f_b", "f_f_b",
                     "f_h", "f_f_h",
                     "f_i", "f_f_i",
                     "f_j", "f_f_j",
                     "f_k", "f_f_k",
                     "f_l", "f_f_l",
                     "f_f")

        # and Arabic romanisation characters
        romanisation = ("uni02BC", "uni02BE", "uni02BE", "amacron", "uni02BE",
                "amacron", "eacute", "uni1E6F", "ccedilla", "uni1E6F", "gcaron",
                "ycircumflex", "uni1E29", "uni1E25", "uni1E2B", "uni1E96",
                "uni1E0F", "dcroat", "scaron", "scedilla", "uni1E63", "uni1E11",
                "uni1E0D", "uni1E6D", "uni1E93", "dcroat", "uni02BB", "uni02BF",
                "rcaron", "grave", "gdotaccent", "gbreve", "umacron", "imacron",
                "amacron", "amacron", "uni02BE", "amacron", "uni02BE",
                "acircumflex", "amacron", "uni1E97", "tbar", "aacute", "amacron",
                "ygrave", "agrave", "uni02BE", "aacute", "Amacron", "Amacron",
                "Eacute", "uni1E6E", "Ccedilla", "uni1E6E", "Gcaron",
                "Ycircumflex", "uni1E28", "uni1E24", "uni1E2A", "uni1E0E",
                "Dcroat", "Scaron", "Scedilla", "uni1E62", "uni1E10", "uni1E0C",
                "uni1E6C", "uni1E92", "Dcroat", "Rcaron", "Gdotaccent", "Gbreve",
                "Umacron", "Imacron", "Amacron", "Amacron", "Amacron",
                "Acircumflex", "Amacron", "Tbar", "Aacute", "Amacron", "Ygrave",
                "Agrave", "Aacute")

        # and some typographic characters
        typographic = ("uni2010", "uni2011", "figuredash", "endash", "emdash",
                "uni2015", "quoteleft", "quoteright", "quotesinglbase",
                "quotereversed", "quotedblleft", "quotedblright", "quotedblbase",
                "uni201F", "dagger", "daggerdbl", "bullet", "onedotenleader",
                "ellipsis", "uni202F", "perthousand", "minute", "second",
                "uni2038", "guilsinglleft", "guilsinglright", "uni203E",
                "fraction", "i.TRK", "minus", "uni2213", "radical", "uni2042")

        for l in (ligatures, romanisation, typographic):
            for name in l:
                if name not in latinglyphs:
                    latinglyphs.append(name)

    if not quran:
        # we want our ring above and below in Quran font only
        for name in ("uni030A", "uni0325"):
            font[name].clear()

        latinglyphs += buildComposition(latinfont, latinglyphs)
    subsetFont(latinfont, latinglyphs)

    digits = ("zero", "one", "two", "three", "four", "five", "six", "seven",
              "eight", "nine")

    # common characters that can be used in Arabic and Latin need to be handled
    # carefully in the slanted font so that right leaning italic is used with
    # Latin, and left leaning slanted is used with Arabic, using ltra and rtla
    # features respectively, for less OpenType savvy apps we make the default
    # upright so it works reasonably with bot scripts
    if italic:
        if "bold" in style:
            upright = fontforge.open("sources/latin/amirilatin-bold.sfdir")
        else:
            upright = fontforge.open("sources/latin/amirilatin-regular.sfdir")

        shared = ("exclam", "quotedbl", "numbersign", "dollar", "percent",
                  "quotesingle", "asterisk", "plus", "colon", "semicolon",
                  "less", "equal", "greater", "question", "at", "asciicircum",
                  "exclamdown", "section", "copyright", "logicalnot", "registered",
                  "plusminus", "uni00B2", "uni00B3", "paragraph", "uni00B9",
                  "ordmasculine", "onequarter", "onehalf", "threequarters",
                  "questiondown", "quoteleft", "quoteright", "quotesinglbase",
                  "quotereversed", "quotedblleft", "quotedblright",
                  "quotedblbase", "uni201F", "dagger", "daggerdbl",
                  "perthousand", "minute", "second", "guilsinglleft",
                  "guilsinglright", "fraction", "uni2213")

        for name in shared:
            glyph = latinfont[name]
            glyph.clear()
            upright.selection.select(name)
            upright.copy()
            latinfont.createChar(upright[name].encoding, name)
            latinfont.selection.select(name)
            latinfont.paste()

        for name in digits:
            glyph = latinfont[name]
            glyph.glyphname += '.ltr'
            glyph.unicode = -1
            upright.selection.select(name)
            upright.copy()
            latinfont.createChar(upright[name].encoding, name)
            latinfont.selection.select(name)
            latinfont.paste()

            rtl = latinfont.createChar(-1, name + ".rtl")
            rtl.addReference(name, italic)
            rtl.useRefsMetrics(name)

        for name in digits:
            pname = name + ".prop"
            glyph = latinfont[pname]
            glyph.glyphname = name + '.ltr.prop'
            glyph.unicode = -1
            upright.selection.select(pname)
            upright.copy()
            latinfont.createChar(-1, pname)
            latinfont.selection.select(pname)
            latinfont.paste()

            rtl = latinfont.createChar(-1, name + ".rtl" + ".prop")
            rtl.addReference(pname, italic)
            rtl.useRefsMetrics(pname)

    # copy kerning classes
    kern_lookups = {}
    if not quran:
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

    if not quran:
        buildComposition(font, latinglyphs)

    # add Latin small and medium digits
    for name in digits:
        if italic:
            # they are only used in Arabic contexts, so always reference the
            # italic rtl variant
            refname = name +".rtl"
        else:
            refname = name
        small = font.createChar(-1, name + ".small")
        if not small.isWorthOutputting():
            small.clear()
            small.addReference(refname, psMat.scale(0.6))
            small.transform(psMat.translate(0, -40))
            small.width = 600
            centerGlyph(small)

        medium = font.createChar(-1, name + ".medium")
        if not medium.isWorthOutputting():
            medium.clear()
            medium.addReference(refname, psMat.scale(0.8))
            medium.transform(psMat.translate(0, 50))
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

def makeSlanted(infile, outfile, latinfile, feafile, version, slant):

    font = makeDesktop(infile, outfile, feafile, version, False, False)

    # compute amout of skew, magic formula copied from fontforge sources
    import math
    skew = psMat.skew(-slant * math.pi/180.0)

    # Remove Arabic math alphanumerics, they are upright-only.
    font.selection.select(["ranges"], "u1EE00", "u1EEFF")
    for glyph in font.selection.byGlyphs:
        font.removeGlyph(glyph)

    font.selection.all()
    punct = ("period", "guillemotleft", "guillemotright", "braceleft", "bar",
             "braceright", "bracketleft", "bracketright", "parenleft",
             "parenright", "slash", "backslash", "brokenbar", "uni061F")

    for name in punct:
        font.selection.select(["less"], name)

    font.transform(skew)

    # fix metadata
    font.italicangle = slant
    font.fullname += " Slanted"
    if font.weight == "Bold":
        font.fontname = font.fontname.replace("Bold", "BoldSlanted")
        font.appendSFNTName("Arabic (Egypt)", "SubFamily", "عريض مائل")
        font.appendSFNTName("English (US)",   "SubFamily", "Bold Slanted")
    else:
        font.fontname = font.fontname.replace("Regular", "Slanted")
        font.appendSFNTName("Arabic (Egypt)", "SubFamily", "مائل")

    mergeLatin(font, latinfile, italic=skew)
    makeNumerators(font)

    # we want to merge features after merging the latin font because many
    # referenced glyphs are in the latin font
    prepareFeatures(font, feafile)

    generateFont(font, outfile)

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

def makeQuran(infile, outfile, latinfile, feafile, version):
    font = makeDesktop(infile, outfile, feafile, version, False, False)

    # fix metadata
    font.fontname = font.fontname.replace("-Regular", "Quran-Regular")
    font.familyname += " Quran"
    font.fullname += " Quran"

    digits = ("zero", "one", "two", "three", "four", "five", "six",
              "seven", "eight", "nine")

    mergeLatin(font, latinfile, glyphs=digits, quran=True)

    punct = ("period", "guillemotleft", "guillemotright", "braceleft", "bar",
             "braceright", "bracketleft", "bracketright", "parenleft",
             "parenright", "slash", "backslash")

    for name in punct:
        if name+".ara" in font:
            glyph = font[name+".ara"]
            glyph.glyphname = name
            glyph.unicode = fontforge.unicodeFromName(name)

    # abuse U+065C as a below form of U+06EC, for Qaloon
    dotabove = font["uni06EC"]
    dotbelow = font["uni065C"]
    delta = dotbelow.boundingBox()[-1] - dotabove.boundingBox()[-1]
    dotbelow.references = []
    dotbelow.addReference(dotabove.glyphname, psMat.translate(0, delta))
    dotbelow.addAnchorPoint("TashkilTashkilBelow", "basemark", 220, dotbelow.boundingBox()[1] - 100)

    # scale some vowel marks and dots down a bit
    scaleGlyph(font["uni0651"], 0.8)
    for mark in ("uni064B", "uni064C", "uni064E", "uni064F", "uni06E1"):
        scaleGlyph(font[mark], 0.9)

    for dot in ("TwoDots.a", "ThreeDots.a", "vTwoDots.a"):
        scaleGlyph(font[dot], 0.9)

    quran_glyphs = []

    # create dummy glyphs used for some coding hacks
    for i in range(1, 11):
        dummy = font.createChar(-1, "dummy%s" %i)
        dummy.width = 0
        quran_glyphs.append(dummy.glyphname)

    prepareFeatures(font, feafile)

    quran_glyphs += digits
    quran_glyphs += punct
    quran_glyphs += ("space",
            "uni060C", "uni0615", "uni0617", "uni0618", "uni0619", "uni061A",
            "uni061B", "uni061E", "uni061F", "uni0621", "uni0622", "uni0623",
            "uni0624", "uni0625", "uni0626", "uni0627", "uni0628", "uni0629",
            "uni062A", "uni062B", "uni062C", "uni062D", "uni062E", "uni062F",
            "uni0630", "uni0631", "uni0632", "uni0633", "uni0634", "uni0635",
            "uni0636", "uni0637", "uni0638", "uni0639", "uni063A", "uni0640",
            "uni0641", "uni0642", "uni0643", "uni0644", "uni0645", "uni0646",
            "uni0647", "uni0648", "uni0649", "uni064A", "uni064B", "uni064C",
            "uni064D", "uni064E", "uni064F", "uni0650", "uni0651", "uni0652",
            "uni0653", "uni0654", "uni0655", "uni0656", "uni0657", "uni0658",
            "uni065C", "uni0660", "uni0661", "uni0662", "uni0663", "uni0664",
            "uni0665", "uni0666", "uni0667", "uni0668", "uni0669", "uni066E",
            "uni066F", "uni06A1", "uni06BA", "uni0670", "uni0671", "uni067A",
            "uni06CC", "uni06D6", "uni06D7", "uni06D8", "uni06D9", "uni06DA",
            "uni06DB", "uni06DC", "uni06DD", "uni06DE", "uni06DF", "uni06E0",
            "uni06E1", "uni06E2", "uni06E3", "uni06E4", "uni06E5", "uni06E6",
            "uni06E7", "uni06E8", "uni06E9", "uni06EA", "uni06EB", "uni06EC",
            "uni06ED", "uni06F0", "uni06F1", "uni06F2", "uni06F3", "uni06F4",
            "uni06F5", "uni06F6", "uni06F7", "uni06F8", "uni06F9", "uni08F0",
            "uni08F1", "uni08F2", "uni2000", "uni2001", "uni2002", "uni2003",
            "uni2004", "uni2005", "uni2006", "uni2007", "uni2008", "uni2009",
            "uni200A", "uni200B", "uni200C", "uni200D", "uni200E", "uni200F",
            "uni2028", "uni2029", "uni202A", "uni202B", "uni202C", "uni202D",
            "uni202E", "uni202F", "uni25CC", "uniFD3E", "uniFD3F", "uniFDFA",
            "uniFDFD")
    quran_glyphs += ("uni030A", "uni0325") # ring above and below

    subsetFont(font, quran_glyphs, True)

    # set font ascent to the highest glyph in the font so that waqf marks don't
    # get truncated
    # we could have set os2_typoascent_add and hhea_ascent_add, but ff makes
    # the offset relative to em-size in the former and font bounds in the
    # later, but we want both to be relative to font bounds
    ymax = 0
    for glyph in font.glyphs():
        bb = glyph.boundingBox()
        if bb[-1] > ymax:
            ymax = bb[-1]

    font.os2_typoascent = font.hhea_ascent = ymax

    # create overline glyph to be used for sajda line, it is positioned
    # vertically at the level of the base of waqf marks
    overline_pos = font[0x06D7].boundingBox()[1]
    makeOverUnderline(font, under=False, o_pos=overline_pos)

    generateFont(font, outfile)

def makeDesktop(infile, outfile, latinfile, feafile, version, generate=True):
    font = fontforge.open(infile)
    font.encoding = "UnicodeFull" # avoid a crash if compact was set

    if version:
        setVersion(font, version)

    # remove anchors that are not needed in the production font
    cleanAnchors(font)

    #makeOverUnderline(font)

    # sample text to be used by font viewers
    # sample = 'صِفْ خَلْقَ خَوْدٍ كَمِثْلِ ٱلشَّمْسِ إِذْ بَزَغَتْ يَحْظَىٰ ٱلضَّجِيعُ بِهَا نَجْلَاءَ مِعْطَارِ.'
    #
    # for lang in ('Arabic (Egypt)', 'English (US)'):
    #     font.appendSFNTName(lang, 'Sample Text', sample)

    if latinfile:
        # mergeLatin(font, latinfile)
        simpleFontMerge(font, latinfile)
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
  --slant=VALUE         autoslant

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
                ["help", "input=", "output=", "latin=", "features=", "version=", "slant=", "quran"])
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
        elif opt == "--slant": slant = float(arg)
        elif opt == "--quran": quran = True

    if not infile:
        usage("No input file specified", -1)
    if not outfile:
        usage("No output file specified", -1)

    if not version:
        usage("No version specified", -1)
    if not feafile:
        usage("No features file specified", -1)

    if slant:
        makeSlanted(infile, outfile, latinfile, feafile, version, slant)
    elif quran:
        makeQuran(infile, outfile, latinfile, feafile, version)
    else:
        makeDesktop(infile, outfile, latinfile, feafile, version)
