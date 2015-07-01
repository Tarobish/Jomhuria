#! /usr/bin/env python
import sys
from defcon import Font
from ufo2fdk.kernFeatureWriter import KernFeatureWriter, inlineGroupInstance



class KernFeatureWriterRTL(KernFeatureWriter):
    def getFeatureRulesForPairs(self, pairs):
        """
        Write pair rules to a list of strings.

        You should not call this method directly.
        """
        rules = []
        for (side1, side2), value in sorted(pairs.items()):
            if not side1 or not side2:
                continue
            if isinstance(side1, inlineGroupInstance) or isinstance(side2, inlineGroupInstance):
                line = "enum pos {0:s} {1:s} <{2:d} 0 {2:d} 0>;"
            else:
                line = "pos {0:s} {1:s} <{2:d} 0 {2:d} 0>;"
            if isinstance(side1, inlineGroupInstance):
                side1 = "[%s]" % " ".join(sorted(side1))
            if isinstance(side2, inlineGroupInstance):
                side2 = "[%s]" % " ".join(sorted(side2))
            rules.append(line.format(side1, side2, value))
        return rules

if __name__ == '__main__':
    font = Font(path=sys.argv[1])
    kfw = KernFeatureWriterRTL(font)
    print kfw.write()
