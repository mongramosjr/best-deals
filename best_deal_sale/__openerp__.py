# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Discounts and Coupons Sales
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Discounts and Coupons Sales and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

{
    'name': 'Discounts and Coupons Sales',
    'version': '2016.0',
    'website': 'https://www.3d2n.deals',
    'category': 'Marketing',
    'summary': 'Sales on Discounts and Coupons',
    'description': """
Creating coupon booking with sale orders.
=======================================

This module allows you to automate and connect your coupon booking with
your main sale flow and therefore, to enable the invoicing feature of procurement.

It defines a new kind of service products that offers you the possibility to
choose a coupon category associated with it. When you encode a sale order for
that product, you will be able to choose an existing coupon of that category and
when you confirm your sale order it will automatically create a booking for
this coupon.
""",
    'depends': ['best_deal', 'sale'],
    'data': [
        'data/best_deal_sale_data.xml',
        'security/ir.model.access.csv',
        'views/best_deal_view.xml',
        'views/product_view.xml',
        'views/sale_order_view.xml',
        'report/best_deal_templates.xml',
        'wizard/best_deal_edit_booking.xml',
    ],
    'demo': [
        'data/best_deal_demo.xml'
    ],
    #'test': ['test/confirm.yml'],
    'installable': True,
    'auto_install': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
