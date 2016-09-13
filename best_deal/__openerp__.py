# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Discounts and Coupons
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Discounts and Coupons and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
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
