#! /usr/bin/env python

from __future__ import with_statement, print_function

"""
This script removes characters from Jomhuria that became inaccessible with
certainty. That means

* no unicode value
* not referenced as a component
* name is not mentioned in the fea files (this does NOT check semantically
  whether a glyph, if it's name is used in the fea, can be accessed) Thus,
  the names should really be removed from there if not needed anymore. Then
  this script can "clean up"

$ ./Tools/removeInaccessibleGlyphs.py ./sources/jomhuria.sfdir ./sources/*.fea
$ sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && ./Tools/removeInaccessibleGlyphs.py ./sources/jomhuria.sfdir ./sources/*.fea"; sudo chown -R $USER:$USER .
"""

import sys
import os
import re
try:
    from sortsmill import ffcompat as fontforge
except ImportError:
    import fontforge


def info(*objs):
    print("Info: ", *objs, file=sys.stderr)


def readLines(name):
    with open(name) as f:
        return f.readlines()

def isGlyphName(name):
    return re.match('[A-Za-z][A-Za-z0-9_\.\-]*', name) is not None;


def isClassName(name):
    return re.match('@[A-Za-z][A-Za-z0-9_\.\-]*', name) is not None;


def getMatchNamePattern(name):
    assert isGlyphName(name) or isClassName(name), \
                '`name` must be a glyph/class name, but doesn\'t match\
                the patterns,'.format(name=name)
    # escape prior injecting into the regex
    escaped = name.replace('.', '\.').replace('-', '\-');
    return re.compile('(?<![A-Za-z_\-\.@]){name}(?![A-Za-z_\-\.])'.format(name=escaped))


def replaceNameInFeatures(oldName, newName, featureFiles):
    assert isGlyphName(newName) or isClassName(name), \
        '`newName` does not match the pattern assumed for glyph/class names: \
         {name}'.format(name=newName)
    r = getMatchNamePattern(oldName)
    total = 0
    perFile = [] # tuples of (filename, count)
    perFileAndLine = [] # tuples of (filename, (tuples of (lineNo, count)))
    for fileName, lines in featureFiles.iteritems():
        perFileTotal = 0
        lineNoCount = []
        for i in range(len(lines)):
            lines[i], numberSubsMade = r.subn(newName, lines[i]);
            lineNoCount.append((i, numberSubsMade))
            perFileTotal += numberSubsMade;
        perFileAndLine.append((fileName, tuple(lineNoCount)))
        perFile.append(fileName, perFileTotal)
        total += perFileTotal
    return total, tuple(perFile), tuple(perFileAndLine);



def countNameInFeatures(name, featureFiles):
    """
    This is to analyze the usage of a name in the features.
    If you just want to check whether a name is used at all `nameIsInFeatures`
    is much faster.
    """
    r = getMatchNamePattern(name)
    total = 0;
    perFile = [];
    perFileAndLine = [];
    for fileName, lines in featureFiles.iteritems():
        perFileTotal = 0
        lineNoCount = []
        for i, line in enumerate(lines):
            numberSubsMade = r.subn(newName, line)[1]
            lineNoCount.append((i, numberSubsMade))
            perFileTotal += numberSubsMade
        perFileAndLine.append((fileName, tuple(lineNoCount)))
        perFile.append(fileName, perFileTotal)
        total += perFileTotal
    return total, tuple(perFile), tuple(perFileAndLine);

def nameIsInFeatures(name, featureFiles):
    r = getMatchNamePattern(name)
    for _, lines in featureFiles.iteritems():
        for line in lines:
            if r.search(line) is not None:
                return True
    return False

def nameIsException(name):
    if name.endswith('.small'):
        return True;
    return False

def glyphHasUnicode(glyph):
    return glyph.unicode != -1 or glyph.altuni is not None

class _State(object):
    def __init__(self, font, featureFiles):
        self.font = font
        self.featureFiles = featureFiles
        self.itemRegistry = {}

    def findUnaccessibleGlyphs(self):
        candidates = {}
        # find potentially unaccessible glyphs:
        #    no unicode
        #    not in the feature files
        #
        # then, we can check for dependants of that glyph, if the glyph is
        # not used anywhere it can be removed. If it defined components,
        # these can be removed when no dependants are  left
        for name in self.font:
            glyph = self.font[name]
            if glyphHasUnicode(glyph) or nameIsInFeatures(name, self.featureFiles) \
                        or nameIsException(name):
                continue
            # this glyph is a candidate for removal, it can be removed if
            # it has no dependants, if it has dependants we may be able to
            # remove it later
            candidates[name] = set() # dependants
        # get all dependants of the candidates
        for name in self.font:
            glyph = self.font[name]
            for glyphName, _ in glyph.references:
                if glyphName in candidates:
                    candidates[glyphName].add(name)

        # initially fill removals
        cleanup = []
        for name in candidates:
            dependants = candidates[name]
            if len(dependants) == 0:
                # print('\t', name)
                cleanup.append(name)

        # clean up dependencies
        removals = set()
        while len(cleanup):
            name = cleanup.pop()
            removals.add(name)
            glyph = self.font[name]
            print(name)
            for glyphName, _ in glyph.references:
                if glyphName not in candidates:
                    continue
                dependants = candidates[glyphName]
                if name not in dependants:
                    continue
                dependants.remove(name)
                if len(dependants) == 0:
                    # print('\t', name)
                    cleanup.append(glyphName)

        return removals

def main(fontLocation, featureFileList):
    font = fontforge.open(fontLocation)
    featureFiles = {name: readLines(name) for name in featureFileList}
    state = _State(font, featureFiles)
    removals = state.findUnaccessibleGlyphs()

    info('to be removed:', len(removals), 'of', len(font), 'new length: ', len(font) - len(removals))

    if not removals:
        info('nothing to do')
        return;

    for name in removals:
        font.removeGlyph(name)
    font.save()


if __name__ == '__main__':
    fontLocation = sys.argv[1]
    featureFiles = sys.argv[2:]

    info('font file:', fontLocation)
    info('featureFiles:\n\t', ',\n\t'.join(featureFiles))

    main(fontLocation, featureFiles);
