(function(){
    "use strict";
    /*jshint laxcomma: true, laxbreak: true*/
    /*global document:true*/

    // about String.fromCodePoint: there is a polyfill if this is missing
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/fromCodePoint
    // but in here probably this will do:
    if (!String.fromCodePoint)
        String.fromCodePoint  = String.fromCharCode;

    var zwj = String.fromCodePoint(0x200D) // zero-width joiner
      , zwnj = String.fromCodePoint(0x200C)// zero-width non-joiner
      , nbsp = String.fromCodePoint(0x00A0)// no break space
      , first = [
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
          , 'uniFEF3'
          , 'uni0680.medi_YaaBari'
          , 'uni0776.medi_YaaBari'
          , 'uni0750.medi_YaaBari'
          , 'uni06CE.medi_YaaBari'
          , 'uni0775.medi_YaaBari'
          , 'uni06BD.medi_YaaBari'
          , 'uni064A.medi_YaaBari'
          , 'uni067E.medi_YaaBari'
          , 'uni0753.medi_YaaBari'
          , 'uni0752.medi_YaaBari'
          , 'uni063D.medi_YaaBari'
          , 'uni0754.medi_YaaBari'
          , 'uni06D1.medi_YaaBari'
          , 'uni06CC.medi_YaaBari'
          , 'uni0767.medi_YaaBari'
          , 'u1EE29'
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
          , 'uniFB58'
          , 'uniFB5C'
          , 'uniFBFE'
          , 'uniFEF3'
          , 'uni0680.medi_YaaBari'
          , 'uni0776.medi_YaaBari'
          , 'uni0750.medi_YaaBari'
          , 'uni06CE.medi_YaaBari'
          , 'uni0775.medi_YaaBari'
          , 'uni06BD.medi_YaaBari'
          , 'uni064A.medi_YaaBari'
          , 'uni067E.medi_YaaBari'
          , 'uni0753.medi_YaaBari'
          , 'uni0752.medi_YaaBari'
          , 'uni063D.medi_YaaBari'
          , 'uni0754.medi_YaaBari'
          , 'uni06D1.medi_YaaBari'
          , 'uni06CC.medi_YaaBari'
          , 'uni0767.medi_YaaBari'
          , 'u1EE29'
        ].map(parseName)
      , second = [
            'aHeh.medi'
          , 'aYaa.fina'
          , 'aYaa.fina_KafYaaIsol'
          , 'uni0647.medi'
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
          , 'aYaaBari.fina'
          , 'aYaaBari.fina_PostTooth'
          , 'uni077B.fina'
          , 'uni077A.fina'
          , 'uni06D2.fina'
          , 'aYaaBari.fina_PostAscender'
          , 'uni06FF.medi'
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
          , 'aYaaBari.fina_PostToothFina'
          , 'uni077B.fina_PostToothFina'
          , 'uni077A.fina_PostToothFina'
          , 'uni06D2.fina_PostToothFina'
          , 'uni0625.fina'
          , 'uni0673.fina'
        ].map(parseName)
        // second "if they have vowels"
        // TODO: need to comprehend
      , secondWithVowl = [
            'aAlf.fina'
          , 'uni0625.fina'
          , 'uni0627.fina'
          , 'uni0774.fina'
          , 'uni0773.fina'
          , 'uni0623.fina'
          , 'uni0622.fina'
          , 'uni0675.fina'
          , 'uni0672.fina'
          , 'uni0673.fina'
          , 'uni0671.fina'
          , 'uniFB51'
          , 'uniFE82'
          , 'uniFE84'
          , 'uniFE88'
          , 'uniFE8E'
          , 'u1EE6F'
        ].map(parseName)
      ;

    function toString(item) {
        return item + '';
    }


    /**
     * Be intelligent about Jomhuria char names
     *
     * returns a struct:
     * {
     *       name: name // same as input argument
     *     , code: null || int unicode codepoint
     *     , char: null || str the char for the codepoint
     *     , type: null || anthing after the '.' if the dot follows the unicode
     *     , mainType: null || if there is a type anything before the first '_' in the type
     *     , subType: null || if there is a type anything after the first '_' in the type
     * }
     */
    function parseName(name) {
        var glyph = {
                name: name
              , code: null
              , char: null
              , type: null
              , mainType: null
              , subType: null
            }
          , codeRegEx = /^(uni|u)([A-F0-9]{4,}).*/ // matches things like u1EE29* or uni1234*
          , codeMatch
          , typeDivider
          , subtypeDivider
          ;
        codeMatch = name.match(codeRegEx);
        if(codeMatch === null)
            return glyph;
        typeDivider = codeMatch[1].length + codeMatch[2].length;

        // If codeMatch[2] is not the end of the name and not followed by a dot
        // we refuse to parse the name.
        if(name.length !== typeDivider && name[typeDivider] !== '.')
            return glyph;

        glyph.code = parseInt(codeMatch[2], 16);
        glyph.char = String.fromCodePoint(glyph.code);

        // see if there is a type
        if(name[typeDivider] !== '.')
            // no type
            return glyph;

        // got a type
        glyph.type = name.slice(8);
        subtypeDivider = glyph.type.indexOf('_');
        if(subtypeDivider !== -1) {
            glyph.mainType = glyph.type.slice(0, subtypeDivider);
            glyph.subType = glyph.type.slice(subtypeDivider + 1);
        }
        else
            glyph.mainType = glyph.type;
        return glyph;
    }

    function getGlyphInContext(glyph, cantDoChar) {
        var typeContexts = {
                'init': function(char){return [zwnj, char, zwj, zwnj].join('');}
              , 'medi': function(char){return [zwnj, zwj, char, zwj, zwnj].join('');}
              , 'fina': function(char){return [zwnj, zwj, char, zwnj].join('');}
              , '_nocontext_': function(char){return [zwnj, char, zwnj].join('');}
            }
          , type = glyph.type === null  ? '_nocontext_' : glyph.type
          , nope = cantDoChar || null
          ;
        return (glyph.type in typeContexts
                    ? typeContexts[glyph.type](glyph.char)
                    : nope
               );
    }

    var colCount = 7;
    function makeGlyphRow(glyph) {
        return [ glyph.name
               , glyph.code
               , glyph.char
               , glyph.type
               , getGlyphInContext(glyph, '—')
               , glyph.mainType, glyph.subType
            ].map(toString);
    }

    function prepareGroup(data) {
        return data.map(makeGlyphRow);
    }

    function createElement(tagname, attr, contents) {
        var _contents = contents instanceof Array ? contents : [contents]
          , elem = document.createElement(tagname)
          , k, i, l, child
          ;
        if(attr) for(k in attr)
            elem.setAttribute(k, attr[k]);
        for(i=0,l=_contents.length;i<l;i++) {
            child = _contents[i];
            if(typeof child.nodeType !== 'number')
                child = document.createTextNode(child);
            elem.appendChild(child);
        }
        return elem;
    }


    function makeCell(thing) {
        return createElement('td', {dir:'RTL'}, thing);
    }

    function makeRow(cells) {
        return createElement('tr', null, cells.map(makeCell));
    }
    function makeTable(rows) {
        return createElement('tbody', null , rows.map(makeRow));
    }

    function makeTableHead(attr, text, colCount) {
        return createElement('thead', attr ,
            createElement('tr', null ,
                createElement('td', {'colspan': colCount} , text)
            )
        );
    }


    function hasChar(glyph) {
        return glyph.char !== null;
    }
    function booleanFilter(item){return !!item;}

    function combineWith(secondGlyphs, firstGlyph) {
        var type
          , firstTypeContexts = {
                'init': function(char){return [zwnj, char];}
              , 'medi': function(char){return [zwnj, zwj, char];}
              , '_nocontext_': function(char){return [zwnj, char];}
            }
          , secondTypeContexts = {
                'medi': function(char){return [char, zwj, zwnj];}
              , 'fina': function(char){return [char, zwnj];}
              , '_nocontext_': function(char){return [char, zwnj];}
            }
          , data
          , getContext = function(contexts, glyph) {
                var type = glyph.type === null ? '_nocontext_' : glyph.type;
                if(!hasChar(glyph) || !(type in contexts))
                    return [false, glyph];
                return [true, glyph, contexts[type](glyph.char)];
            }
          , combine = function(firstContext, secondContext) {
                var first, second, result;
                if(!secondContext[0])
                    return createElement('td', {dir:'LTR', colspan: 3},
                        '(no context for '+ secondContext[1].name +')');
                first = firstContext[2];
                second = secondContext[2];
                return [
                    // the names of the glyphs used
                    createElement('td', {dir:'LTR'}, [
                            firstContext[1].name
                          , createElement('sup', null, '(1)')
                          , ' + '
                          , secondContext[1].name
                          , createElement('sup', null, '(2)')
                    ])
                    // this should render the real combination:
                  , createElement('td', {dir:'RTL'}, first.concat(second).join(''))
                    // what the content is made of
                  , createElement('td', {dir:'RTL'}, first.concat(
                            [zwj, nbsp, '+', nbsp, zwj], second).join(''))
                  //, createElement('td', {dir:'LTR'}, createElement('pre',
                  //          null, JSON.stringify(secondContext[1])))
                ];
            }
          , combinations
          , content
          , first = getContext(firstTypeContexts, firstGlyph)
          ;
        if(!first[0]) {
            return createElement('div', null, createElement('h2', {dir:'LTR'}
                    , 'skipping: ' + firstGlyph.name + '(no context)'));
        }
        combinations = secondGlyphs
            .map(getContext.bind(null, secondTypeContexts))
            .map(combine.bind(null, first))
            .map(createElement.bind(null, 'tr', null))
            ;
        if(!combinations.length) {
            return createElement('div', null, createElement('h2', {dir:'LTR'}
                    , 'skipping: ' + firstGlyph.name + '(no combinations)'));
        }
        combinations.unshift(createElement('caption', null, firstGlyph.name));
        return createElement('table', {dir:'LTR'}, combinations);
    }

    function main() {
        var body = document.body;

        first.map(combineWith.bind(null, second))
            .filter(booleanFilter)
            .forEach(body.appendChild, body);



        // the general glyph information;
        [
            createElement('table', {dir:'LTR'}, [
                createElement('caption', null, 'Glyph Tables')
              , makeTableHead(null, 'first:', colCount)
              , makeTable(prepareGroup(first))
              , makeTableHead(null, 'second:', colCount)
              , makeTable(prepareGroup(second))
              , makeTableHead(null, 'secondWithVowl:', colCount)
              , makeTable(prepareGroup(secondWithVowl))
            ])
        ].forEach(body.appendChild, body);
    }
    document.addEventListener("DOMContentLoaded", main);
})();
