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


from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website_best_deal.controllers.main import website_best_deal
from openerp.addons.website_sale.controllers.main import get_pricelist
from openerp.tools.translate import _


class website_best_deal(website_best_deal):

    @http.route(['/bestdeal/<model("best.deal"):best_deal>/booking'], type='http', auth="public", website=True)
    def best_deal_booking(self, best_deal, **post):
        pricelist_id = int(get_pricelist())
        values = {
            'best_deal': best_deal.with_context(pricelist=pricelist_id),
            'main_object': best_deal.with_context(pricelist=pricelist_id),
            'range': range,
        }
        return request.website.render("website_best_deal.best_deal_description_full", values)

    def _process_coupons_details(self, data):
        coupon_post = {}
        for key, value in data.iteritems():
            if not key.startswith('nb_booking') or '-' not in key:
                continue
            items = key.split('-')
            if len(items) < 2:
                continue
            coupon_post[int(items[1])] = int(value)
        coupons = request.registry['best.deal.coupon'].browse(request.cr, request.uid, coupon_post.keys(), request.context)
        return [{'id': coupon.id, 'name': coupon.name, 'quantity': coupon_post[coupon.id], 'price': coupon.price} for coupon in coupons if coupon_post[coupon.id]]

    @http.route(['/bestdeal/<model("best.deal"):best_deal>/booking/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def booking_confirm(self, best_deal, **post):
        cr, uid, context = request.cr, request.uid, request.context
        order = request.website.sale_get_order(force_create=1)
        customer_ids = set()

        bookings = self._process_booking_details(post)
        for booking in bookings:
            request.registry['best.deal.coupon'].uid = SUPERUSER_ID
            coupon = request.registry['best.deal.coupon'].with_context(context).browse(int(booking['coupon_id']))
            cart_values = order.with_context(best_deal_coupon_id=coupon.id)._cart_update(product_id=coupon.product_id.id, add_qty=1, booking_data=[booking])
            customer_ids |= set(cart_values.get('customer_ids', []))

        # free coupons -> order with amount = 0: auto-confirm, no checkout
        if not order.amount_total:
            order.action_confirm()  # tde notsure: email sending ?
            customers = request.registry['best.deal.booking'].with_context(context).browse(list(customer_ids))
            # clean context and session, then redirect to the confirmation page
            request.website.with_context(context).sale_reset()
            return request.website.render("website_best_deal.booking_complete", {
                'customers': customers,
                'best_deal': best_deal,
            })

        return request.redirect("/shop/checkout")

    def _add_best_deal(self, best_deal_name="New Deal", context={}, **kwargs):
        try:
            res_id = request.env.ref('best_deal_sale.product_product_best_deal').id
            context['default_best_deal_coupon_ids'] = [[0, 0, {
                'name': _('Subscription'),
                'product_id': res_id,
                'deadline': False,
                'coupons_max': 1000,
                'price': 0,
            }]]
        except ValueError:
            pass
        return super(WebsiteBestDeal, self)._add_best_deal(best_deal_name, context, **kwargs)
