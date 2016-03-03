#! /usr/bin/env python

# this is a one time tool used to create commit 65163cc811324ad5fbef01012264cb0ba11517b8

# with docker/fontbuilder:
# sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && python Jomhuria/Tools/recoverCompatibility.py"; sudo chown -R $USER:$USER .

try:
    from sortsmill import ffcompat as fontforge
    from sortsmill import psMat
except ImportError:
    import fontforge
    import psMat

def tupleSignature(ref):
    """this apparently works for both types: glyph.achorPoints and glyph.references"""
    signature = []
    names = {}
    for item in ref:
        name = item[0];
        if name not in names:
            names[name] = 1
        else:
            names[name] += 1
    for name in names:
        signature.append((name, names[name]))
    return tuple(sorted(signature))

def pickTupleItems(source, target):
    """target has the authority of which anchor points/references are picked,
    source gives the values, if defined. Otherwise fall back to the target
    value.
    This way, source can't define more and/or other anchors/references than target
    which happend, but is not wanted in this phase of the project.
    """
    sourceDict = {}
    items = []
    for item in source:
        name = item[0]
        if name not in sourceDict:
            sourceDict[name] = []
        sourceDict[name].append(item)

    for item in target:
        name = item[0]
        if name in sourceDict:
            items.append(sourceDict[name][0])
            # remove this item
            sourceDict[name] = sourceDict[name][1:]
            if not sourceDict[name]:
                del sourceDict[name]
        else:
            items.append(item)
    return tuple(items)

def copyContoursIfDifferent(sourceFont, targetFont):
    # copy fg to bg and mark the glyph red if it contains any contours
    for name in sourceFont:
        source = sourceFont[name]
        # at the moment it looks looks like source is a subset
        if name not in targetFont:
            # if this happens: make a copy and a special color key for this
            # 0x0000ff

            print 'CAUTION: Source has a new glyph', name
            continue;

        target = targetFont[name]

        anchorPoints = pickTupleItems(source.anchorPoints, target.anchorPoints)

        #references = source.references
        references = pickTupleItems(source.references, target.references)

        # target.width = source.width
        # target.vwidth = source.vwidth
        # target.anchorPoints = anchorPoints;
        # target.references = references;


        if (target.layers[1] != source.layers[1]) and len(source.layers[1]) != 0:
            target.color = target.color + 0x00ff00
            target.layers[1] = source.layers[1].dup();
        elif len(source.layers[1]) == 0 and len(target.layers[1]) != 0:
            print name, 'detected deleted contents, skipping import'
            target.color = target.color + 0x0000ff


        target.width = source.width
        target.vwidth = source.vwidth
        target.anchorPoints = anchorPoints;
        target.references = references;
    return True;

if __name__ == '__main__':
   # cd ./.build
    pairs = (
        ('Jomhuria/Sources/jomhuria.sfdir', 'jomhuria-recover/Sources/jomhuria.sfdir')
      , ('Jomhuria/Sources/jomhuria-latin.sfdir', 'jomhuria-recover/Sources/jomhuria-latin.sfdir')
    )
    for source, target in pairs:
        print 'doing', source, target
        sourceFont = fontforge.open(source)
        targetFont = fontforge.open(target)
        if copyContoursIfDifferent(sourceFont, targetFont):
            targetFont.save(target)
