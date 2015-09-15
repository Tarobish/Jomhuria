define([
    'lib/domStuff'
], function(
    domStuff

) {
    "use strict";
    var createElement = domStuff.createElement
      , createElementfromMarkdown = domStuff.createElementfromMarkdown
      ;

    var title = 'Live Font Testing'
      , description = ['Hi, this is a small ["unhosted"](https://unhosted.org/) tool for font testing in the browser. It stores all your input in the ["#"](https://en.wikipedia.org/wiki/Fragment_identifier) part of the url as base64 encoded JSON. It works like this:'
        , '\n1. Enter your test content below.'
        , '* Copy the url from the address bar of your browser and share it with anyone or use it [to file a bug report](https://github.com/Tarobish/Jomhuria/issues).'
        , '* Please attach a screenshot of the rendering when reporting a bug. This archives the broken state and enables us to compare with new versions of the font.'
        ].join('\n')
      , exampleURL = '#live?eyJ2YWx1ZSI6IiMgQmlnIEhlYWRsaW5lXG4jIyMgc21hbGxlciBIZWFkbGluZVxuXG4+IEEgY29tbWVudCBhYm91dCB0aGUgZm9udCwgbGlrZSBcIlRoaXMgc2hvdWxkIGhhdmUgYSB0aWdodGVyIGtlcm5pbmdcIlxuXG5KdXN0IG5vcm1hbCB0ZXh0LiBUaGlzIGlzIFwibGVmdCB0byByaWdodFwiLCB3ZSBjYW4gYWxzbyBkbyBBcmFiaWMgXCJyaWdodC10by1sZWZ0XCIgYnV0IGJpZGlyZWN0aW9uYWwgbGFuZ3VhZ2Ugc3VwcG9ydCBpcyBub3QgdmVyeSBnb29kIGluIG1hcmtkb3duIHlldC4gV2UgZmFsbGJhY2sgdG8gaHRtbCB0byBzZXQgZXhwbGljaXQgZGlyZWN0aW9ucyB1c2luZyB0aGUgYGRpcmAgYXR0cmlidXRlIGBydGxgIGZvciBcInJpZ2h0IHRvIGxlZnRcIiBgbHRyYCBmb3IgXCJsZWZ0IHRvIHJpZ2h0XCI6XG5cbjxoMSBkaXI9XCJydGxcIj4g2K7ZiNi02YbZiNuM2LPbjCA8L2gxPlxuXG48cCBkaXI9XCJydGxcIj7YrtmI2LTZhtmI24zYs9uMINuM2Kcg2K7Yt9in2LfbjCDYqNmHINmF2LnZhtuMINiy24zYqNin2YbZiNuM2LPbjCDbjNinINmG2YjYtNiq2YYg2YfZhdix2KfZhyDYqNinINiu2YTZgiDYstuM2KjYp9uM24wg2KfYs9iqINmIINmB2LHYr9uMINqp2Ycg2KfbjNmGINmB2LHYp9uM2YbYryDYqtmI2LPYtyDYp9mIINin2YbYrNin2YUg2YXbjOKAjNqv24zYsdivINiu2YjYtCDZhtmI24zYsyDZhtin2YUg2K/Yp9ix2K/YjCDYqNmH4oCM2K7YtdmI2LUg2LLZhdin2YbbjCDaqdmHINiu2YjYtCDZhtmI24zYs9uMINit2LHZgdmHINuMINi02K7YtSDYqNin2LTYry4g2q/Yp9mH24wg2K/YsdqpINiu2YjYtNmG2YjbjNiz24wg2KjZhyDYudmG2YjYp9mGINuM2qkg2YfZhtixINmF2LTaqdmEINin2LPYqi4g2KjZhyDZhti42LEg2YXbjOKAjNix2LPYryDYqNix2KfbjCDYr9ix2qkg2Ygg2YTYsNiqINio2LHYr9mGINin2LIg2KrYrNix2KjZhyDYqNi12LHbjCDYrtmI2LTZhtmI24zYs9uMINio2KfbjNivINio2K/Yp9mG24zZhSDYrtmI2LTZhtmI24zYsyDYp9mB2LLZiNmGINio2LEg2Ybar9in2LHYtCDbjNqpINmF2KrZhtiMINiz2LnbjCDYr9in2LTYqtmHINin2KvYsduMINmH2YbYsduMINio2Kcg2KfYsdiy2LTigIzZh9in24wg2LLbjNio2KfbjNuMINi02YbYp9iu2KrbjCDYrtmE2YIg2qnZhtivLlvbsV0g2KfYsiDYp9uM2YYg2LHZiCDYrtmI2LTZhtmI24zYs9uMINio2Kcg2Ybar9in2LHYtCDYs9in2K/Zh9mUINmF2LfYp9mE2Kgg2Ygg2K3YqtinINi32LHYp9it24wg2K3YsdmI2YEg2Ygg2LXZgdit2YfigIzYotix2KfbjNuMINmF2KrZgdin2YjYqiDYp9iz2KouINmH2YXahtmG24zZhiDYp9iyINii2YbYrNin24zbjCDaqdmHINin24zZhiDZh9mG2LEg2KzZhtio2YfigIzZh9in24zbjCDYp9iyINiz2YbYqiDYsdinINiv2LEg2K/ZhCDYrtmI2K8g2K/Yp9ix2K8g2KjYp9uM2K8g2KLZhiDYsdinINiq2Kcg2K3Yr9uMINin2LIg2KrYp9uM2b7ZiNqv2LHYp9mB24wg2qnZhyDZhdio2KrZhtuMINio2LEg2KfYsdiy2LTigIzZh9in24wg2q/Ysdin2YHbjNqp24wg2YXYr9ix2YYg2Ygg2qnYp9ix2YfYp9uMINqG2KfZvtuMINin2LPYqiDZhdiq2YXYp9uM2LIg2qnYsdivLiBcbiIsImJpZGkiOiJsdHIifQ=='
      , tips = [
          '### Quick Tips:'
        , '* You can use [GitHub Flavored Markdown](https://help.github.com/articles/github-flavored-markdown/) and some plain HTML with custom CSS `style` attributes'
        , '* Use "`>`" at the beginning of a line to add comments in a sans-serif font to your example (markdown quotes).'
        , '* Use "#", "##" or "###" at the beginning of a line to create headlines.'
        , '* Use the dropdown to choose the dominant text direction and fall back to html like this `<h1 dir="rtl">right to left text</h1>` or `<p dir="ltr">Left to right text</p>` to change directions inside of specific elements.'
        , '* [here is an example](' + exampleURL + ')'
        ].join('\n')

    ;


    function FontTester(parentAPI) {
        this._parentAPI = parentAPI;
        this._currentPayload = null;

        this._input = createElement('textarea', null);
        this._dirs = createElement('select', {'class': 'dirs'}, [
            createElement('option', {'value': 'rtl', 'selected': 'selected'}, 'right-to-left')
          , createElement('option', {'value': 'ltr'}, 'left-to-right')
        ]);
        this._langs = createElement('select', {'class': 'langs'}, [
            createElement('option', {'value': 'en', 'selected': 'selected'}, 'English')
          , createElement('option', {'value': 'ar'}, 'Arabic')
        ]);


        this._usercontent = createElement('article', null);


        var pageContents = [
            createElement('h1', null, title)
          , createElementfromMarkdown('div', null, description)
          , this._input
          , this._dirs
          , this._langs
          , createElement('div', {'class':'content'}, [
                this._usercontent
              , createElementfromMarkdown('div', {'class': 'tips'}, tips)
            ])
        ];

        // public api for parent
        this.dom = createElement('div', {'class': 'live-testing'}, pageContents);

        var userInputHandler = this._userInputHandler.bind(this);
        this._input.addEventListener('input', userInputHandler);
        this._dirs.addEventListener('change', userInputHandler);
        this._langs.addEventListener('change', userInputHandler);
    }

    function getDataObject(value, bidi, lang) {
        return {
            value: value || ''
          , bidi: bidi
          , lang: lang
        };
    }

    function formatPayload(value, bidi, lang) {
        var data = getDataObject(value, bidi, lang);
        return JSON.stringify(data);
    }

    function parsePayload(payload) {
        var data;
        try {
            data = JSON.parse(payload);
        } catch(e) {
            // SyntaxError
            // handle payload as "value" string
            data = getDataObject(payload);
        }
        if(!data)
            // default
            data = getDataObject();
        return data;

    }

    var _p = FontTester.prototype;

    _p._setData = function(data) {
        // when there is more data like fontsize for example, well
        // use this function to keep it organized
        this._input.value = data.value;
        this._dirs.value = data.bidi || getSelectValue(this._dirs, 0);
        this._langs.value = data.lang || getSelectValue(this._langs, 0);
    };

    function getSelectValue(select, index) {
        return select.options[index !== undefined ? index : select.selectedIndex].value;
    }

    _p._getLanguage = function() {
        return getSelectValue(this._langs);
    };

    _p._getBidiDirection = function() {
        return getSelectValue(this._dirs);
    };

    _p._render = function() {
        var dir = this._getBidiDirection()
          , lang = this._getLanguage()
          , article = createElementfromMarkdown(
                'article'
              , {
                    dir: dir
                  , lang: lang
                }
              , this._input.value
            );
        // Change input as well, otherwise non latin users could be impaired.
        this._input.setAttribute('dir', dir)
        this._input.setAttribute('lang', lang)

        this._usercontent.parentNode.replaceChild(article,  this._usercontent);
        this._usercontent = article;
    };

    _p.payloadChangeHandler = function(payload) {
        var data = parsePayload(payload);
        this._currentPayload = payload;
        this._setData(data);
        this._render();
        // important, because this is uses as payloadChangeHandler API
        return true;
    };

    // not needed
    //_p.initHandler = function(){}

    /**
     * Run when any input element had a change.
     * Collect data from all input elements.
     * Format as payload JSON.
     * If the payload changed, set the window location hash.
     *
     * TODO: throttle this a bit!
     */
    _p._userInputHandler = function () {
        var  payload = formatPayload(
                this._input.value
              , this._getBidiDirection()
              , this._getLanguage()
            );
        // JSON.stringify is by far the easierst way to compare
        // data, it's not perfect though as for example key
        // order matters.
        if(payload === this._currentPayload)
            return;
        this._parentAPI.setPayload(payload);
    };

    function main(parentAPI) {
        return new FontTester(parentAPI);
    }
    return {
        title: title
      , generate: main
    };
});
