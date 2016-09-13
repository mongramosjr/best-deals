odoo.define('website_best_deal.tour', function (require) {
'use strict';

var core = require('web.core');
var Tour = require('web.Tour');
var base = require('web_editor.base');
var website = require('website.website');


var _t = core._t;

base.ready().done(function () {
    Tour.register({
        id:   'best_deal',
        name: _t("Create a deal"),
        steps: [
            {
                title:     _t("Create a Deal"),
                content:   _t("Let's go through the first steps to publish a new deal."),
                popover:   { next: _t("Start Tutorial"), end: _t("Skip It") },
            },
            {
                element:   '#content-menu-button',
                placement: 'left',
                title:     _t("Add Content"),
                content:   _t("The <em>Content</em> menu allows you to create new pages, deals, menus, etc."),
                popover:   { fixed: true },
            },
            {
                element:   'a[data-action=new_best_deal]',
                placement: 'left',
                title:     _t("New Deal"),
                content:   _t("Click here to create a new deal."),
                popover:   { fixed: true },
            },
            {
                element:   '.modal-dialog #editor_new_best_deal input[type=text]',
                sampleText: 'Boracay Summer Escapade',
                placement: 'right',
                title:     _t("Create a Deal Name"),
                content:   _t("Create a name for your new deal and click <em>'Continue'</em>. e.g: Boracay Summer Escapade"),
            },
            {
                waitNot:   '.modal-dialog #editor_new_best_deal input[type=text]:not([value!=""])',
                element:   '.modal-dialog button.btn-primary.btn-continue',
                placement: 'right',
                title:     _t("Create Deal"),
                content:   _t("Click <em>Continue</em> to create the deal."),
            },
            {
                waitFor:   '#o_scroll .oe_snippet',
                title:     _t("New Deal Created"),
                content:   _t("This is your new deal page. We will edit the deal presentation page."),
                popover:   { next: _t("Continue") },
            },
            {
                snippet:   '#snippet_structure .oe_snippet:eq(2)',
                placement: 'bottom',
                title:     _t("Drag & Drop a block"),
                content:   _t("Drag the 'Image-Text' block and drop it in your page."),
                popover:   { fixed: true },
            },
            {
                snippet:   '#snippet_structure .oe_snippet:eq(4)',
                placement: 'bottom',
                title:     _t("Drag & Drop a block"),
                content:   _t("Drag the 'Text Block' in your deal page."),
                popover:   { fixed: true },
            },
            {
                element:   'button[data-action=save]',
                placement: 'right',
                title:     _t("Save your modifications"),
                content:   _t("Once you click on save, your deal is updated."),
                popover:   { fixed: true },
            },
            {
                waitFor:   'button[data-action=edit]:visible',
                element:   'button.btn-danger.js_publish_btn',
                placement: 'top',
                title:     _t("Publish your deal"),
                content:   _t("Click to publish your deal."),
            },
            {
                waitFor:   '.js_publish_management button.js_publish_btn.btn-success:visible',
                element:   '.js_publish_management button[data-toggle="dropdown"]',
                placement: 'left',
                title:     _t("Customize your deal"),
                content:   _t("Click here to customize your deal further."),
            },
            {
                element:   '.js_publish_management ul>li>a:last:visible',
            },
        ]
    });
});

});
