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

$ ./Tools/analyzeGlyphsMarkedForRemoval.py sources/jomhuria.sfdir sources/*.fea | less
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
            numberSubsMade = r.subn('', line)[1]
            lineNoCount.append((i, numberSubsMade))
            perFileTotal += numberSubsMade
        perFileAndLine.append((fileName, tuple(lineNoCount)))
        perFile.append((fileName, perFileTotal))
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

def isMarkedForRemoval(glyph):
    return glyph.color == 0x00FF00

def getDependents(glyphs, font):
    dependents = {}
    for glyph in glyphs:
        dependents[glyph.glyphname] = set() # dependents

    for name in font:
        glyph = font[name]
        for glyphName, _ in glyph.references:
            if glyphName in dependents:
                dependents[glyphName].add(name)
    return dependents

def getTableRow(glyph, dependents, featureFiles):
    font = glyph.font
    hardDeps = set()
    softDeps = set()
    for name in dependents[glyph.glyphname]:
        if not isMarkedForRemoval(font[name]):
            hardDeps.add(name)
        else:
            softDeps.add(name)

    # the dependencies of a soft dependency can be hard dependencies
    softDepsStack = list(softDeps)
    higherOrderHardDeps = set()
    while len(softDepsStack):
        glyphname = softDepsStack.pop()
        for name in dependents[glyphname]:
            if not isMarkedForRemoval(font[name]):
                higherOrderHardDeps.add(name)
            else:
                # it's a soft dependencies, push to stack to examine futther
                softDepsStack.append(name);

    return (
      # this is rather bad, we won't remove encoded glyphs
        glyphHasUnicode(glyph)
      # we got to decide what to do
      , nameIsException(glyph.glyphname)
      # this is a blocker, need to understand the reason
      # a 0 can be removed
      # number of dependents not marked for removal
      , len(hardDeps)
      # soft deps that eventually have hard deps
      , len(higherOrderHardDeps)
      # real soft deps
      , len(softDeps) - len(higherOrderHardDeps)

      # number of dependents <= not important

      # it is most probably, this should be the only blocker
      , nameIsInFeatures(glyph.glyphname, featureFiles)
       #name
      , glyph.glyphname
    )

def getMarkedGlyphs(font):
    marked = []
    for name in font:
        if isMarkedForRemoval(font[name]):
            marked.append(font[name])
    return marked

def main_blockers(fontLocation, featureFileList):
    font = fontforge.open(fontLocation)
    featureFiles = {name: readLines(name) for name in featureFileList}

    marked = getMarkedGlyphs(font)
    dependents = getDependents(marked, font)
    table = sorted([getTableRow(glyph, dependents, featureFiles) for glyph in marked], reverse=True)

    headers = ['unicode', 'is exception', '1-hard deps', 'n-hard deps', 'soft deps', 'in fea', 'name']
    headerSizes = [len(name) for name in headers]
    print(' | '.join(headers))
    for row in table:
        # skip rows that would be removed by removeInaccessibleGlyphs.py
        if tuple(row[:-1]) == (False, False, 0, 0, 0,False): continue
        index = iter(xrange(len(headers)))
        print(' | '.join([str(item).rjust(headerSizes[index.next()]) for item in row]))

def main_features(fontLocation, featureFileList):
    font = fontforge.open(fontLocation)
    featureFiles = {name: readLines(name) for name in featureFileList}

    marked = getMarkedGlyphs(font)
    table = sorted([(countNameInFeatures(glyph.glyphname, featureFiles), glyph.glyphname) for glyph in marked], reverse=True)

    for (total, perFile, _), name in table:
        if not total: continue
        print('-' * 20)
        print(name, 'total:', total)
        for filename, count in perFile:
            if not count: continue
            print(str(count).ljust(5), ' | ', filename)


def _cleanClass(classname, font, classFeatureFile, featureFiles):
    klass = None
    r = getMatchNamePattern(classname)
    for line in classFeatureFile:
        if not r.match(line):
            continue
        klass = []
        klass = filter(len, line[line.index('[') + 1:line.index(']')].split(' '))
    if klass is None:
        raise Exception('Class {name} not found'.format(name=classname))

    marked = getMarkedGlyphs(font)
    dependents = getDependents(marked, font)

    new_klass = []
    # clean class from otherwise removable glyphs
    for name in klass:
        if name not in dependents:
            new_klass.append(name)
            continue
        glyph = font[name]
        row = tuple(getTableRow(glyph, dependents, featureFiles)[:-1])
        if row == (False, False, 0, 0, 0, True) \
                    and countNameInFeatures(name, featureFiles)[0] == 1: # it's in the classFeatureFile and nowhere else
            continue
        new_klass.append(name)
    return tuple(new_klass), tuple(klass), len(klass) - len(new_klass)

def main_cleanClass(classname, fontLocation, featureFileList):
    font = fontforge.open(fontLocation)
    featureFiles = {name: readLines(name) for name in featureFileList}
    classFeatureFile = featureFiles['sources/classes.fea']
    new_klass, _, removed = _cleanClass(classname, font, classFeatureFile, featureFiles)
    print('removed', removed)
    print('{name} = [ {classes} ];'.format(name=classname,classes=' '.join(new_klass)))

def main_cleanable(fontLocation, featureFileList):
    font = fontforge.open(fontLocation)
    featureFiles = {name: readLines(name) for name in featureFileList}
    classFeatureFile = featureFiles['sources/classes.fea']

    classes = []
    for number, line in enumerate(classFeatureFile):
        index = line.find('=')
        if index == -1:
            index = line.find(' ')
        if index <= 0:
            continue
        classname = line[:index-1].strip();
        if not isClassName(classname):
            continue
        new_klass, _, removed = _cleanClass(classname, font, classFeatureFile, featureFiles)
        if removed:
            print (classname, 'removed:', removed, 'empty:', not len(new_klass))


if __name__ == '__main__':
    command = sys.argv[1]
    fontLocation = sys.argv[2]
    featureFiles = sys.argv[3:]

    info('font file:', fontLocation)
    info('featureFiles:\n\t', ',\n\t'.join(featureFiles))
    if command == 'blockers':
        main_blockers(fontLocation, featureFiles);
    elif command == 'fea':
        main_features(fontLocation, featureFiles)
    elif command.startswith('clean@'):
        main_cleanClass(command[5:], fontLocation, featureFiles)
    elif command == 'cleanable':
        main_cleanable(fontLocation, featureFiles)
    else:
        raise Exception('Unknown command "{command}".'.format(command=command))
