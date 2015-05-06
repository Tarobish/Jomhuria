#! /usr/bin/env python

from __future__ import with_statement

# This is a stupid script. It does not search activeley for defined classes, instead
# it uses a file like our classes.fea file as input. Each class is defined in it's own line
# A line must start immediately with the @classname, otherwise it is ignored
# class names match: @A-Za-z0-9.

# usage:
# removeUnusedFeatureClasses <classes-file> [list of feature files]
# using find to get the input names
# Jomhuria/sources $ ../tools/removeUnusedFeatureClasses.py classes.fea `find . \( -name "*.fea" ! -name "classes.fea" \)`
import sys
import os
import re

def readLines(name):
    with open(name) as f:
        return f.readlines()

def getClassName(line):
    classname = re.match("(@[A-Za-z0-9_\.]+)", line)
    if classname is None:
        return None
    return classname.groups()[0]

class Glyph(object):
    def __init__(self, name):
        self.name = name

class GlyphClass(object):
    def __init__(self, definition, name, items=None):
        self.definition = definition
        self.name = name
        self.items = items or []

    @staticmethod
    def getClassName(line):
        classname = re.match("(@[A-Za-z0-9_\.]+)", line)
        if classname is None:
            return None
        return classname.groups()[0]

    @classmethod
    def getClassItems(cls, definition, itemRegistry):
        names = []
        items = []
        for m in re.finditer('\[(.*)\]', definition):
            names = [name.strip() for name in m.groups()[0].split(' ')]
            names = filter(len, names)
            break

        for name in names:
            if name in itemRegistry:
                items.append(itemRegistry[name])
            elif name[0] == '@':
                raise Exception('The class "{classname}" is used but \
                                not defined at: {definition}'.format(
                                classname=name, definition=definition)
                        )
            else:
                itemRegistry[name] = Glyph(name)
                items.append(itemRegistry[name])
        return tuple(items);

    @classmethod
    def factory(cls, definition, itemRegistry):
        classname = cls.getClassName(definition);
        if classname is None:
            # this is not a class definition
            return None;
        item = itemRegistry.get(classname, None)
        if item is None:
            # we don't do recursion detection here. It would be illegal in the
            # original fea file anyways.
            # However, a class must be defined prior usage!
            # also, redefinitions will be ignored (unlike in fea format
            # where a redefinition is in fact just that, a redefinition)
            items = cls.getClassItems(definition, itemRegistry);
            item = itemRegistry[classname] = cls(definition, classname, items)
        else:
            print 'redefinition of', item.name, '\nold: ', item.definition, 'new: ', definition
        return item;

class _State(object):
    def __init__(self, classDefs, corpus):
        self.corpus = corpus
        self.itemRegistry = {}
        self.classes = []
        self.lines = []

        for definition in classDefs:
            gClass = GlyphClass.factory(definition, self.itemRegistry)
            if gClass is not None:
                self.classes.append(gClass)
                self.lines.append(gClass)
            else:
                self.lines.append(definition)


    @staticmethod
    def getClassUsage(classname, line):
        """ match classname if not followed by [A-Za-z0-9\.]
            return None or a tuples of start indexes where the classname is used
        """
        usage = [];
        p = re.compile("({classname})(?![A-Za-z0-9_\.])".format(classname=classname))
        for m in p.finditer(line):
            usage.append(m.start())
        if len(usage) == 0:
            return None
        return tuple(usage)

    def findInCorpus(self, gClass):
        found = False
        messages = []
        for fileName, lines in self.corpus.iteritems():
            #print '++++****' * 6
            finds = [] # line numbers matching
            matchedLines = []
            for lineNumber, line in enumerate(lines):
                usage = self.getClassUsage(gClass.name, line)
                if usage is not None:
                    finds.append(str(lineNumber))
                    found = True
                    matchedLines.append(line)
            if len(finds) != 0:
                messages.append('found {classname} ({times} instances) in "{filename}" lines {lines}'.format(
                      classname=gClass.name
                    , filename=fileName
                    , times=len(finds)
                    , lines= ', '.join(finds)
                ))
                #print '\n'.join(matchedLines)
        return found, messages

    def findInClasses(self, needle):
        found = False
        referencing = None
        for gClass in self.classes:
            if gClass is needle or needle not in gClass.items:
                continue
            found = True
            if referencing is None:
                referencing = set()
            referencing.add(gClass)
        return found, referencing;

    def findClasseInUse(self, gClass):
        found, messages = self.findInCorpus(gClass)
        referencing = None
        # if len(messages):
        #     print '\t' + ('\n\t'.join(messages))

        if not found:
            found, referencing = self.findInClasses(gClass);
            if referencing is not None:
                print '{classname} is referenced in {classes}'.format(
                    classname=gClass.name
                  , classes=', '.join([item.name for item in referencing])
                )
            # else:
            #     print '{classname} is not referenced'.format(classname=gClass.name)

        return found, referencing

    def removeUnusedClasses(self):
        removals = set()
        referenced = {}
        resolve = []

        # straight forward removal
        # plus collecting references within other classes, if otherwise the
        # class could be removed
        for gClass in self.classes:
            found, referencing = self.findClasseInUse(gClass)
            if not found:
                resolve.append(gClass)
                removals.add(gClass)
            elif referencing is not None:
                referenced[gClass] = referencing;

        print len(removals), 'classes are ready for removal'

        print 'resolving references within other classes ...'
        while len(resolve):
            gClass = resolve.pop()
            for item in gClass.items:
                # references are not set if class is in corpus
                if not item in referenced:
                    # if item is a GlyphClass and not in referenced, that means
                    # it is used in self.corpus.
                    continue
                # Thus, if we can remove all references, the item can be removed
                referencing = referenced[item]
                if gClass in referencing:
                    referencing.remove(gClass)
                    print 'removed', gClass.name, 'reference from', item.name, len(referencing), 'left'
                    if not len(referencing):
                        resolve.append(item)
                        removals.add(item)
                        del referenced[item]
        print len(removals), 'classes are ready for removal'
        return tuple(getattr(line, 'definition', line) for line in self.lines if not line in removals)

def main(classesFile, featureFiles):
    corpus = {name: readLines(name) for name in featureFiles}
    inData = tuple(readLines(classesFile))
    state = _State(inData, corpus)
    out = state.removeUnusedClasses()
    if inData == out:
        print 'classes file did not change'
        return;
    print 'classes file changed, removed: ', len(inData) - len(out), 'lines'
    with open(classesFile, 'w') as f:
        f.write(''.join(out));
    #print [cls for cls in classes if cls[0] is not None]

if __name__ == '__main__':
    classesFile = sys.argv[1]
    featureFiles = sys.argv[2:]

    print 'classes file:', classesFile
    print 'featureFiles:\n\t', ',\n\t'.join(featureFiles)

    main(classesFile, featureFiles);




