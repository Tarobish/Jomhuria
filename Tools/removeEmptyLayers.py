#! /usr/bin/env python

# sortsmill can't use glyphs with empty background layers in the form of:
# Back
# Fore
# This just removes "Back\n" when it is present in the combination "Back\nFore"
import os

def removeEmptyBack(filename):
    file = open(filename, 'r+')
    content = file.read()
    changed = False

    pos = content.find('Back\nFore');
    if pos != -1:
        content = content[:pos] + content[pos + len('Back\n'):]
        changed = True
        print 'found Back', filename

    pos = content.find('Fore\nColour');
    if pos != -1:
        content = content[:pos] + content[pos + len('Fore\n'):]
        changed = True
        print 'found Fore', filename

    if not changed:
        return

    file.seek(0)
    file.truncate()
    file.write(content)


if __name__ == '__main__':
    dirs = ('./sources/jomhuria.sfdir', './sources/jomhuria-latin.sfdir')
    for directory in dirs:
        files = [os.path.join(root, name) for root, _, files in os.walk('.')
                            for name in files if name.endswith('.glyph')]
        for f in files: removeEmptyBack(f)
