# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Discounts and Coupons
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Discounts and Coupons and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################


from openerp import models, api


class BestDealConfirm(models.TransientModel):
    """Deal Confirmation"""
    _name = "best.deal.confirm"

    @api.multi
    def confirm(self):
        best_deals = self.env['best.deal'].browse(self._context.get('best_deal_ids', []))
        best_deals.do_confirm()
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
