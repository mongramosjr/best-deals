# -*- coding: utf-8 -*-
##############################################################################
#
#   Discounts and Coupons
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


from openerp import api, fields, models, tools

class BestDealConfigSettings(models.TransientModel):
    _name='best.deal.config.settings'
    _inherit='res.config.settings'
    
    module_best_deal_sale = fields.Selection([
            (0, "All deals are free"),
            (1, 'Allow selling coupons')
            ], "Coupons",
            help='Install the best_deal_sale module')
            
    auto_confirmation = fields.Selection([
            (1, 'No validation step on booking'),
            (0, "Manually confirm every booking")
            ], "Auto Confirmation",
            help='Unselect this option to manually manage draft deal and draft booking')
            
    group_email_scheduling = fields.Selection([
            (0, "No automated emails"),
            (1, 'Schedule emails to customers and subscribers')
            ], "Email Scheduling",
            help='You will be able to configure emails, and to schedule them to be automatically sent to the customers on booking',
            implied_group='best_deal.group_email_scheduling')

    def set_default_auto_confirmation(self, cr, uid, ids, context=None):
        config_value = self.browse(cr, uid, ids, context=context).auto_confirmation
        self.pool.get('ir.values').set_default(cr, uid, 'best.deal.config.settings', 'auto_confirmation', config_value)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
