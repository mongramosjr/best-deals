# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Online Discounts and Coupons
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Online Discounts and Coupons and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

{
    'name': 'Online Discounts and Coupons',
    'version': '2016.0',
    'website': 'https://www.3d2n.deals',
    'category': 'Marketing',
    'summary': 'Schedule and Promote Coupons',
    'description': """
Online Discounts and Coupons
        """,
    'depends': ['website', 'website_partner', 'website_mail', 'best_deal'],
    'data': [
        'data/best_deal_data.xml',
        'views/website_best_deal_template.xml',
        'views/website_best_deal_backend.xml',
        'security/ir.model.access.csv',
        'security/website_best_deal.xml',
    ],
    'qweb': [
        #'static/src/xml/*.xml'
    ],
    'demo': [
        #'data/best_deal_demo.xml'
    ],
    'installable': True,
    'application': True,
}
