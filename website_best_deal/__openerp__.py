# -*- coding: utf-8 -*-
##############################################################################
#
#   Online Discounts and Coupons
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
    'name': 'Online Discounts and Coupons',
    'version': '2016.0',
    'author': 'Dominador B. Ramos Jr.',
    'license': 'Other OSI approved licence',
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
        'static/src/xml/*.xml'
    ],
    'demo': [
        'data/best_deal_demo.xml',
        'data/best_deal_image_demo.xml'
    ],
    'installable': True,
    'application': True,
}
