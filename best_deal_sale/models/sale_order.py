# -*- coding: utf-8 -*-
##############################################################################
#
#   Discounts and Coupons Sales
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

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        res = super(SaleOrder, self).action_confirm()
        
        self.order_line._update_bookings(confirm=self.amount_total == 0, cancel_to_draft=False)
        if any(self.order_line.filtered(lambda line: line.best_deal_id)):
            return self.env['ir.actions.act_window'].with_context(default_sale_order_id=self.id).for_xml_id('best_deal_sale', 'action_sale_order_best_deal_booking')
        return res
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    best_deal_id = fields.Many2one('best.deal', string = 'Deal',
            help="Choose an deal and it will automatically create a booking for this deal.")
    best_deal_coupon_id = fields.Many2one('best.deal.coupon', string = 'Deal Coupon',
            help="Choose an deal coupon and it will automatically create a booking for this deal coupon.")
    best_deal_type_id = fields.Many2one("best.deal.type", related = 'product_id.best_deal_type_id', string="Deal Type", readonly=True)
    best_deal_ok = fields.Boolean(related = 'product_id.best_deal_ok', string='Coupon', readonly=True)
    

    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.best_deal_id:
            res['name'] = '%s: %s' % (res.get('name', ''), self.best_deal_id.name)
        return res

    @api.onchange('product_id')
    def onchange_product_id_best_deal(self):
        if self.product_id.best_deal_ok:
            values = dict(best_deal_type_id=self.product_id.best_deal_type_id.id,
                          best_deal_ok=self.product_id.best_deal_ok)
        else:
            values = dict(best_deal_type_id=False, best_deal_ok=False)
        self.update(values)

    @api.multi
    def _update_bookings(self, confirm=True, cancel_to_draft=False, booking_data=None):
        """ Create or update bookings linked to a sale order line. A sale
        order line has a product_uom_qty attribute that will be the number of
        bookings linked to this line. This method update existing bookings
        and create new one for missing one. """
        Booking = self.env['best.deal.booking']
        bookings = Booking.search([('sale_order_line_id', 'in', self.ids)])
        for so_line in self.filtered('best_deal_id'):
            existing_bookings = bookings.filtered(lambda self: self.sale_order_line_id.id == so_line.id)
            if confirm:
                existing_bookings.filtered(lambda self: self.state != 'open').confirm_booking()
            if cancel_to_draft:
                existing_bookings.filtered(lambda self: self.state == 'cancel').do_draft()
            
            for count in range(int(so_line.product_uom_qty) - len(existing_bookings)):
                booking = {}
                if booking_data:
                    booking = booking_data.pop()
                # TDE CHECK: auto confirmation
                booking['sale_order_line_id'] = so_line
                Booking.with_context(booking_force_draft=True).create(
                    Booking._prepare_customer_values(booking))
        return True


    @api.onchange('best_deal_coupon_id')
    def onchange_best_deal_coupon(self):
        if self.best_deal_coupon_id:
            self.price_unit = (self.best_deal_id.company_id or self.env.user.company_id).currency_id.compute(self.best_deal_coupon_id.price, self.order_id.currency_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
