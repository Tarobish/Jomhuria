#!/usr/bin/env python

from __future__ import print_function
from runtest import runHB

import sys
import re


def replaceSpecials(inp, dictionary={}):
    pattern = '|'.join(sorted(re.escape(k) for k in dictionary))
    return re.sub(pattern, lambda m: dictionary.get(m.group(0)), inp)

def replaceUnicodes(inp):
    pattern = '\\u([0-9A-Fa-f]+)'
    #m.group(0)
    return re.sub(pattern, lambda m: unichr(int(m.group(1), 16)), inp)

specials = {
    u':zwj:': u'\u200D'
  , u':zwnj:': u'\u200C'
  , u':nbsp:': u'\u00A0'
  , u':dottedCircle:': u'\u25CC'
}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('Input text is missing.');
    font = './generated/Jomhuria-Regular.ttf'
    if len(sys.argv) >= 3:
        font = sys.argv[2];

    print('font:', font);


    text = sys.argv[1];
    print('input:', text);
    text = replaceSpecials(text.decode('utf-8'), specials);
    text = replaceUnicodes(text);

    print('parsed:', text);

    print ('unicodes', 'u"' + (''.join(['\\u{:04X}'.format(ord(x)) for x in text])) + '"')
    row = ['rtl','arab','','',text]
    print('shaped:', runHB(row, font))
