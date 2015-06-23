define([
    'lib/domStuff'
  , 'lib/text!../README.md'
  , 'collisionsBelow-1'
  , 'collisionsBelow-2'
  , 'collisionsAbove-1'
  , 'collisionsAbove-1b'
  , 'collisionsAbove-2'
  , 'collisionsAbove-3'
  , 'collisionsAbove-3b'
  , 'lib/text!texts/persian-arabic.htmlPart'
  , 'texts/marks1'
  , 'KafLamAlf-1'
  , 'KafLamAlf-2'

], function(
    domStuff
  , README
  , collisionsBelow1
  , collisionsBelow2
  , collisionsAbove1
  , collisionsAbove1b
  , collisionsAbove2
  , collisionsAbove3
  , collisionsAbove3b
  , text1
  , marksText1
  , kafLamAlf1
  , kafLamAlf2
){
    "use strict";
    /*global document:true window:true*/

    var createElement = domStuff.createElement
      , fromHTML = domStuff.createElementfromHTML
      , fromMarkdown = domStuff.createElementfromHTML
      ;

    return {
        index: {
            title: 'Home'
          , generate: fromMarkdown.bind(null, 'article', {'class': 'home'}, README)
        }
      , tests: {
            title: 'Generated Tests'
          , '/': {
                'collision-below-1': collisionsBelow1
              , 'collision-below-2': collisionsBelow2
              , 'collision-above-1': collisionsAbove1
              , 'collision-above-1b': collisionsAbove1b
              , 'collision-above-2': collisionsAbove2
              , 'collision-above-3': collisionsAbove3
              , 'collision-above-3b': collisionsAbove3b
              , 'kaf-lam-alf-1': kafLamAlf1
              , 'kaf-lam-alf-2': kafLamAlf2
            }
        }
      , texts: {
            title: 'Test-Texts'
          , '/': {
                text1: {
                    title: 'Arabic Text 1'
                  , generate: fromHTML.bind(null, 'article', {dir: 'RTL', 'class': 'testcontent'}, text1)
                }
              , marks1: marksText1
            }
        }
    };
});
