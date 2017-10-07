# -*- coding: utf-8 -*-
##############################################################################
#
#   Sell Discount Coupons
#   Authors: Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#   Company: 3D2N World (http://www.3d2nworld.com)
#
#   Copyright 2016 Dominador B. Ramos Jr.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
##############################################################################


from odoo import http, _
from odoo.addons.website_best_deal.controllers.main import WebsiteBestDealController
from odoo.http import request


class WebsiteBestDealSaleController(WebsiteBestDealController):
    
    @http.route(['/bestdeal/<model("best.deal"):best_deal>/booking'], type='http', auth="public", website=True)
    def best_deal_booking(self, best_deal, **post):
        best_deal = best_deal.with_context(pricelist=request.website.get_current_pricelist().id)
        return super(WebsiteBestDealSaleController, self).bestdeal_booking(best_deal, **post)

    def _process_coupons_details(self, data):
        coupon_post = {}
        for key, value in data.iteritems():
            if not key.startswith('nb_booking') or '-' not in key:
                continue
            items = key.split('-')
            if len(items) < 2:
                continue
            coupon_post[int(items[1])] = int(value)
        coupons = request.env['best.deal.coupon'].browse(coupon_post.keys())
        return [{'id': coupon.id, 'name': coupon.name, 'quantity': coupon_post[coupon.id], 'price': coupon.price} for coupon in coupons if coupon_post[coupon.id]]

    @http.route(['/bestdeal/<model("best.deal"):best_deal>/booking/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def booking_confirm(self, best_deal, **post):
        order = request.website.sale_get_order(force_create=1)
        customer_ids = set()

        bookings = self._process_booking_details(post)
        for booking in bookings:
            coupon = request.env['best.deal.coupon'].sudo().browse(int(booking['coupon_id']))
            cart_values = order.with_context(best_deal_coupon_id=coupon.id, fixed_price=True)._cart_update(product_id=coupon.product_id.id, add_qty=1, booking_data=[booking])
            customer_ids |= set(cart_values.get('customer_ids', []))

        # free coupons -> order with amount = 0: auto-confirm, no checkout
        if not order.amount_total:
            order.action_confirm()  # tde notsure: email sending ?
            customers = request.env['best.deal.booking'].browse(list(customer_ids))
            # clean context and session, then redirect to the confirmation page
            request.website.sale_reset()
            return request.render("website_best_deal.booking_complete", {
                'customer_ids': customer_ids,
                'best_deal': best_deal,
            })

        return request.redirect("/shop/checkout")
        
    def _add_best_deal(self, best_deal_name="New Deal", context=None, **kwargs):
        product = request.env.ref('best_deal_sale.product_product_best_deal', raise_if_not_found=False)
        if product:
            context = dict(context or {}, default_best_deal_coupon_ids=[[0, 0, {
                'name': _('Subscription'),
                'product_id': product.id,
                'deadline': False,
                'coupons_max': 1000,
                'price': 0,
            }]])
        return super(WebsiteBestDealSaleController, self)._add_best_deal(best_deal_name, context, **kwargs)
