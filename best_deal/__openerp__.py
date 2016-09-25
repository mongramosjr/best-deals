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

{
    'name': 'Discounts and Coupons',
    'version': '2016.0',
    'website': 'https://www.3d2n.deals',
    'category': 'Marketing',
    'summary': 'Discounts and Coupons',
    'description': """
Management of discounts and promotional coupons.
======================================

The best deal module allows you to efficiently manages discounts and promotional coupons.

Key Features
------------
* Manage your discounts and promotional coupons
* Use emails to automatically confirm and send confirmation of purchased deals and promotional coupons
""",
    'depends': ['base_setup', 'mail', 'marketing', 'web_tip'],
    'data': [

        'security/best_deal_security.xml',
        'security/ir.model.access.csv',
        
        'wizard/best_deal_confirm_view.xml',
        'views/best_deal_view.xml',
        'report/report_best_deal_booking_view.xml',
        'report/best_deal_templates.xml',
        'report/best_deal_reports.xml',
        'data/best_deal_data.xml',
        'data/best_deal_data_tip.xml',
        'views/best_deal_config_settings_view.xml',
        'views/best_deal_templates.xml',
        'data/email_template_data.xml',

    ],
    'demo': [
        'data/best_deal_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
