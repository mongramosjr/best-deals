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


from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class BestDeal(models.Model):
    _inherit = 'best.deal'
    
    @api.multi
    @api.depends('best_deal_coupon_ids')
    def _prices(self):
        for deal in self:
            if len(deal.best_deal_coupon_ids) > 0:
                deal.price = min([float(coupon.price) for coupon in deal.best_deal_coupon_ids])
            else:
                deal.price = 0.00

    price = fields.Float(compute='_prices', string='Price', store=True)
    
    def _default_coupons(self):
        product = self.env.ref('best_deal_sale.product_product_best_deal', raise_if_not_found=False)
        if not product:
            return self.env['best.deal.coupon']
        return [{
            'name': _('Coupons'),
            'product_id': product.id,
            'price': 0,
        }]
            
    best_deal_coupon_ids = fields.One2many('best.deal.coupon', 'best_deal_id', string='Deal Coupon',
        default=lambda self: self._default_coupons(), copy=True)
            
    @api.multi
    def _is_deal_registrable(self):
        self.ensure_one()
        if not self.best_deal_coupon_ids:
            return True
        return all(self.best_deal_coupon_ids.with_context(active_test=False).mapped(lambda t: t.product_id.active))


class BestDealCoupon(models.Model):
    _name = 'best.deal.coupon'
    _description = 'Best Deal Coupon'
    
    def _default_product_id(self):
        return self.env.ref('best_deal_sale.product_product_best_deal', raise_if_not_found=False)

    name = fields.Char('Name', required=True, translate=True)
    best_deal_id = fields.Many2one('best.deal', "Deal", required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True, domain=[("best_deal_ok", "=", True)],
        default=lambda self: self._default_product_id())
    booking_ids = fields.One2many('best.deal.booking', 'best_deal_coupon_id', 'Bookings')
    price = fields.Float('Price', digits=dp.get_precision('Product Price'))
    deadline = fields.Date("Sales End")
    is_expired = fields.Boolean('Is Expired', compute='_compute_is_expired')
    
    price_reduce = fields.Float(string="Price Reduce", compute="_compute_price_reduce", digits=dp.get_precision('Product Price'))
    price_reduce_taxinc = fields.Float(compute='_get_price_reduce_tax', string='Price Reduce Tax inc')
    # coupons fields
    coupons_availability = fields.Selection(
        [('limited', 'Limited'), ('unlimited', 'Unlimited')],
        'Available Seat', required=True, store=True, compute='_compute_coupons', default="limited")
    coupons_max = fields.Integer('Maximum Available Coupons',
                               help="Define the number of available coupons. If you have too much bookings you will "
                                    "not be able to sell coupons anymore. Set 0 to ignore this rule set as unlimited.")
    coupons_reserved = fields.Integer(string='Reserved Coupons', compute='_compute_coupons', store=True)
    coupons_available = fields.Integer(string='Available Coupons', compute='_compute_coupons', store=True)
    coupons_unconfirmed = fields.Integer(string='Unconfirmed Reserved Coupons', compute='_compute_coupons', store=True)
    coupons_used = fields.Integer(compute='_compute_coupons', store=True)

    @api.multi
    def _compute_is_expired(self):
        for record in self:
            if record.deadline:
                current_date = fields.Date.context_today(record.with_context({'tz': record.best_deal_id.date_tz}))
                record.is_expired = record.deadline < current_date
            else:
                record.is_expired = False
    
    @api.multi
    def _compute_price_reduce(self):
        for record in self:
            product = record.product_id
            discount = product.lst_price and (product.lst_price - product.price) / product.lst_price or 0.0
            record.price_reduce = (1.0 - discount) * record.price

    def _get_price_reduce_tax(self):
        for record in self:
            # sudo necessary here since the field is most probably accessed through the website
            tax_ids = record.sudo().product_id.taxes_id.filtered(lambda r: r.company_id == record.best_deal_id.company_id)
            taxes = tax_ids.compute_all(record.price_reduce, record.best_deal_id.company_id.currency_id, 1.0, product=record.product_id)
            record.price_reduce_taxinc = taxes['total_included']

    @api.multi
    @api.depends('coupons_max', 'booking_ids.state')
    def _compute_coupons(self):
        """ Determine reserved, available, reserved but unconfirmed and used coupons. """
        # initialize fields to 0 + compute coupons availability
        for coupon in self:
            coupon.coupons_availability = 'unlimited' if coupon.coupons_max == 0 else 'limited'
            coupon.coupons_unconfirmed = coupon.coupons_reserved = coupon.coupons_used = coupon.coupons_available = 0
        # aggregate bookings by coupon and by state
        if self.ids:
            state_field = {
                'draft': 'coupons_unconfirmed',
                'open': 'coupons_reserved',
                'done': 'coupons_used',
            }
            query = """ SELECT best_deal_coupon_id, state, count(best_deal_id)
                        FROM best_deal_booking
                        WHERE best_deal_coupon_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY best_deal_coupon_id, state
                    """
            self.env.cr.execute(query, (tuple(self.ids),))
            for best_deal_coupon_id, state, num in self._cr.fetchall():
                coupon = self.browse(best_deal_coupon_id)
                coupon[state_field[state]] += num
        # compute coupons_available
        for coupon in self:
            if coupon.coupons_max > 0:
                coupon.coupons_available = coupon.coupons_max - (coupon.coupons_reserved + coupon.coupons_used)

    @api.multi
    @api.constrains('booking_ids', 'coupons_max')
    def _check_seats_limit(self):
        for record in self:
            if record.coupons_max and record.coupons_available < 0:
                raise ValidationError(_('No more available coupons'))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.price = self.product_id.list_price or 0
        
