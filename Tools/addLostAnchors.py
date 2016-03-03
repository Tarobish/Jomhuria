#! /usr/bin/env python

# Using the fontforge sortsmill glyph pen deletes the anchors of a glyph,
# which is undocumented behavior. The  makeInitialFontFromAmiri.py did not
# recover them when I created the initial Jomhuria fonts.
# This script copies the anchors from one font to another.

# with docker/fontbuilder:
# sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && python ./Tools/addLostAnchors.py"; sudo chown -R $USER:$USER .



from sortsmill import ffcompat as fontforge

def copyAnchors(sourceFont, targetFont):
    count = 0
    for name in sourceFont:
        if name not in targetFont:
            continue
	glyph = targetFont[name]
        sourceAnchors = sourceFont[name].anchorPoints
        targetAnchors = {p[0]:p for p in glyph.anchorPoints}

        for p in sourceAnchors:
            if p[0] in targetAnchors: continue
            print glyph, 'adding', p
            glyph.addAnchorPoint(*p)
            count += 1
    return count


if __name__ == '__main__':
   # cd ./.build
    pairs = (
        ('amiri-font/sources/amiri-regular.sfdir', 'sources/jomhuria.sfdir')
      , ('amiri-font/sources/latin/amirilatin-regular.sfdir', 'sources/jomhuria-latin.sfdir')
    )
    for source, target in pairs:
        sourceFont = fontforge.open(source)
        targetFont = fontforge.open(target)
        if copyAnchors(sourceFont, targetFont):
            targetFont.save()


