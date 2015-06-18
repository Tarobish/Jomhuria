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

    var first = [
            'uni0680.init'
          , 'uni0776.init'
          , 'uni06CE.init'
          , 'uni0775.init'
          , 'uni06BD.init'
          , 'uni064A.init'
          , 'uni067E.init'
          , 'uni0753.init'
          , 'uni0752.init'
          , 'uni063D.init'
          , 'uni0754.init'
          , 'uni06D1.init'
          , 'uni06CC.init'
          , 'uni0767.init'
          , 'uni0680.medi'
          , 'uni0776.medi'
          , 'uni0750.medi'
          , 'uni06CE.medi'
          , 'uni0775.medi'
          , 'uni06BD.medi'
          , 'uni064A.medi'
          , 'uni067E.medi'
          , 'uni0753.medi'
          , 'uni0752.medi'
          , 'uni063D.medi'
          , 'uni0754.medi'
          , 'uni06D1.medi'
          , 'uni06CC.medi'
          , 'uni0767.medi'
          , 'uni0680.init_High'
          , 'uni0776.init_High'
          , 'uni0750.init_High'
          , 'uni06CE.init_High'
          , 'uni0775.init_High'
          , 'uni06BD.init_High'
          , 'uni064A.init_High'
          , 'uni067E.init_High'
          , 'uni0753.init_High'
          , 'uni0752.init_High'
          , 'uni063D.init_High'
          , 'uni0754.init_High'
          , 'uni06D1.init_High'
          , 'uni06CC.init_High'
          , 'uni0767.init_High'
          , 'uni0680.medi_High'
          , 'uni0776.medi_High'
          , 'uni0750.medi_High'
          , 'uni06CE.medi_High'
          , 'uni0775.medi_High'
          , 'uni06BD.medi_High'
          , 'uni064A.medi_High'
          , 'uni067E.medi_High'
          , 'uni0753.medi_High'
          , 'uni0752.medi_High'
          , 'uni063D.medi_High'
          , 'uni0754.medi_High'
          , 'uni06D1.medi_High'
          , 'uni06CC.medi_High'
          , 'uni0767.medi_High'
          , 'uni064A.init_BaaYaaIsol'
          , 'uniFEF3'
          , 'u1EE29'
          , 'uniFB58'
          , 'uniFB5C'
          , 'uniFBFE'
    ].map(Glyph.factory).filter(filterApplicableTypes)
    , second = [
            'uni0647.medi'
          , 'uni06C1.medi'
          , 'uni0777.fina'
          , 'uni06D1.fina'
          , 'uni0775.fina'
          , 'uni063F.fina'
          , 'uni0678.fina'
          , 'uni063D.fina'
          , 'uni063E.fina'
          , 'uni06D0.fina'
          , 'uni0649.fina'
          , 'uni0776.fina'
          , 'uni06CD.fina'
          , 'uni06CC.fina'
          , 'uni0626.fina'
          , 'uni0620.fina'
          , 'uni064A.fina'
          , 'uni06CE.fina'
          , 'uni077B.fina'
          , 'uni077A.fina'
          , 'uni06D2.fina'
          , 'uni06FF.medi'
          , 'uni077B.fina_PostToothFina'
          , 'uni077A.fina_PostToothFina'
          , 'uni06D2.fina_PostToothFina'
          , 'uni0625.fina'
          , 'uni0673.fina'
          , 'uniFBA9'
          , 'uniFBAF'
          , 'uniFBE5'
          , 'uniFBFD'
          , 'uniFC10'
          , 'uniFC90'
          , 'uniFD17'
          , 'uniFD18'
          , 'uniFE8A'
          , 'uniFEF0'
          , 'uniFEF2'
    ].map(Glyph.factory).filter(filterApplicableTypes)
    ;

    var filler = [undefined];
    filler.hasLabel = false;
    first.name = 'first Glyph';
    second.name = 'second Glyph';



    var axes = {
        _items: [first, second, filler]
      , len: function(axisIndex) {
            return this._items[axisIndex].length;
        }
      , hasLabel: function (axisIndex) {
            var axis = this._items[axisIndex];
            return 'hasLabel' in axis ? !!axis.hasLabel : true;
        }
      , getData: function (firstIndex, secondIndex, fillerIndex) {
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
            // what the content is made of
            // createElement('td', {dir:'RTL'}, first.concat(
            // [zwj, nbsp, '+', nbsp, zwj], second).join(''))

            // the names of the glyphs used
            // [
            //         firstGlyph.name
            //         , createElement('sup', null, '(first)')
            //         , ' + '
            //         , secondGlyph.name
            //         , createElement('sup', null, '(second)')
            // ])
            title = [firstGlyph.name, secondGlyph.name].join(' + ');
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
            else switch(item.type) {
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
            createElement('h1', null, 'Collisions below the baseline')
          , createElement('p', null, 'The glyphs should not collide.')
          , createElement('p', null, 'Note that uniF{xxx} and u{xxxx} glyphs are not meant to '
                                    +'join properly with uni0{xxx} glyphs.')

        ]);

        var table = new Table(axes, [2, 0, 1]) //[sectionAxis, rowAxis, columnAxis]
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
        title: 'issue#6-1'
      , generate: main
    };
});
