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


    first = [].concat(
            otClasses['aKaf.init']
          , otClasses['aKaf.medi']
        ).map(Glyph.factory);
    second = [].concat(
            otClasses['aLam.medi']
          , otClasses['aLam.fina']
          , otClasses['aAlf.fina']
          , otClasses['aKaf.fina']
        ).map(Glyph.factory);
    // filler
    third = [undefined];
    third.hasLabel = false;

    first.name = 'first glyph @aKaf.init + @aKaf.medi';
    second.name = 'second glyph @aLam.medi + @aLam.fina + @aAlf.fina + @aKaf.fina';

    function getData(firstIndex, secondIndex, thirdIndex) {
        /*jshint validthis:true*/
        var glyphs = [this._items[0][firstIndex]
                , this._items[1][secondIndex]
            ]
          , i,l
          , charString = []
          , content
          , title
          ;

        // firstIndex
        charString.push(glyphs[0].mainType === 'medi' ? zwj : zwnj, glyphs[0].char);
        // secondIndex
        charString.push(glyphs[1].char, glyphs[1].mainType === 'medi' ?  zwj : '');

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
            , createElement('pre', null, 'sub [@aKaf.init @aKaf.medi]\' lookup KafLam\n\
      [@aLam.medi @aLam.fina @aAlf.fina @aKaf.fina]\' lookup KafLam;')
          ]
          , table = new Table(axes, [2, 0, 1]) //[sectionAxis, rowAxis, columnAxis]
          , state = new TableContent(info, table)
          ;
        return state.body;
    }

    return {
        title: 'issue#7-1'
      , generate: main
    };
});
