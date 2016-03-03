#! /usr/bin/env python

"""
./Tools/replaceReferences.py ./Sources/jomhuria.sfdir 'uni0645.medi_KafMemMedi' 'aMem.medi_KafMemMedi'
sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && ./Tools/replaceReferences.py ./Sources/jomhuria.sfdir 'uni0645.medi_KafMemMedi' 'aMem.medi_KafMemMedi'"; sudo chown -R $USER:$USER .
"""

from __future__ import with_statement, print_function

import sys

try:
    from sortsmill import ffcompat as fontforge
except ImportError:
    import fontforge


def info(*objs):
    print("Info: ", *objs, file=sys.stderr)

def replaceReference(font, oldName, newName):
    replacementsTotal = 0;
    replacementsPerGlyph = []
    for name in font:
        glyph = font[name]
        references = []
        replaced = False
        replacements = 0
        for glyphName, data in glyph.references:
            if glyphName == oldName:
                references.append((newName, data))
                replaced = True
                replacements += 1
            else:
                references.append((glyphName, data))
        if replaced:
            glyph.references = tuple(references)
            replacementsPerGlyph.append((name, replacements))
            replacementsTotal += replacements

    return replacementsTotal, replacementsPerGlyph


def main_replaceReferences(fontLocation, oldName, newName):
    font = fontforge.open(fontLocation)

    # just to check if the names exist
    glyph = font[oldName]
    replacement = font[newName]

    total, perGlyph = replaceReference(font, oldName, newName)

    print('Details:')
    print('-'*50)
    for name, number in perGlyph:
        print(str(number).rjust(5), '|', name)
    print('Replaced references to "{oldName}" with "{newName}"'.format(oldName=oldName,newName=newName))
    print('Changed:', len(perGlyph),'glyphs')
    print('Total:', total, 'references replaced')

    if total != 0:
        font.save();






if __name__ == '__main__':
    fontLocation = sys.argv[1]
    glyphname = sys.argv[2]
    replacementname = sys.argv[3]
    info('font file:', fontLocation)
    main_replaceReferences(fontLocation, glyphname, replacementname)