class BestDealBooking(models.Model):
    _inherit = 'best.deal.booking'

    best_deal_coupon_id = fields.Many2one('best.deal.coupon', 'Deal Coupon')
    # in addition to origin generic fields, add real relational fields to correctly
    # handle attendees linked to sale orders and their lines
    # TDE FIXME: maybe add an onchange on sale_order_id + origin
    sale_order_id = fields.Many2one('sale.order', 'Source Sale Order', ondelete='cascade')
    sale_order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', ondelete='cascade')

    @api.multi
    @api.constrains('best_deal_coupon_id', 'state')
    def _check_coupon_coupons_limit(self):
        for record in self:
            if record.best_deal_coupon_id.coupons_max and record.best_deal_coupon_id.coupons_available < 0:
                raise ValidationError(_('No more available coupons for this booking'))

    @api.multi
    def _check_auto_confirmation(self):
        res = super(BestDealBooking, self)._check_auto_confirmation()
        if res:
            orders = self.env['sale.order'].search([('state', '=', 'draft'), ('id', 'in', self.mapped('sale_order_id').ids)], limit=1)
            if orders:
                res = False
        return res
        
    @api.model
    def create(self, vals):
        res = super(BestDealBooking, self).create(vals)
        if res.origin or res.sale_order_id:
            #res.message_post_with_view('mail.message_origin_link',
                #values={'self': res, 'origin': res.sale_order_id},
                #subtype_id=self.env.ref('mail.mt_note').id)
            message = _("The booking has been created for deal %(best_deal_name)s%(coupon)s from sale order %(order)s") % ({
                'best_deal_name': '<i>%s</i>' % res.best_deal_id.name,
                'coupon': res.best_deal_coupon_id and _(' with coupon %s') % (('<i>%s</i>') % res.best_deal_coupon_id.name) or '',
                'order': res.origin or res.sale_order_id.name})
            res.message_post(body=message)
        return res

    @api.model
    def _prepare_customer_values(self, booking):
        """ Override to add sale related stuff """
        line_id = booking.get('sale_order_line_id')
        if line_id:
            booking.setdefault('partner_id', line_id.order_id.partner_id)
        att_data = super(BestDealBooking, self)._prepare_customer_values(booking)
        if line_id:
            att_data.update({
                'best_deal_id': line_id.best_deal_id.id,
                'best_deal_id': line_id.best_deal_id.id,
                'best_deal_coupon_id': line_id.best_deal_coupon_id.id,
                'origin': line_id.order_id.name,
                'sale_order_id': line_id.order_id.id,
                'sale_order_line_id': line_id.id,
            })
        return att_data


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
