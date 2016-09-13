# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Sell Discount Coupons
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Sell Discount Coupons and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

from openerp import models, fields, api, _

# defined for access rules
class Product(models.Model):
    _inherit = 'product.product'
    best_deal_coupon_ids = fields.One2many('best.deal.coupon', 'product_id', 'Deal Coupon')
    
