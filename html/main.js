require([
    'lib/domStuff'
  , 'pages'
], function(
    domStuff
  , pages
) {
    "use strict";
    /*global document:true window:true*/

    var createElement = domStuff.createElement
      , makeTable = domStuff.makeTable
      , makeTableHead = domStuff.makeTableHead
      ;


    function getPage(pages, fallback) {
        var hash = window.location.hash, path, piece, dir, page;
        hash = hash.length ? hash.slice(1) : hash;
        if(hash === '')
            hash = 'index';

        path = hash.split('/');
        dir = pages;
        while((piece = path.shift()) !== undefined) {
            if(piece === '') continue;
            if(!dir) {
                page = undefined;
                break;
            }
            page = dir[piece];
            if(!page) break;
            dir = page['/'];
        }
        if(page)
            return page;
        else if (fallback !== undefined && (fallback || 'index') in pages)
            return pages[fallback || 'index'];
        return undefined;
    }

    function showPage(target, page) {
        while(target.lastChild)
            target.removeChild(target.lastChild);
        var href = window.location.href;
        target.ownerDocument.title = page.title;
        target.appendChild(page.generate());
    }

    function renderMenu(target, pages, prefix) {
        var k
          , child
          , children = []
          , _prefix = prefix || ''
          , here
          ;
        for(k in pages) {
            here = _prefix + k;
            child = createElement('li', null);
            children.push(child);

            if(pages[k].generate)
                child.appendChild(createElement('a', {href: '#' + here}, pages[k].title));
            else if(pages[k].title)
                child.appendChild(createElement('span', null, pages[k].title));

            if(pages[k]['/'])
                renderMenu(child, pages[k]['/'], here + '/');
        }
        target.appendChild(createElement('ul', {dir:'LTR'}, children));
    }

    function main() {
        var body = document.body
          , content = createElement('main', {lang: 'fr', dir:'LTR'})
          , nav = createElement('nav')
          ;
        function switchPageHandler(e) {
            var page = getPage(pages);
            if(!page) return;
            e.preventDefault();
            showPage(content, page);
        }
        body.appendChild(nav);
        body.appendChild(content);
        renderMenu(nav, pages);
        showPage(content, getPage(pages, 'index'));

        // Listen to hash changes.
        window.addEventListener('hashchange', switchPageHandler, false);
    }
    domStuff.onLoad(main);
});
