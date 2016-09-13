odoo.define('website_best_deal.geolocation', function (require) {
"use strict";

var animation = require('web_editor.snippets.animation');

animation.registry.visitor = animation.Class.extend({
    selector: ".oe_country_best_deals",
    start: function () {
        $.get("/bestdeal/get_country_best_deal_list").then(function( data ) {
            if(data){
                $( ".country_best_deals_list" ).replaceWith( data );
            }
        });
    }
});

});
