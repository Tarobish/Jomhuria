#!/usr/bin/env python

from __future__ import print_function
from runtest import runHB

import sys
import re


def replace(inp, dictionary={}):
    pattern = '|'.join(sorted(re.escape(k) for k in dictionary))
    return re.sub(pattern, lambda m: dictionary.get(m.group(0)), inp)


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
    text = replace(text.decode('utf-8'), specials);
    print('parsed:', text);


    row = ['rtl','arab','','',text]
    print('shaped:', runHB(row, font))
