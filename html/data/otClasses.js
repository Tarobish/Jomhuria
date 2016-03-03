define([
    '../lib/text!../../Sources/classes.fea'
],function(classes) {
    "use strict";
    var classDef = /(@[A-Za-z0-9_\.\-]+)\s*=\s*\[([^\]]*)\]\s*;/;

    function len(item) {
        return item.length;
    }

    // Note: this does not consider comments. A class definitions that
    // contains comments is parsed wrongly and a class definition that
    // is commented out is parsed anyways;
    function extractClassesFromFea(fea) {
        var _fea = fea
          , result = Object.create(null)
          , match, name, def, i,dependencyName, spliceArgs
          ;
        while((match = classDef.exec(_fea)) !== null) {
            name = match[1].slice(1);
            def = match[2];
            _fea = _fea.slice(match[0].length);
            result[name] = def.split(/\s+/).filter(len);
            // Assuming that a class in fea can only be referenced when it
            // was already defined. Otherwise, we must resolve the
            // dependency tree, which needs a bit more code.
            for(i=result[name].length-1;i>=0;i--) {
                if(result[name][i][0] !== '@')
                    continue;
                dependencyName = result[name][i].slice(1);
                if(!(dependencyName in result))
                    throw new Error('A class "@'+dependencyName+'" is not yet defined at "@'+name+'".');
                spliceArgs = [i,1];
                Array.prototype.push.apply(spliceArgs, result[dependencyName]);
                Array.prototype.splice.apply(result[name], spliceArgs);
            }
        }
        return result;
    }
    return extractClassesFromFea(classes);
});
