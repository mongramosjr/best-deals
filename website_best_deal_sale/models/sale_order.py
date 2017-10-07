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

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        self.ensure_one()
        lines = super(SaleOrder, self)._cart_find_product_line(product_id, line_id)
        if line_id:
            return lines
        domain = [('id', 'in', lines.ids)]
        if self.env.context.get("best_deal_coupon_id"):
            domain.append(('best_deal_coupon_id', '=', self.env.context.get("best_deal_coupon_id")))
        return self.env['sale.order.line'].sudo().search(domain)
        
    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0):
        order = self.env['sale.order'].sudo().browse(order_id)
        if self._context.get('pricelist') != order.pricelist_id.id:
            self = self.with_context(pricelist=order.pricelist_id.id)

        values = super(SaleOrder, self)._website_product_id_change(order_id, product_id, qty=qty)
        best_deal_coupon_id = None
        if self.env.context.get("best_deal_coupon_id"):
            best_deal_coupon_id = self.env.context.get("best_deal_coupon_id")
        else:
            product = self.env['product.product'].browse(product_id)
            if product.best_deal_coupon_ids:
                best_deal_coupon_id = product.best_deal_coupon_ids[0].id

        if best_deal_coupon_id:
            coupon = self.env['best.deal.coupon'].browse(best_deal_coupon_id)
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

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        OrderLine = self.env['sale.order.line']

        if line_id:
            line = OrderLine.browse(line_id)
            coupon = line.best_deal_coupon_id
            old_qty = int(line.product_uom_qty)
            if coupon.id:
                self = self.with_context(best_deal_coupon_id=coupon.id, fixed_price=1)
        else:
            line = None
            coupon = self.env['best.deal.coupon'].search([('product_id', '=', product_id)], limit=1)
            old_qty = 0
        new_qty = set_qty if set_qty else (add_qty or 0 + old_qty)

        # case: buying coupons for a sold out coupon
        values = {}
        if coupon and coupon.coupons_availability == 'limited' and coupon.coupons_available <= 0:
            values['warning'] = _('Sorry, The %(coupon)s coupons for the %(best_deal)s deal are sold out.') % {
                'coupon': coupon.name,
                'best_deal': coupon.best_deal_id.name}
            new_qty, set_qty, add_qty = 0, 0, 0
        # case: buying coupons, too much attendees
        elif coupon and coupon.coupons_availability == 'limited' and new_qty > coupon.coupons_available:
            values['warning'] = _('Sorry, only %(remaining_coupons)d coupons are still available for the %(coupon)s coupon for the %(best_deal)s deal.') % {
                'remaining_coupons': coupon.coupons_available,
                'coupon': coupon.name,
                'best_deal': coupon.best_deal_id.name}
            new_qty, set_qty, add_qty = coupon.coupons_available, coupon.coupons_available, 0
        values.update(super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs))

        # removing customers
        if coupon and new_qty < old_qty:
            customers = self.env['best.deal.booking'].search([
                ('state', '!=', 'cancel'),
                ('sale_order_id', 'in', self.ids),  # To avoid break on multi record set
                ('best_deal_coupon_id', '=', coupon.id),
            ], offset=new_qty, limit=(old_qty - new_qty), order='create_date asc')
            customers.button_reg_cancel()
        # adding customers
        elif coupon and new_qty > old_qty:
            line = OrderLine.browse(values['line_id'])
            line._update_bookings(confirm=False, booking_data=kwargs.get('booking_data', []))
            # add in return values the bookings, to display them on website (or not)
            values['customer_ids'] = self.env['best.deal.booking'].search([('sale_order_line_id', '=', line.id), ('state', '!=', 'cancel')]).ids
        return values
        
