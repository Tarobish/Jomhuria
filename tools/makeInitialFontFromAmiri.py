#! /usr/bin/env python

# for the moment, run like so o have sortsmill available:
# $env GUILE_LOAD_PATH="/home/commander/sources/sortsmill-build/target/share/guile/site/2.0/" \
#      PYTHONPATH="/home/commander/sources/sortsmill-build/target/lib/python2.7/site-packages/" \
#      ./makeInitialFontFromAmiri.py

# with docker/fontbuilder:
# sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && python ./tools/makeInitialFontFromAmiri.py"; sudo chown -R $USER:$USER .

import os
import subprocess
from random import random
import cmath
import datetime

from sortsmill import ffcompat as fontforge
from sortsmill import psMat

from robofab.pens.reverseContourPointPen import ReverseContourPointPen
from robofab.pens.adapterPens import PointToSegmentPen, SegmentToPointPen, TransformPointPen
from ufoLib.pointPen import AbstractPointPen

class RandomizePointPen(AbstractPointPen):
    def __init__(self, outPen, bounds):
        self._outPen = outPen
        self._min = min(*bounds)
        self._magnitude = max(*bounds) - self._min

    def beginPath(self):
        """Start a new sub path."""
        self._outPen.beginPath()

    def endPath(self):
        """End the current sub path."""
        self._outPen.endPath()

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
        """Add a point to the current sub path."""
        rpt = [coord + self._min + random() * self._magnitude for coord in pt]
        self._outPen.addPoint(rpt, segmentType, smooth, name, **kwargs)

    def addComponent(self, baseGlyphName, transformation):
        """Add a sub glyph."""
        self._outPen(baseGlyphName, transformation)

class MovePointsPointPen(AbstractPointPen):
    """Move points `offset` away from the contour,
       relative to their direction on the contour.

       This is "ok" to create outlined fonts but there are problems in the
       edge cases, like acute angles for example.
       The overall method may or may not be good enough for specific use
       cases make sure to test this yourself before considering using it.
    """
    def __init__(self, outPen, offset=0, direction=0):
        self._outPen = outPen
        self._direction = direction
        self._offset = offset
        self._points = None

    def _getDirBefore(self, index, points, isOpen):
        if index == 0 and isOpen: return None
        pt = points[index];
        # say points has these values: [0, 1, 2, 3, 4, 5]
        # index = 3
        # then search will be: [2, 1, 0, 5, 4]
        search = reversed(points[index+1:] + points[:index])
        for ptBefore in search:
            if ptBefore != pt:
                return cmath.phase(pt - ptBefore);
        return None;

    def _getDirAfter(self, index, points, isOpen):
        if index == (len(points) - 1) and isOpen: return None
        pt = points[index];
        # say points has these values: [0, 1, 2, 3, 4, 5]
        # index = 3
        # then search will be: [4, 5, 0, 1, 2]
        search =  points[index+1:] + points[:index]
        for ptAfter in search:
            if ptAfter != pt:
                return cmath.phase(ptAfter - pt);
        return None;

    def _flush(self, points):
        isOpen = points[0][1][0] == 'move'
        self._outPen.beginPath();
        coordinates = [p[0] for p in points]
        for index, (point, args, kwargs) in enumerate(points):
            # directions default to 0, which is enough for us here
            dir1 = self._getDirBefore(index, coordinates, isOpen) or 0
            dir2 = self._getDirAfter(index, coordinates, isOpen) or 0

            movement1 = cmath.rect(1, dir1 + self._direction);
            movement2 = cmath.rect(1, dir2 + self._direction);

            movement = cmath.rect(self._offset, cmath.phase(movement1 + movement2));

            newPoint = point + movement;
            self._outPen.addPoint((newPoint.real, newPoint.imag), *args, **kwargs);
        self._outPen.endPath();

    def beginPath(self):
        """Start a new sub path."""
        self._points = [];

    def endPath(self):
        """End the current sub path."""
        points = self._points
        self._points = None;
        if len(points):
            self._flush(points)

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
        """Add a point to the current sub path."""
        self._points.append((pt[0] + pt[1]*1j, (segmentType, False, name), kwargs));

    def addComponent(self, baseGlyphName, transformation):
        """Add a sub glyph."""
        self._outPen.addComponent(baseGlyphName, transformation);



amiriGit = 'git@github.com:khaledhosny/amiri-font.git'
amiriDir = 'amiri-font'

