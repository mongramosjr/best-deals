# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Sell Discount Coupons
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Sell Discount Coupons and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

from openerp import models, fields, api, SUPERUSER_ID, _
from openerp.tools.translate import _
from openerp.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        self.env.uid = SUPERUSER_ID
        line_ids = super(SaleOrder, self)._cart_find_product_line(product_id, line_id)
        if line_id:
            return line_ids
        for sale_order in self:
            domain = [('id', 'in', line_ids)]
            if context.get("best_deal_coupon_id"):
                domain += [('best_deal_coupon_id', '=', context.get("best_deal_coupon_id"))]
            return self.env['sale.order.line'].search(domain)

    def _website_product_id_change(self, order_id, product_id, qty=0):
        context = self._context or {}
        self.env.uid = SUPERUSER_ID
        values = super(SaleOrder, self)._website_product_id_change(order_id, product_id, qty=qty)

        best_deal_coupon_id = None
        if context.get("best_deal_coupon_id"):
            best_deal_coupon_id = context.get("best_deal_coupon_id")
        else:
            product = self.env['product.product'].browse(product_id)
            if product.best_deal_coupon_ids:
                best_deal_coupon_id = product.best_deal_coupon_ids[0].id

        if best_deal_coupon_id:
            order = self.env['sale.order'].browse(order_id)
            ctx = dict(self._context or {})
            ctx['pricelist'] = order.pricelist_id.id
            coupon = self.env['best.deal.coupon'].with_context(ctx).browse(best_deal_coupon_id)
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

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        context = self._context or {}
        OrderLine = self.env['sale.order.line']
        Customer = self.env['best.deal.booking']
        Coupon = self.env['best.deal.coupon']

        if line_id:
            line = OrderLine.browse(line_id)
            coupon = line.best_deal_coupon_id
            old_qty = int(line.product_uom_qty)
            context = dict(context, best_deal_coupon_id=coupon.id)
        else:
            line, coupon = None, None
            coupon_ids = Coupon.search([('product_id', '=', product_id)], limit=1)
            if coupon_ids:
                coupon = Coupon.browse(coupon_ids[0])
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

        values.update(super(SaleOrder, self).with_context(context)._cart_update(product_id, line_id, add_qty, set_qty))

        # removing customers
        if coupon and new_qty < old_qty:
            customers = Customer.with_context(context).search([
                    ('state', '!=', 'cancel'),
                    ('sale_order_id', '=', ids[0]),
                    ('best_deal_coupon_id', '=', coupon.id)
                ], offset=new_qty, limit=(old_qty-new_qty),
                order='create_date asc')
            Customer.with_context(context).button_reg_cancel(customers)
        # adding customers
        elif coupon and new_qty > old_qty:
            line = OrderLine.with_context(context).browse(values['line_id'])
            line._update_bookings(confirm=False, booking_data=kwargs.get('booking_data', []))
            # add in return values the bookings, to display them on website (or not)
            values['customer_ids'] = Customer.with_context(context).search(
                [('sale_order_line_id', '=', line.id), ('state', '!=', 'cancel')])
        return values
