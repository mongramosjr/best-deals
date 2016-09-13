odoo.define('website_best_deal_sale.tour', function (require) {
'use strict';

var Tour = require('web.Tour');
var base = require('web_editor.base');
var website = require('website.website');

base.ready().done(function () {
    Tour.booking({
        id:   'best_deal_buy_coupons',
        name: "Buy coupons for the Boracay Summer Escapade",
        path: '/bestdeal',
        mode: 'test',
        steps: [
            {
                title:     "Go to the `Deal` page",
                element:   'a[href*="/bestdeal"]:contains("Boracay Summer Escapade"):first',
            },
            {
                title:     "Select 1 unit of `Standard` coupon type",
                waitNot:   'a[href*="/bestdeal"]:contains("Boracay Summer Escapade")',
                element:   'select:eq(0)',
                sampleText: '1',
            },
            {
                title:     "Select 2 units of `VIP` coupon type",
                waitFor:   'select:eq(0) option:contains(1):propSelected',
                element:   'select:eq(1)',
                sampleText: '2',
            },
            {
                title:     "Click on `Order Now` button",
                waitFor:   'select:eq(1) option:contains(2):propSelected',
                element:   '.btn-primary:contains("Order Now")',
            },
            {
                title:     "Fill customers details",
                waitFor:   'form[id="customer_booking"] .btn:contains("Continue")',
                autoComplete: function (tour) {
                    $("input[name='1-name']").val("Att1");
                    $("input[name='1-phone']").val("111 111");
                    $("input[name='1-email']").val("att1@example.com");
                    $("input[name='2-name']").val("Att2");
                    $("input[name='2-phone']").val("222 222");
                    $("input[name='2-email']").val("att2@example.com");
                    $("input[name='3-name']").val("Att3");
                    $("input[name='3-phone']").val("333 333");
                    $("input[name='3-email']").val("att3@example.com");
                },
            },
            {
                title:     "Validate custoimers details",
                waitFor:   "input[name='1-name'], input[name='2-name'], input[name='3-name']",
                element:   '.modal button:contains("Continue")',
            },
            {
                title:     "Check that the cart contains exactly 3 elements",
                element:   'a:has(.my_cart_quantity:containsExact(3))',
            },
            {
                title:     "Modify the cart to add 1 unit of `VIP` coupon type",
                waitFor:   "#cart_products:contains(Standard):contains(VIP)",
                element:   "#cart_products tr:contains(VIP) .fa-plus",
            },
            {
                title:     "Now click on `Process Checkout`",
                waitFor:   'a:has(.my_cart_quantity):contains(4)',
                element:   '.btn-primary:contains("Process Checkout")'
            },
            {
                title:     "Complete the checkout",
                element:   'form[action="/shop/confirm_order"] .btn:contains("Confirm")',
                onload: function () {
                    if ($("input[name='name']").val() === "")
                        $("input[name='name']").val("website_sale-test-shoptest");
                    if ($("input[name='email']").val() === "")
                        $("input[name='email']").val("website_best_deal_sale_test_shoptest@websitedealsaletest.3d2nworld.com");
                    $("input[name='phone']").val("123");
                    $("input[name='street2']").val("123");
                    $("input[name='city']").val("123");
                    $("input[name='zip']").val("123");
                    $("select[name='country_id']").val("21");
                },
            },
            {
                title:     "Check that the subtotal is 5,500.00",
                element:   '#order_total_untaxed .oe_currency_value:contains("5,500.00")',
            },
            {
                title:     "Select `Wire Transfer` payment method",
                element:   '#payment_method label:has(img[title="Wire Transfer"]) input',
            },
            {
                title:     "Pay",
                waitFor:   '#payment_method label:has(input:checked):has(img[title="Wire Transfer"])',
                element:   '.oe_sale_acquirer_button .btn[type="submit"]:visible',
            },
            {
                title:     "Last step",
                waitFor:   '.oe_website_sale:contains("Thank you for your order")',
            }
        ]
    });
});

});
