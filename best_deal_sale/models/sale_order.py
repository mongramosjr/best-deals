# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Discounts and Coupons Sales
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Discounts and Coupons Sales and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

from openerp import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            redirect_to_best_deal_booking, sales_order_id = any(line.best_deal_id for line in order.order_line), order.id
            order.order_line._update_bookings(confirm=True)
        if redirect_to_best_deal_booking:
            best_deal_context = dict(self.env.context, default_sale_order_id=sales_order_id)
            return self.env['ir.actions.act_window'].with_context(best_deal_context).for_xml_id('best_deal_sale', 'action_sale_order_best_deal_booking')
        else:
            return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    best_deal_id = fields.Many2one('best.deal', string = 'Deal',
            help="Choose an deal and it will automatically create a booking for this deal.")
    best_deal_coupon_id = fields.Many2one('best.deal.coupon', string = 'Deal Coupon',
            help="Choose an deal coupon and it will automatically create a booking for this deal coupon.")
    best_deal_type_id = fields.Many2one("best.deal.type", related = 'product_id.best_deal_type_id', string="Deal Type", readonly=True)
    best_deal_ok = fields.Boolean(related = 'product_id.best_deal_ok', string='Coupon', readonly=True)
    

    #deprecated
    @api.v7
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(SaleOrderLine, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        if line.best_deal_id:
            best_deal = self.pool['best.deal'].read(cr, uid, line.best_deal_id.id, ['name'], context=context)
            res['name'] = '%s: %s' % (res.get('name', ''), best_deal['name'])
        return res
        
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
    def _update_bookings(self, confirm=True, booking_data=None):
        """ Create or update bookings linked to a sale order line. A sale
        order line has a product_uom_qty attribute that will be the number of
        bookings linked to this line. This method update existing bookings
        and create new one for missing one. """
        booking_obj = self.env['best.deal.booking']
        bookings = booking_obj.search([('sale_order_line_id', 'in', self.ids)])
        for so_line in [l for l in self if l.best_deal_id]:
            existing_bookings = bookings.filtered(lambda self: self.sale_order_line_id.id == so_line.id)
            if confirm:
                existing_bookings.filtered(lambda self: self.state != 'open').confirm_booking()
            else:
                existing_bookings.filtered(lambda self: self.state == 'cancel').do_draft()

            for count in range(int(so_line.product_uom_qty) - len(existing_bookings)):
                booking = {}
                if booking_data:
                    booking = booking_data.pop()
                # TDE CHECK: auto confirmation
                booking['sale_order_line_id'] = so_line
                self.env['best.deal.booking'].with_context(booking_force_draft=True).create(
                    booking_obj._prepare_customer_values(booking))
        return True


    @api.onchange('best_deal_coupon_id')
    def onchange_best_deal_coupon(self):
        if self.best_deal_coupon_id:
            self.price_unit = self.best_deal_coupon_id.price or False

    #deprecated
    @api.v7
    def onchange_best_deal_coupon_id(self, cr, uid, ids, best_deal_coupon_id=False, context=None):
        price = best_deal_coupon_id and self.pool["best.deal.coupon"].browse(cr, uid, best_deal_coupon_id, context=context).price or False
        return {'value': {'price_unit': price}}



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
