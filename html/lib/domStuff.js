define([
    './marked'
], function(
    marked
){
    "use strict";
    /*jshint laxcomma: true, laxbreak: true*/
    /*global document:true setTimeout:true*/

    function createElement(tagname, attr, contents) {
        var _contents
          , elem = document.createElement(tagname)
          , k, i, l, child
          ;

        if(contents === undefined)
            _contents = [];
        else
            _contents = contents instanceof Array ? contents : [contents];

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

    function onLoad(main, doc) {
        var _doc = doc || document;
        if(_doc.readyState === 'complete')
            // make it async to reduce confusion
            setTimeout(main, 0);
        else
            _doc.addEventListener("DOMContentLoaded", main);
    }

    function createElementfromHTML(tag, attr, innerHTMl) {
        var element = createElement(tag, attr);
        element.innerHTML = marked(innerHTMl, {gfm: true});
        return element;
    }

    function createElementfromMarkdown(tag, attr, mardownText) {
        return createElementfromHTML(tag, attr, marked(mardownText, {gfd: true}));
    }

    return {
        createElement: createElement
      , makeCell: makeCell
      , makeRow: makeRow
      , makeTable: makeTable
      , makeTableHead: makeTableHead
      , onLoad: onLoad
      , createElementfromHTML: createElementfromHTML
      , createElementfromMarkdown: createElementfromMarkdown
    };
});
