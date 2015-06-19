define([
    'lib/domStuff'
  , 'lib/typoStuff'
  , 'lib/Table'
], function(
    domStuff
  , typoStuff
  , Table
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
      , makeTable = domStuff.makeTable
      , makeTableHead = domStuff.makeTableHead
      , applicableTypes = new Set(['init','medi','fina','isol', '_nocontext_'])
      ;

    function filterApplicableTypes(glyph) {
        var type = glyph.getType('_nocontext_');
        return applicableTypes.has(type);
    }


    // I let out uniF*** and u1EE6F on purpose
    var first = [
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
        ].map(Glyph.factory).filter(filterApplicableTypes)
    , second = [
          // the uni0XXX.medi_LamAlfFina occur
          // when the uni076A.medi char meets an alef.fina char

          // NOTE: in classes.fea (* is in our list)
          // This is exactly the same group!
          // @aLam.medi_LamAlfFina = [
          //    uni06B5.medi_LamAlfFina*
          //    uni06B7.medi_LamAlfFina*
          //    uni0644.medi_LamAlfFina*
          //    uni06B8.medi_LamAlfFina*
          //    uni06B6.medi_LamAlfFina*
          //    uni076A.medi_LamAlfFina*
          //    ];
            'uni076A.medi'//_LamAlfFina'
          , 'uni06B6.medi'//_LamAlfFina'
          , 'uni06B8.medi'//_LamAlfFina'
          , 'uni0644.medi'//_LamAlfFina'
          , 'uni06B7.medi'//_LamAlfFina'
          , 'uni06B5.medi'//_LamAlfFina'
    ].map(Glyph.factory).filter(filterApplicableTypes)
    , third = [
          // these are all glyph required to trigger second
          // this group will be substituted in the same lookup
          // see also lookup LamAlfFina in contextuals fea
          // @aAlf.fina_LamAlfFina = [
          //    uni0625.fina_LamAlfFina
          //    uni0627.fina_LamAlfFina
          //    uni0774.fina_LamAlfFina
          //    uni0773.fina_LamAlfFina
          //    uni0623.fina_LamAlfFina
          //    uni0622.fina_LamAlfFina
          //    uni0675.fina_LamAlfFina
          //    uni0672.fina_LamAlfFina
          //    uni0673.fina_LamAlfFina
          //    uni0671.fina_LamAlfFina
          //    ];
            'uni0625.fina'//_LamAlfFina
          , 'uni0627.fina'//_LamAlfFina
          , 'uni0774.fina'//_LamAlfFina
          , 'uni0773.fina'//_LamAlfFina
          , 'uni0623.fina'//_LamAlfFina
          , 'uni0622.fina'//_LamAlfFina
          , 'uni0675.fina'//_LamAlfFina
          , 'uni0672.fina'//_LamAlfFina
          , 'uni0673.fina'//_LamAlfFina
          , 'uni0671.fina'//_LamAlfFina
    ].map(Glyph.factory).filter(filterApplicableTypes)
    ;


    first.name = 'first Glyph';
    second.name = 'second Glyph Lam';
    third.name = 'third Glyph Alef';



    var axes = {
        _items: [first, second, third]
      , len: function(axisIndex) {
            return this._items[axisIndex].length;
        }
      , hasLabel: function (axisIndex) {
            var axis = this._items[axisIndex];
            return 'hasLabel' in axis ? !!axis.hasLabel : true;
        }
      , getData: function (firstIndex, secondIndex, thirdIndex) {
            var glyphs = [this._items[0][firstIndex]
                    , this._items[1][secondIndex]
                    , this._items[2][thirdIndex]
                ]
              , i,l
              , charString = []
              , content
              , title
              ;

            // firstIndex is all init at the moment
            charString.push(zwnj, glyphs[0].char);
            // secondIndex is all medi at the moment
            charString.push(glyphs[1].char);
            // secondIndex is all fina at the moment
            charString.push(glyphs[2].char, zwnj);

            content = charString.join('');
            title = glyphs.map(function(glyph){ return glyph.name; }).join(' + ');
            return [{dir: 'RTL', title: title}, content];
        }
        /**
         * `type`, string: one of 'section', 'row', 'column'
         */
      , getLabel: function (axisIndex, itemIndex, type) {
            var axis = this._items[axisIndex]
            , item = axis[itemIndex]
            , axisName = axis.name
            , attr = {dir: 'LTR'}
            , content, str, char
            ;
            attr.title = axisName + ': '+ item.name;
            if(axis.isMark)
                str = [dottedCircle, item.char, nbsp];
            else switch(item.mainType) {
                case 'init':
                    str = [nbsp, zwnj, item.char, zwj, nbsp];
                    break;
                case 'medi':
                    str = [nbsp, zwj, item.char, zwj, nbsp];
                    break;
                case 'fina':
                    str = [nbsp, zwj, item.char, zwnj, nbsp];
                    break;
                default:
                    str = [nbsp, zwnj, item.char, zwnj, nbsp];
            }
            char = createElement('span', {dir: 'RTL'},  str.join(''));
            switch (type) {
                case 'column':
                    // very short label
                    content = char;
                    break;
                // long labels
                case 'section':
                    content = axisName + ': ';
                    /* falls through */
                case 'row':
                    /* falls through */
                default:
                    content = (content && [content] || []).concat(item.name, char);
                break;
            }
            return [attr, createFragment(content)];
        }
    };

    function main() {
        var body = createElement('article', null, [
            createElement('h1', null, 'Collisions above the baseline')
          , createElement('p', null, 'The first glyph should not collide with the second glyph.')
          , createElement('p', null, 'The combination of medial form second glyph and final form '
                          + 'third glyph triggers this specific shaping of second and third glyph.')
        ]);

        var table = new Table(axes, [0, 1, 2]) //[sectionAxis, rowAxis, columnAxis]
          , mode = 'default' // "doubleColumns" or "doubleRows" or it defaults (to "default")
          , hasSectionLabel = true
          , hasRowLabel = true
          , hasColumnLabel = true
          ;
        body.appendChild(
            createElement('table', {dir: 'RTL', 'class': 'testcontent'},
                    table.render(mode, hasSectionLabel, hasRowLabel, hasColumnLabel)));
        return body;
    }
    return {
        title: 'issue#11-2 (LamAlfFina)'
      , generate: main
    };
});
