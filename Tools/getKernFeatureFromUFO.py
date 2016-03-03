#! /usr/bin/env python
from __future__ import print_function
import sys
import re
import unicodedata2 as unicodedata
from fontTools import agl

from defcon import Font
from ufo2fdk.kernFeatureWriter import KernFeatureWriter, inlineGroupInstance \
                                    , side1FeaPrefix, side2FeaPrefix

def info(*objs):
    print('INFO: ', *objs, file=sys.stderr)

def warning(*objs):
    print('WARNING: ', *objs, file=sys.stderr)

def scriptGetHorizontalDirection (script):
    """
    from: https://github.com/behdad/harfbuzz/blob/master/src/hb-common.cc#L446

    see: http://goo.gl/x9ilM
    see also: http://unicode.org/iso15924/iso15924-codes.html
    """
    if script.lower() in (
                # Unicode-1.1 additions
                  'arab' # ARABIC
                , 'hebr' # HEBREW

                # Unicode-3.0 additions
                , 'syrc' # SYRIAC
                , 'thaa' # THAANA

                # Unicode-4.0 additions
                , 'cprt' # CYPRIOT

                # Unicode-4.1 additions
                , 'khar' # KHAROSHTHI

                # Unicode-5.0 additions
                , 'phnx' # PHOENICIAN
                , 'nkoo' # NKO

                # Unicode-5.1 additions
                , 'lydi' # LYDIAN

                # Unicode-5.2 additions
                , 'avst' # AVESTAN
                , 'armi' # IMPERIAL_ARAMAIC
                , 'phli' # INSCRIPTIONAL_PAHLAVI
                , 'prti' # INSCRIPTIONAL_PARTHIAN
                , 'sarb' # OLD_SOUTH_ARABIAN
                , 'orkh' # OLD_TURKIC
                , 'samr' # SAMARITAN

                # Unicode-6.0 additions
                , 'mand' # MANDAIC

                # Unicode-6.1 additions
                , 'merc' # MEROITIC_CURSIVE
                , 'mero' # MEROITIC_HIEROGLYPHS

                # Unicode-7.0 additions
                , 'mani' # MANICHAEAN
                , 'mend' # MENDE_KIKAKUI
                , 'nbat' # NABATAEAN
                , 'narb' # OLD_NORTH_ARABIAN
                , 'palm' # PALMYRENE
                , 'phlp' # PSALTER_PAHLAVI
                # Unicode-8.0 additions
                , 'hung' # OLD_HUNGARIAN
                ):
        return 'RTL'
    return 'LTR'



