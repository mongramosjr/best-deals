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


class product_template(models.Model):
    _inherit = 'product.template'
    
    best_deal_ok = fields.Boolean(string='Deal Coupon', help='Determine if a product needs to create automatically an deal booking at the confirmation of a sales order line.')
    best_deal_type_id = fields.Many2one('best.deal.type', string='Type of Deal', help='Select deal types so when we use this product in sales order lines, it will filter deals of this type only.')
    
    @api.onchange('best_deal_ok')
    def onchange_best_deal_product(self):
        if self.best_deal_ok:
            self.type = 'service'
    
class product(models.Model):
    _inherit = 'product.product'
    
    best_deal_coupon_ids = fields.One2many('best.deal.coupon', 'product_id', string='Deal Coupons')
    
    @api.onchange('best_deal_ok')
    def onchange_best_deal_product(self):
        if self.best_deal_ok:
            self.type = 'service'
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
