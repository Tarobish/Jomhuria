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
){
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
      , applicableTypes = new Set(['init','medi','fina','isol', '_nocontext_'])
      , first, second, filler, axes
      ;

    function filterApplicableTypes(glyph) {
        var type = glyph.getType('_nocontext_');
        return applicableTypes.has(type);
    }

    first = [
            'uniFED7'
          , 'uniFB6C'
          , 'uniFB70'
    ].map(Glyph.factory).filter(filterApplicableTypes);
    second = [
            'uniFE82'
    ].map(Glyph.factory).filter(filterApplicableTypes);

    filler = [undefined];
    filler.hasLabel = false;
    first.name = 'first Glyph';
    second.name = 'second Glyph';

    function getData (firstIndex, secondIndex, fillerIndex) {
        /*jshint validthis:true*/
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
                createElement('h1', null, 'Collisions above the baseline with final letter Alef with Madda above')
              , createElement('p', null, 'The glyphs should not collide.')
              , createElement('p', null, 'Note that this are legacy uniF{xxx} glyphs.')
          ]
          , table = new Table(axes, [2, 0, 1]) //[sectionAxis, rowAxis, columnAxis]
          , state = new TableContent(info, table)
          ;
        return state.body;
    }
    return {
        title: 'issue#12-legacy'
      , generate: main
    };
});