class KernFeatureWriterWithHorizontalDirections(KernFeatureWriter):
    def __init__(self, font, scripts, groupNamePrefix='', **options):
        """
        font: a defcon font
        scripts: list of four letter unicode script codes in the "scripts" argument.

        options:
            simpleImplementation: bool, default False
                True:
                    Generate both an LTR kern lookup and an RTL one; including all kerning pairs in both.
                    Reference the RTL lookup from script systems that are RTL, and the LTR one for others.
                False (default value):
                    The same as "True" but try to eliminate pairs from the RTL and LTR lookup to reduce
                    kern table size.

                see: https://github.com/unified-font-object/ufo-spec/issues/16#issuecomment-120036174

            ignoreMissingUnicodeInGroupItems: bool, default True
                True (default value):
                    create "LTR" or "RTL" pure groups if the reason to be
                    "MIX" would be only glyphs that don't yield a unicode/direction
                False:
                    create "MIX" rules if a group has members without
                    unicode and with unicode, but is otherwise homogenous
                    "LTR" or "RTL"

                Details:
                For each side of a pair the method getPairItemDirection
                returns one of:"LTR", "RTL", "MIX", False
                False: discards the kerning pair completeley.
                MIX: creates two rules for the pair in both script directions
                LTR and RTL: create just one lookup in the respective direction.

                If the pair-item is a glyph-group each member is evaluated.
                If the items of a group yield different values "MIX" is
                returned. For the filesize however "LTR" or "RTL" is preferable.
                A group member that yields `False` can change a homogenous
                group into a "MIX" group. In case of the Jomhuria input
                kerning data this happens, because we can't determine a
                unicode for the glyph/name. However, the glyphs in that font
                that don't yield a useful unicode are not used in text layout
                (they are not inserted by fea `sub` rules). They also
                shouldn't be in the kerning data at all (but they are). Thus
                it's better to ignore these cases and produce more rules
                with homogenous "RTL" or "LTR" value.

                Hence the more aggressive option is the default here.
                Glyphs that happen in the text layout that don't yield
                unicode values (we use several approaches here) are not
                desireable in general (e.g. it breaks pdf text extraction).

            createPureLookups: bool, default True
                True (default value):
                    Keep the "mixed rules" and the "pure rules" of a direction
                    separated, by creating up to two lookups per direction.
                False:
                    Merge the "mixed rules" and the "pure rules" of a direction
                    into one lookup per direction.

                Helps when analyzing the result of this script by preserving
                the data of pure vs mixed pairs.

            usePureLookupsInDFLT: bool, default False
                True:
                    Use the "pure lookups" for `script DFLT` not in the scripts
                    defined by the `scripts` argument.
                False (default value):
                    Use the "pure lookups" in the scripts with the same direction
                    as the lookup has, not as DFLT for all scripts.

                    Default because of: https://github.com/unified-font-object/ufo-spec/issues/16#issuecomment-120036174

                NOTE: Has only an effect if "createPureLookups" is true.

                This may be useful for research and also may help to find/fix
                possible bugs.
                The direction of the kerning pairs in the "pure lookups"
                is in theory unambigous. They should always be kerned by
                the shaping engine in the direction that is forseen by
                this code. Putting them into DFLT may or may not be better
                depending on how the fea "script" tags are processed and
                if there are effects by the metadata of the text that is
                processed, i.e. if the user tags the text as some script
                that we don't define here.
                AFAIK a glyph can be associated with many different scripts
                in unicode, so it may be hard to determine  the right kern
                lookup sometimes. (The more data in DFLT, the better?)
        """
        # TODO: There may be a way to find out the scripts to use by looking
        # at the font data. Unicode should be capable of providing that
        # information, but there seems to be no ready to use implementation
        # for it.
        self.scripts = _scripts = {}
        if not scripts:
            raise TypeError('Need at least one script in the "scripts" argument iterable.')
        for script in scripts:
            writingDir = scriptGetHorizontalDirection(script.lower())
            if writingDir not in _scripts:
                _scripts[writingDir] = []
            _scripts[writingDir].append((script, scripts[script]))

        self.scriptDirs = self.scripts.keys()

        self.options = {}
        for k, default in self._optionDefaults.iteritems():
            self.options[k] = options.get(k, default)

        super(KernFeatureWriterWithHorizontalDirections, self).__init__(font, groupNamePrefix)

    _optionDefaults = {
          'simpleImplementation': False
        , 'ignoreMissingUnicodeInGroupItems':  True
        , 'createPureLookups': True
        , 'usePureLookupsInDFLT': False
    }

    getFeatureRulesForPairsLTR = KernFeatureWriter.getFeatureRulesForPairs

    def getFeatureRulesForPairsRTL(self, pairs):
        """
        Write RTL pair rules to a list of strings.

        You should not call this method directly.
        """
        rules = []
        for (side1, side2), value in sorted(pairs.items()):
            if not side1 or not side2:
                continue
            if isinstance(side1, inlineGroupInstance) or isinstance(side2, inlineGroupInstance):
                line = 'enum pos {0:s} {1:s} <{2:d} 0 {2:d} 0>;'
            else:
                line = 'pos {0:s} {1:s} <{2:d} 0 {2:d} 0>;'
            if isinstance(side1, inlineGroupInstance):
                side1 = '[%s]' % ' '.join(sorted(side1))
            if isinstance(side2, inlineGroupInstance):
                side2 = '[%s]' % ' '.join(sorted(side2))
            rules.append(line.format(side1, side2, value))
        return rules


    def getWritingDirRules(self, writingDir, pairs):
        """
            Return a list of the kerning rules and some comments
        """
        glyphGlyph, glyphGroupDecomposed, groupGlyphDecomposed, glyphGroup, groupGlyph, groupGroup = self.getSeparatedPairs(pairs)
        order = [
            ('# glyph, glyph', glyphGlyph),
            ('# glyph, group exceptions', glyphGroupDecomposed),
            ('# group exceptions, glyph', groupGlyphDecomposed),
            ('# glyph, group', glyphGroup),
            ('# group, glyph', groupGlyph),
            ('# group, group', groupGroup),
        ]

        getFeatureRulesForPairs = self.getFeatureRulesForPairsLTR \
                            if writingDir == 'LTR' \
                            else self.getFeatureRulesForPairsRTL

        rules = []
        for note, pairs in order:
            if pairs:
                rules.append(note)
                rules += getFeatureRulesForPairs(pairs)
                rules.append('')
        # remove the last empty line
        if rules and rules[-1] == '': rules.pop();
        return rules

    def getUnicodeFromGlyphName(self, name):
        # Ask the font
        glyph = self.font[name]
        if glyph.unicode:
            return unichr(glyph.unicode)

        # Names can be constructed like uni1234_uni4567.old or f_i.swash
        # since we need the unicode value only to determine a direction,
        # the first glyph name should be enough.
        firstNamePart = name.split('.', 1)[0].split('_', 1)[0]

        # Ask AGLFN
        if firstNamePart in agl.AGL2UV:
            return unichr(agl.AGL2UV[firstNamePart])

        # Try to parse the name into a unicode value
        # matches things like u1EE29* or uni1234*
        match = re.match('^(uni|u)([A-F0-9]{4,}).*', firstNamePart, re.IGNORECASE)
        if match:
            code = int(match.group(2), 16)
            return unichr(code)

        # no luck
        return False

    def getPairItemDirection(self, item):
        """
        Return one of: "LTR", "RTL", "MIX", False

        Note that when mentioning "groups" that includes single glyphs.
        A single item is treated as a group with just one member.

        This was the initial description

        * Associate each glyph to a Unicode character,
        * Exclude from RTL kern table all glyphs associated
                with Unicode characters that have Bidi_Type=L,
        * Exclude from LTR kern table all glyphs associated
               with Unicode characters that have Bidi_Type=R or Bidi_Type=AL.

        However, the exclusion model got altered into an inclusion model
        because groups could define mixed directions and thus would have
        to stay in all kern tables.

        An alternative way could be to break up the groups and reorder
        them to create a couple of better defined groups.

        FILTERING:
        Only if all memnbers of a group are `False` the whole group and
        subsequently pair is dissmissed. Alternativeley we could dismiss
        the whole group when at least one member is `False`. But I believe
        that would create more problems.
        Rather: we should filter the group contents much earlier in
        KernFeatureWriter.getPairs or KernFeatureWriter.getGroups

        See also: the docs for options.ignoreMissingUnicodeInGroupItems
                  in __init__
        """
        # Note: KernFeatureWriter.getPairs should already have filtered
        # empty groups and nonexisting pairs, thus it is not checked here.
        if item.startswith(side1FeaPrefix) or item.startswith(side2FeaPrefix):
            groups = self.side1Groups if item.startswith(side1FeaPrefix) \
                                      else self.side2Groups
            names = groups[item]
        else:
            names = [item]

        writingDirs = set()
        for name in names:
            unicodeChar = self.getUnicodeFromGlyphName(name)
            # http://unicode.org/reports/tr9/#Table_Bidirectional_Character_Types
            if unicodeChar == False:
                if not self.options['ignoreMissingUnicodeInGroupItems']:
                    # may result in a "MIX" pair if this is a bigger group
                    writingDirs.add(False)
                continue
            bidiType = unicodedata.bidirectional(unicodeChar)

            # L: Left-to-Right
            if bidiType == 'L':
                writingDirs.add('LTR')
            # R: Right-to-Left
            # AL: Right-to-Left Arabic
            elif bidiType in ('R', 'AL'):
                writingDirs.add('RTL')
            # AN: Arabic Number
            # FIXME: remove bidiType == 'AN' this from kerning? This
            # filtering should rather happen earlier, somewhere in
            # KernFeatureWriter.getPairs or KernFeatureWriter.getGroups
            # elif bidiType == 'AN':
            #    writingDirs.add(False)
            else:
                writingDirs.add('MIX')

        # if writingDirs.has(False)
        #     return False
        if len(writingDirs) > 1:
            return 'MIX'
        elif len(writingDirs) == 0:
            return False
        return writingDirs.pop() # "LTR", "RTL", "MIX" or False

    def getPairData(self, pair):
        """
        Returns writingDir for the pair

        writingDir may be "LTR", "RTL", "MIX" or False

        "LTR" and "RTL": The pair goes only into the respective direction lookup.
        "MIX": A pair with mixed entry types, goes into the lookups for both directions
        False: The pair is removed from kerning
        """

        side1writingDir, side2writingDir = [self.getPairItemDirection(side)
                                for side in pair]

        if not side1writingDir or not side2writingDir:
            # Filtered/Removed
            writingDir = False
        elif side1writingDir in ['LTR', 'RTL'] and side1writingDir == side2writingDir:
            writingDir = side1writingDir
        else:
            writingDir = 'MIX'

        return writingDir

    def getPairsData(self, pairs):
        """
        Returns: (purePairs, mixedPairs)

        purePairs = {'LTR': { *dict of pairdata* },'RTL': { *dict of pairdata* }}
        mixedPairs = { *dict of pairdata* }
        """

        purePairs = {'LTR': {},'RTL': {}}
        mixedPairs = {}

        if self.options['simpleImplementation']:
            mixedPairs.update(pairs)
            return purePairs, mixedPairs

        # try to reduce kern table size
        for pair, value in pairs.iteritems():
            writingDir = self.getPairData(pair)
            if not writingDir:
                continue
            elif writingDir == 'MIX':
                mixedPairs[pair] = value
            else:
                purePairs[writingDir][pair] = value
        return purePairs, mixedPairs

    def createSeparatedPureAndMixedLookups(self, purePairs, mixedPairs):
        lookups = {}
        for scriptDir, pairs in purePairs.iteritems():
            if len(pairs):
                label = 'kernPure{0}'.format(scriptDir)
                lookups[label] = self.getWritingDirRules(scriptDir, pairs)
        if len(mixedPairs):
            for scriptDir in ['LTR', 'RTL']:
                label = 'kernMixed{0}'.format(scriptDir)
                lookups[label] = self.getWritingDirRules(scriptDir, mixedPairs)
        return lookups

    def createUnifiedPureAndMixedLookups(self, purePairs, mixedPairs):
        lookups = {}
        for scriptDir in ['LTR', 'RTL']:
            unifiedPairs = {}
            if scriptDir in purePairs:
                unifiedPairs.update(purePairs[scriptDir])
            unifiedPairs.update(mixedPairs)
            if not len(unifiedPairs):
                continue;
            label = 'kernMixed{0}'.format(scriptDir)
            lookups[label] = self.getWritingDirRules(scriptDir, unifiedPairs)
        return lookups

    def getLookupData(self, pairs):
        """
        Returns lookups, directions.

        lookups = {lookupLabel: [rules]}
        directions = { (lookupLabel, lookupLabel, ...): [scripts]}
        """
        purePairs, mixedPairs = self.getPairsData(pairs)

        if self.options['createPureLookups']:
            lookups = self.createSeparatedPureAndMixedLookups(purePairs, mixedPairs)
        else:
            lookups = self.createUnifiedPureAndMixedLookups(purePairs, mixedPairs)

        directions = {}
        for scriptDir, scripts in self.scripts.iteritems():
            if len(scripts):
                labels = []
                if not self.options['usePureLookupsInDFLT']:
                    # kernPure* lookups must also be present in lookups
                    # to get used.
                    labels.append('kernPure{0}'.format(scriptDir))
                labels.append('kernMixed{0}'.format(scriptDir))
                directions[tuple(labels)] = scripts

        return lookups, directions

    def compileKern(self, headerText, classes, lookups, directions):
        # line indentation
        lineFormat = '    {0}'
        def makeLines (lines):
            return [lineFormat.format(line) for line in lines]
        # lookup definition
        lookupOpenFormat = 'lookup {label} {{'
        lookupCloseFormat = '}} {label};'
        # lookup usage
        lookupUsageFormat = 'lookup {label};'

        # write the lookups
        feature = []

        # add kerning classes
        if classes:
            feature.append('# kerning classes')
            feature += classes
            feature.append('')

        for label, rules in lookups.iteritems():
            feature.append(lookupOpenFormat.format(label=label))
            feature.append(lineFormat.format('lookupflag IgnoreMarks;'))
            feature += makeLines(rules)
            feature.append(lookupCloseFormat.format(label=label))
            feature.append('')

        # write the feature
        feature.append('feature kern {')
        if headerText:
            for line in headerText.splitlines():
                line = line.strip()
                if not line.startswith('#'):
                    line = '# ' + line
                feature.append(lineFormat.format(line))

        # the usage of the lookups
        usage = []
        if self.options['createPureLookups'] and self.options['usePureLookupsInDFLT']:
            # put kernPure* into the DFLT script
            pureLabels = ['kernPure{0}'.format(script) for script in self.scripts]
            for label in pureLabels:
                if label not in lookups:
                    continue
                usage.append(lookupUsageFormat.format(label=label))

        # Use the lookups in their specific scripts
        for labels, scripts in directions.iteritems():
            lookupReferences = [lookupUsageFormat.format(label=label)
                                for label in labels if label in lookups]
            if not lookupReferences:
                # no actual lookups present for the label
                continue

            for script, langs in scripts:
                usage.append('script {0};'.format(script))
                for lang in langs:
                    usage.append('language {0};'.format(lang))
                    usage += lookupReferences

        feature += makeLines(usage)
        feature.append('} kern;')
        return '\n'.join(feature)

    def write(self, headerText=None):
        """
        Write the feature text. If *headerText* is provided
        it will inserted after the ``feature kern {`` line.
        """
        if not self.pairs:
            return ''

        lineFormat = '    {0}'

        # get the classes
        groups = dict(self.side1Groups)
        groups.update(self.side2Groups)
        classes = self.getClassDefinitionsForGroups(groups)

        # get the rules
        lookups, directions = self.getLookupData(self.pairs)
        return self.compileKern(headerText, classes, lookups, directions)

if __name__ == '__main__':
    font = Font(path=sys.argv[1])
    scripts = {'arab': ('dflt', 'ARA ', 'URD ', 'SND '), 'latn': ('dflt', 'TRK ')}

    kfw = KernFeatureWriterWithHorizontalDirections(font, scripts)
    print(kfw.write())
