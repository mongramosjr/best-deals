# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Sell Discount Coupons
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Sell Discount Coupons and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

{
    'name': "Sell Discount Coupons",
    'version': '2016.0',
    'website': 'https://www.3d2n.deals',
    'category': 'Marketing',
    'summary': "Sell Your Coupons",
    'description': """
Online Discount Coupons
======================

        """,
    'depends': ['website_best_deal', 'best_deal_sale', 'website_sale'],
    'data': [
        'views/website_best_deal_sale_template.xml',
        'security/ir.model.access.csv',
        'security/website_best_deal_sale.xml',
    ],
    'qweb': [
        #'static/src/xml/*.xml'
    ],
    'installable': True,
    'auto_install': True
}