def makeBlueprint(font):

    # copy fg to bg and mark the glyph red if it contains any contours
    for name in font:
        glyph = font[name]
        background = glyph.layers[0]
        foreground = glyph.layers[1]
        if len(background):
            print glyph, 'had a background ({0} contours)'.format(len(background))
        # copy fg to bg
        glyph.layers[0] = foreground;
        if len(foreground):
            # Glyphs marked red are the ones that need new outlines
            # not red marked glyphs contain only references
            glyph.color = 0xff0000
        else:
            glyph.color = 0xffffff

    # This draws a scrambled echo of the original glyphs to the foreground
    # so it is easy to spot where work is needed and also still which glyph
    # is in which place.

    #we are going to draw with cubics
    font.layers['Fore'].is_quadratic = False;

    for name in font:
        glyph = font[name]

        width = glyph.width
        vwidth = glyph.vwidth
        anchorPoints = tuple(glyph.anchorPoints)

        newFg = fontforge.layer();
        newFg.is_quadratic = False;
        glyph.layers[1] = newFg;

        background = glyph.background # this creates a copy
        if not len(background): continue

        # convert the copy to cubics the real background stays quadratics
        background.is_quadratic = False
        layerPen = glyph.glyphPen() # <= pen will remove more than it should

        # outer line of the outline
        toSegments = PointToSegmentPen(layerPen)
        rand = RandomizePointPen(toSegments, [-7, 7])
        moved = MovePointsPointPen(rand, -15, cmath.pi * .5)
        points = SegmentToPointPen(moved)
        background.draw(points)

        # inner line of the outline
        toSegments = PointToSegmentPen(layerPen)
        rand = RandomizePointPen(toSegments, [-7, 7])
        moved = MovePointsPointPen(rand, 15, -cmath.pi * .5)
        reverse = ReverseContourPointPen(moved)
        points = SegmentToPointPen(reverse)
        background.draw(points)

        # restore stuff that a pen should rather not change automagically
        # in fact, the pen should not reset anything besides outline and components.
        glyph.width = width
        glyph.vwidth = vwidth
        [glyph.addAnchorPoint(*p) for p in anchorPoints]

if __name__ == '__main__':
   # cd ./.build

    if not os.path.exists(amiriDir):
        status = subprocess.call(['git', 'clone', amiriGit, amiriDir])
        if status != 0:
            raise Exception('git clone failed with status: {0} '.format(1))
    else:
        status = subprocess.Popen(['git', 'pull'], cwd=amiriDir).wait()
        if status != 0:
            raise Exception('git pull failed with status: {0} '.format(1))

    p = subprocess.Popen(['git', 'rev-parse', 'HEAD']
                                , cwd=amiriDir, stdout=subprocess.PIPE)
    p.wait();
    git_revison = p.stdout.read();
    fontlog = '\n'.join((
            datetime.datetime.now().isoformat(' ')
          , 'This file was generated from the sources of Amiri Font by Khaled Hosny,'
          , 'to serve as a blueprint for the font engineering of Jomhuria font.'
          , 'http://www.amirifont.org/'
          , 'Amiri git:  {amiriGit}'
          , 'git revison: {git_revison}'

        )).format(amiriGit=amiriGit, git_revison=git_revison)
    # just hijack what Khaled wrote, to make a subsetted, clean latin font
    import imp
    build = imp.load_source('build', os.path.join(amiriDir, 'tools', 'build.py'))

    amiriFont = fontforge.open(os.path.join(amiriDir, 'sources', 'amiri-regular.sfdir'))

    newFont = fontforge.font();
    # < needed for build.mergeLatin, it looks for the -Regular"
    newFont.fontname = 'JomhuriaLatin-Regular';
    # take the dimensions from amiri
    newFont.ascent = amiriFont.ascent
    newFont.descent = amiriFont.descent
    newFont.em = amiriFont.em
    newFont.fontlog = fontlog;

    # the source is quadratic, I want to keep that information in the background
    # the foreground will be cubic
    newFont.layers['Fore'].is_quadratic = True;
    newFont.layers['Back'].is_quadratic = True;

    # mergeLatin expects these (just to remove them when qran = false)
    for name in ("uni030A", "uni0325"):
        newFont.createChar(-1 ,name)
    os.chdir(amiriDir);
    build.mergeLatin(newFont, None);
    os.chdir('..');

    makeBlueprint(newFont);
    # copy the guides of the source font
    sourceLatin = fontforge.open(os.path.join(amiriDir, 'sources', 'latin', 'amirilatin-regular.sfdir'));
    newFont.guide = sourceLatin.guide
    newFont.save('jomhuria-latin.sfdir');

    makeBlueprint(amiriFont);
    amiriFont.fontlog = fontlog;
    amiriFont.save('jomhuria.sfdir');
