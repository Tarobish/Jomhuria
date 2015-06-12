define([
    'lib/domStuff'
  , 'lib/marked'
  , 'lib/text!/README.md'
  , 'collisionsBelow-1'
  , 'collisionsBelow-2'
], function(
    domStuff
  , marked
  , README
  , collisionsBelow1
  , collisionsBelow2
){
    "use strict";
    /*global document:true window:true*/

    return {
        index: {
            title: 'Home'
          ,  generate: function() {
                var element = domStuff.createElement('article', {'class': 'home'});
                element.innerHTML = marked(README, {gfm: true});
                return element;
            }
        }
      , tests: {
            tile: 'testDocs'
          , '/': {
                'collision-below-1': collisionsBelow1
              , 'collision-below-2': collisionsBelow2
            }
        }
    };
});
