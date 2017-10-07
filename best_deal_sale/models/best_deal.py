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


from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.osv import fields as old_fields


class BestDeal(models.Model):
    _inherit = 'best.deal'
    
    @api.multi
    @api.depends('best_deal_coupon_ids')
    def _prices(self):
        for deal in self:
            deal.price = min([float(coupon.price) for coupon in deal.best_deal_coupon_ids])

    price = fields.Float(compute='_prices', string='Price', store=True)
    
    best_deal_coupon_ids = fields.One2many(
        'best.deal.coupon', 'best_deal_id', string='Deal Coupon',
        default=lambda rec: rec._default_coupons(), copy=True)

    @api.model
    def _default_coupons(self):
        try:
            product = self.env.ref('best_deal_sale.product_product_best_deal')
            return [{
                'name': _('Coupons'),
                'product_id': product.id,
                'price': 0,
            }]
        except ValueError:
            return self.env['best.deal.coupon']


class BestDealCoupon(models.Model):
    _name = 'best.deal.coupon'
    _description = 'Best Deal Coupon'

    name = fields.Char('Name', required=True, translate=True)
    best_deal_id = fields.Many2one('best.deal', "Deal", required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True, domain=[("best_deal_type_id", "!=", False)],
        default=lambda self: self._default_product_id())
    booking_ids = fields.One2many('best.deal.booking', 'best_deal_coupon_id', 'Bookings')
    price = fields.Float('Price', digits=dp.get_precision('Product Price'))
    deadline = fields.Date("Sales End")
    is_expired = fields.Boolean('Is Expired', compute='_is_expired')

    @api.model
    def _default_product_id(self):
        try:
            product = self.env['ir.model.data'].get_object('best_deal_sale', 'product_product_best_deal')
            return product.id
        except ValueError:
            return False

    @api.one
    @api.depends('deadline')
    def _is_expired(self):
        if self.deadline:
            current_date = fields.Date.context_today(self.with_context({'tz': self.best_deal_id.date_tz}))
            self.is_expired = self.deadline < current_date
        else:
            self.is_expired = False

    # FIXME non-stored fields wont ends up in _columns (and thus _all_columns), which forbid them
    #       to be used in qweb views. Waiting a fix, we create an old function field directly.
    """
    price_reduce = fields.Float("Price Reduce", compute="_get_price_reduce", store=False,
                                digits=dp.get_precision('Product Price'))
    @api.one
    @api.depends('price', 'product_id.lst_price', 'product_id.price')
    def _get_price_reduce(self):
        product = self.product_id
        discount = product.lst_price and (product.lst_price - product.price) / product.lst_price or 0.0
        self.price_reduce = (1.0 - discount) * self.price
    """
    @api.v7
    def _get_price_reduce(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        for coupon in self.browse(cr, uid, ids, context=context):
            product = coupon.product_id
            discount = product.lst_price and (product.lst_price - product.price) / product.lst_price or 0.0
            res[coupon.id] = (1.0 - discount) * coupon.price
        return res

    _columns = {
        'price_reduce': old_fields.function(_get_price_reduce, type='float', string='Price Reduce',
                                            digits_compute=dp.get_precision('Product Price')),
    }

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
            self._cr.execute(query, (tuple(self.ids),))
            for best_deal_coupon_id, state, num in self._cr.fetchall():
                coupon = self.browse(best_deal_coupon_id)
                coupon[state_field[state]] += num
        # compute coupons_available
        for coupon in self:
            if coupon.coupons_max > 0:
                coupon.coupons_available = coupon.coupons_max - (coupon.coupons_reserved + coupon.coupons_used)

    @api.one
    @api.constrains('booking_ids', 'coupons_max')
    def _check_coupons_limit(self):
        if self.coupons_max and self.coupons_available < 0:
            raise UserError(_('No more available coupons'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        price = self.product_id.list_price if self.product_id else 0
        return {'value': {'price': price}}


class BestDealBooking(models.Model):
    _inherit = 'best.deal.booking'

    best_deal_coupon_id = fields.Many2one('best.deal.coupon', 'Deal Coupon')
    # in addition to origin generic fields, add real relational fields to correctly
    # handle attendees linked to sale orders and their lines
    # TDE FIXME: maybe add an onchange on sale_order_id + origin
    sale_order_id = fields.Many2one('sale.order', 'Source Sale Order', ondelete='cascade')
    sale_order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', ondelete='cascade')

    @api.one
    @api.constrains('best_deal_coupon_id', 'state')
    def _check_coupon_coupons_limit(self):
        if self.best_deal_coupon_id.coupons_max and self.best_deal_coupon_id.coupons_available < 0:
            raise UserError(_('No more available coupons for this coupon'))

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
