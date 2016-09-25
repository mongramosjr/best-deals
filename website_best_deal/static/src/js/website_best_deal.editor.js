odoo.define('website_best_deal.editor', function (require) {
"use strict";

var core = require('web.core');
var contentMenu = require('website.contentMenu');
var website = require('website.website');

var _t = core._t;

contentMenu.TopBar.include({
    new_best_deal: function() {
        website.prompt({
            id: "editor_new_best_deal",
            window_title: _t("New Deal"),
            input: "Deal Name",
        }).then(function (best_deal_name) {
            website.form('/bestdeal/add_bestdeal', 'POST', {
                best_deal_name: best_deal_name
            });
        });
    },
});

});
