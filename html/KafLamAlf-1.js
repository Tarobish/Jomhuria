define([
    'lib/domStuff'
  , 'lib/typoStuff'
  , 'lib/Table'
  , 'lib/TableContent'
  , 'lib/TableData'
  , 'data/otClasses'
], function(
    domStuff
  , typoStuff
  , Table
  , TableContent
  , TableData
  , otClasses
){
    "use strict";
    /*global document:true*/

    var Glyph = typoStuff.Glyph
      , zwj = typoStuff.zwj
      , zwnj = typoStuff.zwnj
      , nbsp = typoStuff.nbsp
      , dottedCircle = typoStuff.dottedCircle
      , createElement = domStuff.createElement
      , createFragment = domStuff.createFragment
      , first, second, third, axes
      ;

    first = [].concat(otClasses['aKaf.init'], otClasses['aKaf.medi'])
        .map(Glyph.factory);
    // otClasses['aLam.medi_LamAlfFina'] produces the same input
    // one is enough
    second = otClasses['aLam.medi'].slice() // make a copy
        .map(Glyph.factory);
    // otClasses['aAlf.fina_LamAlfFina'] produces the same input
    // one is enough
    third = otClasses['aAlf.fina'].slice() // make a copy
        .map(Glyph.factory);

    first.name = 'first glyph @aKaf.init + @aKaf.medi';
    second.name = 'second glyph @aLam.medi';
    third.name = 'third glyph @aAlf.fina';
    function getData (firstIndex, secondIndex, thirdIndex) {
        /*jshint validthis: true*/
        var glyphs = [this._items[0][firstIndex]
                , this._items[1][secondIndex]
                , this._items[2][thirdIndex]
            ]
          , i,l
          , charString = []
          , content
          , title
          ;

        // firstIndex
        charString.push(glyphs[0].mainType === 'medi' ? zwj : zwnj, glyphs[0].char);
        // secondIndex
        charString.push(glyphs[1].char);
        // thirdIndex
        charString.push(glyphs[2].char, zwnj);

        content = charString.join('');
        title = glyphs.map(function(glyph){ return glyph.name; }).join(' + ');
        return [{dir: 'RTL', title: title}, content];
    }
    axes = new TableData(first, second, third, getData);

    function main() {
        /*jshint multistr:true*/
        var info = [
              createElement('h1', null, 'The Combination Kaf-Lam-Alf has special substitutions')
            , createElement('p', null, 'This is to test:')
            , createElement('pre', null, '  sub [@aKaf.init @aKaf.medi]\' lookup KafLam\n\
      [@aLam.medi @aLam.medi_LamAlfFina]\' lookup KafLamAlf\n\
      [@aAlf.fina @aAlf.fina_LamAlfFina];')
          ]
          , table = new Table(axes, [0, 1, 2]) //[sectionAxis, rowAxis, columnAxis]
          , state = new TableContent(info, table)
          ;
        return state.body;
    }

    return {
        title: 'issue#7-1'
      , generate: main
    };
});
