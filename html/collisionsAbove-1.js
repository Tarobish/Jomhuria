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
      , applicableTypes = new Set(['init','medi','fina','isol', '_nocontext_'])
      , first, second, filler, axes
      ;

    function filterApplicableTypes(glyph) {
        var type = glyph.getType('_nocontext_');
        return applicableTypes.has(type);
    }

    // I let out uniF*** and u1EE6F on purpose
    first = [
            'uni0753.init'
          , 'uni0751.init'
          , 'uni067D.init'
          , 'uni067F.init'
          , 'uni067C.init'
          , 'uni062B.init'
          , 'uni062A.init'
        //  , 'uniFB64'
        //  , 'uniFE97'
        //  , 'uniFE9B'
        //  , 'u1EE35'
        //  , 'u1EE36'
    ].map(Glyph.factory).filter(filterApplicableTypes);
    second = [

        //    'aAlf.fina'
            'uni0625.fina'
          , 'uni0627.fina'
          , 'uni0774.fina'
          , 'uni0773.fina'
          , 'uni0623.fina'
          , 'uni0622.fina'
          , 'uni0675.fina'
          , 'uni0672.fina'
          , 'uni0673.fina'
          , 'uni0671.fina'
        //  , 'uniFB51'
        //  , 'uniFE82'
        //  , 'uniFE84'
        //  , 'uniFE88'
        //  , 'uniFE8E'
        //  , 'u1EE6F'
        //  , 'aLam.medi_LamAlfFina'
        //  , 'aAlf.fina'
        //  , 'uni076A.medi_LamAlfFina' // TODO: *.medi_LamAlfFina how are these triggered?
        //  , 'uni06B6.medi_LamAlfFina'
        //  , 'uni06B8.medi_LamAlfFina'
        //  , 'uni0644.medi_LamAlfFina'
        //  , 'uni06B7.medi_LamAlfFina'
        //  , 'uni06B5.medi_LamAlfFina'
        //  , 'uniFEFC'
        //  , 'uniFEFA'
        //  , 'uniFEF8'
        //  , 'uniFEF6'
    ].map(Glyph.factory).filter(filterApplicableTypes);

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
              , createElement('p', null, 'Note that uniF{xxx} and u{xxxx} glyphs are filtered.')
            ]
          , table = new Table(axes, [2, 0, 1]) //[sectionAxis, rowAxis, columnAxis]
          , state = new TableContent(info, table)
          ;
        return state.body;
    }
    return {
        title: 'issue#11'
      , generate: main
    };
});
