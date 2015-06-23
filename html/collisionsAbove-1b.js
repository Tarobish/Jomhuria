define([
    'lib/domStuff'
  , 'lib/typoStuff'
  , 'lib/Table'
  , 'lib/TableContent'
  , 'lib/TableData'
], function(
    domStuff
  , typoStuff
  , Table
  , TableContent
  , TableData
) {
    "use strict";
    /*global document:true*/

    var Glyph = typoStuff.Glyph
      , zwj = typoStuff.zwj
      , zwnj = typoStuff.zwnj
      , nbsp = typoStuff.nbsp
      , dottedCircle = typoStuff.dottedCircle
      , hasChar = typoStuff.hasChar
      , createElement = domStuff.createElement
      , createFragment = domStuff.createFragment
      , appendChildren = domStuff.appendChildren
      , first, second, filler, axes
      ;

    first = [
            'uniFB64'
          , 'uniFE97'
          , 'uniFE9B'
    ].map(Glyph.factory)
    second = [
            'uniFB51'
          , 'uniFE82'
          , 'uniFE84'
          , 'uniFE88'
          , 'uniFE8E'
          , 'uniFEFC'
          , 'uniFEFA'
          , 'uniFEF8'
          , 'uniFEF6'
    ].map(Glyph.factory)

    filler = [undefined];
    filler.hasLabel = false;
    first.name = 'first Glyph';
    second.name = 'second Glyph';

    function getData (firstIndex, secondIndex, fillerIndex) {
        /*jshint validthis: true*/
        var firstGlyph = this._items[0][firstIndex]
          , secondGlyph = this._items[1][secondIndex]
          , first
          , second
          , content
          , title
          ;
        switch(firstGlyph.getType('_nocontext_')) {
            case 'init':
                first = [zwnj, firstGlyph.char];
                break;
            case 'medi':
                first = [zwnj, zwj, firstGlyph.char];
                break;
            case '_nocontext_':
                /* falls through */
            default:
                first = [zwnj, firstGlyph.char];
                break;
        }
        switch(secondGlyph.getType('_nocontext_')) {
            case 'medi':
                second = [secondGlyph.char, zwj, zwnj];
                break;
            case 'fina':
                second = [secondGlyph.char, zwnj];
                break;
            case '_nocontext_':
                /* falls through */
            default:
                second = [secondGlyph.char, zwnj];
        }

        content = first.concat(second).join('');
        title = [firstGlyph.name, secondGlyph.name].join(' + ');
        return [{dir: 'RTL', title: title}, content];
    }

    axes = new TableData(first, second, filler, getData);

    function main() {
        var info = [
                createElement('h1', null, 'Collisions above the baseline')
              , createElement('p', null, 'The glyphs should not collide.')
              , createElement('p', null, 'Note that this are legacy uniF{xxx} glyphs.')
            ]
          , table = new Table(axes, [2, 0, 1]) //[sectionAxis, rowAxis, columnAxis]
          , state = new TableContent(info, table)
          ;
        return state.body;
    }
    return {
        title: 'issue#11-legacy'
      , generate: main
    };
});
