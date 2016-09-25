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
