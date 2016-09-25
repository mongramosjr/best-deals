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

from openerp import models, fields, api


class SaleOrderBestDealBooking(models.TransientModel):
    _name = "best.deal.booking.editor"

    sale_order_id = fields.Many2one('sale.order', 'Sale Order', required=True)
    best_deal_booking_ids = fields.One2many('best.deal.booking.editor.line', 'editor_id', string='Bookings to Edit')

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderBestDealBooking, self).default_get(fields)
        if not res.get('sale_order_id'):
            sale_order_id = res.get('sale_order_id', self._context.get('active_id'))
            res['sale_order_id'] = sale_order_id
        sale_order = self.env['sale.order'].browse(res.get('sale_order_id'))
        bookings = self.env['best.deal.booking'].search([
            ('sale_order_id', '=', sale_order.id),
            ('best_deal_coupon_id', 'in', sale_order.mapped('order_line.best_deal_coupon_id').ids),
            ('state', '!=', 'cancel')])

        customer_list = []
        for so_line in [l for l in sale_order.order_line if l.best_deal_coupon_id]:
            existing_bookings = [r for r in bookings if r.best_deal_coupon_id == so_line.best_deal_coupon_id]
            for booking in existing_bookings:
                customer_list.append({
                    'best_deal_id': booking.best_deal_id.id,
                    'best_deal_coupon_id': booking.best_deal_coupon_id.id,
                    'booking_id': booking.id,
                    'name': booking.name,
                    'email': booking.email,
                    'phone': booking.phone,
                    'sale_order_line_id': so_line.id,
                })
            for count in range(int(so_line.product_uom_qty) - len(existing_bookings)):
                customer_list.append([0, 0, {
                    'best_deal_id': so_line.best_deal_id.id,
                    'best_deal_coupon_id': so_line.best_deal_coupon_id.id,
                    'sale_order_line_id': so_line.id,
                }])
        res['best_deal_booking_ids'] = customer_list
        res = self._convert_to_cache(res, validate=False)
        res = self._convert_to_write(res)
        return res

    @api.multi
    def action_make_booking(self):
        Booking = self.env['best.deal.booking']
        for wizard in self:
            for wiz_booking in wizard.best_deal_booking_ids:
                if wiz_booking.booking_id:
                    wiz_booking.booking_id.write(wiz_booking.get_booking_data()[0])
                else:
                    Booking.create(wiz_booking.get_booking_data()[0])
        return {'type': 'ir.actions.act_window_close'}


class BestDealBookingEditorLine(models.TransientModel):
    """Best Deal Booking"""
    _name = "best.deal.booking.editor.line"

    editor_id = fields.Many2one('best.deal.booking.editor')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    best_deal_id = fields.Many2one('best.deal', string='Best Deal', required=True)
    booking_id = fields.Many2one('best.deal.booking', 'Original Booking')
    best_deal_coupon_id = fields.Many2one('best.deal.coupon', string='Best Deal Coupon')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    name = fields.Char(string='Name', select=True)

    @api.one
    def get_booking_data(self):
        return {
            'best_deal_id': self.best_deal_id.id,
            'best_deal_coupon_id': self.best_deal_coupon_id.id,
            'partner_id': self.editor_id.sale_order_id.partner_id.id,
            'name': self.name or self.editor_id.sale_order_id.partner_id.name,
            'phone': self.phone or self.editor_id.sale_order_id.partner_id.phone,
            'email': self.email or self.editor_id.sale_order_id.partner_id.email,
            'origin': self.editor_id.sale_order_id.name,
            'sale_order_id': self.editor_id.sale_order_id.id,
            'sale_order_line_id': self.sale_order_line_id.id,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
