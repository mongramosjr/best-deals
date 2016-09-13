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


class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        # remove product deal from the website content grid and list view (not removed in detail view)
        return ['&'] + super(Website, self).sale_product_domain() + [('best_deal_ok', '=', False)]
