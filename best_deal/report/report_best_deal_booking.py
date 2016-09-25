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

from openerp import models, fields
from openerp import tools


class ReportBestDealBooking(models.Model):
    """Coupons Analysis"""
    _name = "report.best.deal.booking"
    _order = 'best_deal_date desc'
    _auto = False

    create_date = fields.Datetime('Creation Date', readonly=True)
    best_deal_date = fields.Datetime('Deal Date', readonly=True)
    best_deal_id = fields.Many2one('best.deal', 'Deal', required=True)
    draft_state = fields.Integer(' # No of Draft Bookings')
    cancel_state = fields.Integer(' # No of Cancelled Bookings')
    confirm_state = fields.Integer(' # No of Confirmed Bookings')
    coupons_max = fields.Integer('Max Coupons')
    nbdeals = fields.Integer('Number of Deals')
    nbbooking = fields.Integer('Number of Bookings')
    best_deal_type_id = fields.Many2one('best.deal.type', 'Best Deal Type')
    booking_state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Consumed'), ('cancel', 'Cancelled')], 'Booking State', readonly=True, required=True)
    best_deal_state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Deal State', readonly=True, required=True)
    user_id = fields.Many2one('res.users', 'Deal Responsible', readonly=True)
    name_booking = fields.Char('Customer / Contact Name', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    def init(self, cr):
        """Initialize the sql view for the deal booking """
        tools.drop_view_if_exists(cr, 'report_best_deal_booking')

        # TOFIX this request won't select deals that have no booking
        cr.execute(""" CREATE VIEW report_best_deal_booking AS (
            SELECT
                e.id::varchar || '/' || coalesce(r.id::varchar,'') AS id,
                e.id AS best_deal_id,
                e.user_id AS user_id,
                r.name AS name_booking,
                r.create_date AS create_date,
                e.company_id AS company_id,
                e.date_begin AS best_deal_date,
                count(r.id) AS nbdeal,
                count(r.best_deal_id) AS nbbooking,
                CASE WHEN r.state IN ('draft') THEN count(r.best_deal_id) ELSE 0 END AS draft_state,
                CASE WHEN r.state IN ('open','done') THEN count(r.best_deal_id) ELSE 0 END AS confirm_state,
                CASE WHEN r.state IN ('cancel') THEN count(r.best_deal_id) ELSE 0 END AS cancel_state,
                e.best_deal_type_id AS best_deal_type_id,
                e.coupons_max AS coupons_max,
                e.state AS best_deal_state,
                r.state AS booking_state
            FROM
                best_deal e
                LEFT JOIN best_deal_booking r ON (e.id=r.best_deal_id)

            GROUP BY
                best_deal_id,
                r.id,
                booking_state,
                best_deal_type_id,
                e.id,
                e.date_begin,
                e.user_id,
                best_deal_state,
                e.company_id,
                e.coupons_max,
                name_booking
        )
        """)
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

