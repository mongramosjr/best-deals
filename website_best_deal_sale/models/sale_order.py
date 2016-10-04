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

from openerp import models, fields, api, SUPERUSER_ID, _
from openerp.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_find_product_line(self, cr, uid, ids, product_id=None, line_id=None, context=None, **kwargs):
        line_ids = super(SaleOrder, self)._cart_find_product_line(cr, uid, ids, product_id, line_id, context=context)
        if line_id:
            return line_ids
        for so in self.browse(cr, uid, ids, context=context):
            domain = [('id', 'in', line_ids)]
            if context.get("best_deal_coupon_id"):
                domain += [('best_deal_coupon_id', '=', context.get("best_deal_coupon_id"))]
            return self.pool.get('sale.order.line').search(cr, SUPERUSER_ID, domain, context=context)

    def _website_product_id_change(self, cr, uid, ids, order_id, product_id, qty=0, context=None):
        values = super(SaleOrder, self)._website_product_id_change(cr, uid, ids, order_id, product_id, qty=qty, context=None)

        best_deal_coupon_id = None
        if context.get("best_deal_coupon_id"):
            best_deal_coupon_id = context.get("best_deal_coupon_id")
        else:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            if product.best_deal_coupon_ids:
                best_deal_coupon_id = product.best_deal_coupon_ids[0].id

        if best_deal_coupon_id:
            order = self.pool['sale.order'].browse(cr, SUPERUSER_ID, order_id, context=context)
            coupon = self.pool.get('best.deal.coupon').browse(cr, uid, best_deal_coupon_id, context=dict(context, pricelist=order.pricelist_id.id))
            if product_id != coupon.product_id.id:
                raise UserError(_("The coupon doesn't match with this product."))

            values['product_id'] = coupon.product_id.id
            values['best_deal_id'] = coupon.best_deal_id.id
            values['best_deal_coupon_id'] = coupon.id
            values['price_unit'] = coupon.price_reduce or coupon.price
            values['name'] = "%s\n%s" % (coupon.best_deal_id.display_name, coupon.name)

        # avoid writing related values that end up locking the product record
        values.pop('best_deal_type_id', None)
        values.pop('best_deal_ok', None)

        return values

    def _cart_update(self, cr, uid, ids, product_id=None, line_id=None, add_qty=0, set_qty=0, context=None, **kwargs):
        OrderLine = self.pool['sale.order.line']
        Customer = self.pool['best.deal.booking']
        Coupon = self.pool['best.deal.coupon']

        if line_id:
            line = OrderLine.browse(cr, uid, line_id, context=context)
            coupon = line.best_deal_coupon_id
            old_qty = int(line.product_uom_qty)
            context = dict(context, best_deal_coupon_id=coupon.id)
        else:
            line, coupon = None, None
            coupon_ids = Coupon.search(cr, uid, [('product_id', '=', product_id)], limit=1, context=context)
            if coupon_ids:
                coupon = Coupon.browse(cr, uid, coupon_ids[0], context=context)
            old_qty = 0
        new_qty = set_qty if set_qty else (add_qty or 0 + old_qty)

        # case: buying coupons for a sold out coupon
        values = {}
        if coupon and coupon.coupons_availability == 'limited' and coupon.coupons_available <= 0:
            values['warning'] = _('Sorry, The %(coupon)s coupons for the %(best_deal)s deal are sold out.') % {
                'coupon': coupon.name,
                'best_deal': coupon.best_deal_id.name}
            new_qty, set_qty, add_qty = 0, 0, 0
        # case: buying coupons, too much customers
        elif coupon and coupon.coupons_availability == 'limited' and new_qty > coupon.coupons_available:
            values['warning'] = _('Sorry, only %(remaining_coupons)d coupons are still available for the %(coupon)s coupon for the %(best_deal)s deal.') % {
                'remaining_coupons': coupon.coupons_available,
                'coupon': coupon.name,
                'best_deal': coupon.best_deal_id.name}
            new_qty, set_qty, add_qty = coupon.coupons_available, coupon.coupons_available, 0

        values.update(super(SaleOrder, self)._cart_update(
            cr, uid, ids, product_id, line_id, add_qty, set_qty, context, **kwargs))

        # removing customers
        if coupon and new_qty < old_qty:
            customers = Customer.search(
                cr, uid, [
                    ('state', '!=', 'cancel'),
                    ('sale_order_id', '=', ids[0]),
                    ('best_deal_coupon_id', '=', coupon.id)
                ], offset=new_qty, limit=(old_qty-new_qty),
                order='create_date asc', context=context)
            Customer.button_reg_cancel(cr, uid, customers, context=context)
        # adding customers
        elif coupon and new_qty > old_qty:
            line = OrderLine.browse(cr, uid, values['line_id'], context=context)
            line._update_bookings(confirm=False, booking_data=kwargs.get('booking_data', []))
            # add in return values the bookings, to display them on website (or not)
            values['customer_ids'] = Customer.search(cr, uid, [('sale_order_line_id', '=', line.id), ('state', '!=', 'cancel')], context=context)
        return values
