define([
    'lib/domStuff'
  , 'lib/typoStuff'
  , 'lib/Table'
  , 'lib/TableContent'
], function(
    domStuff
  , typoStuff
  , Table
  , TableContent
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
      ;

    function filterApplicableTypes(glyph) {
        var type = glyph.getType('_nocontext_');
        return applicableTypes.has(type);
    }

    // I let out uniF*** and u1EE6F on purpose
    var first = [
            'uni0642.init'
          , 'uni06A8.init'
          , 'uni06A4.init'
          , 'uni06A6.init'
        ].map(Glyph.factory).filter(filterApplicableTypes)
      , second = [
            'uni0622.fina'
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
        var info = [
                createElement('h1', null, 'Collisions above the baseline with final letter Alef with Madda above')
              , createElement('p', null, 'The glyphs should not collide.')
          ]
          , table = new Table(axes, [2, 0, 1]) //[sectionAxis, rowAxis, columnAxis]
          , state = new TableContent(info, table)
          ;
        return state.body;
    }
    return {
        title: 'issue#12'
      , generate: main
    };
});
