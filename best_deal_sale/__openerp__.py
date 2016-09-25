# -*- coding: utf-8 -*-
##############################################################################
#
#   Discounts and Coupons Sales
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
