require([
    'lib/domStuff'
  , 'lib/typoStuff'
], function(
    domStuff
  , typoStuff
){
    "use strict";
    /*jshint laxcomma: true, laxbreak: true*/
    /*global document:true*/

    var Glyph = typoStuff.Glyph
      , zwj = typoStuff.zwj
      , zwnj = typoStuff.zwnj
      , nbsp = typoStuff.nbsp
      , hasChar = typoStuff.hasChar
      , createElement = domStuff.createElement
      , makeTable = domStuff.makeTable
      , makeTableHead = domStuff.makeTableHead
      ;

    function main() {
        var body = document.body
          , alefFina = Glyph.factory('uni0627.fina')
          , marksBelow = [


              'uni0655' // becomes uni0625.fina
              // , 'uni064D', 'uni08F2', 'uni064D.small'

               , 'uni065F'// becomes uni0673.fina
              //
              // , 'uni0650' , 'uni0650.small' , 'uni0650.small2'
              //
               , 'uni0656'
              // , 'uni061A'
              //
              // , 'uni06ED'
              // , 'uni065C'
              // , 'uni0325'
              // , 'uni08E6'
              // , 'uni08E9'
            ].map(Glyph.factory)
          , kashida = Glyph.factory('uni0640')
          , i,l
          , items = []
          ;


        // TODO: this produces colisions sometimes
        // sometimes it is not displayed and sometimes it just works
        // alefFina.char + marksBelow[i].char + Glyph.factory('uni0650').char +zwnj


        for(i=0,l=marksBelow.length;i<l;i++)
            items.push(
                createElement('p', {dir:'RTL'}, zwnj + kashida.char +  kashida.char +  kashida.char + kashida.char + alefFina.char + marksBelow[i].char + zwnj)
              , createElement('p', {dir:'RTL'}, zwnj + kashida.char + zwj + alefFina.char + marksBelow[i].char + zwnj)
            );


        items.map(body.appendChild, body)
    }


    domStuff.onLoad(main);
});
