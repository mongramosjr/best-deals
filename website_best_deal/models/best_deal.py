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


import re

from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from openerp.addons.website.models.website import slug


class BestDealStyle(models.Model):
    _name = "best.deal.style"
    name = fields.Char('Style Name', required=True)
    html_class = fields.Char('HTML Classes')
    

class BestDeal(models.Model):
    _name = 'best.deal'
    _inherit = ['best.deal', 'website.seo.metadata', 'website.published.mixin']

    website_style_ids = fields.Many2many('best.deal.style', string='Styles')

    twitter_hashtag = fields.Char('Twitter Hashtag', default=lambda self: self._default_hashtag())
    website_published = fields.Boolean(track_visibility='onchange')
    # TDE TODO FIXME: when website_mail/mail_thread.py inheritance work -> this field won't be necessary
    website_message_ids = fields.One2many(
        'mail.message', 'res_id',
        domain=lambda self: [
            '&', ('model', '=', self._name), ('message_type', '=', 'comment')
        ],
        string='Website Messages',
        help="Website communication history",
    )

    @api.multi
    @api.depends('name')
    def _website_url(self, name, arg):
        res = super(BestDeal, self)._website_url(name, arg)
        res.update({(e.id, '/bestdeal/%s' % slug(e)) for e in self})
        return res

    def _default_hashtag(self):
        return re.sub("[- \\.\\(\\)\\@\\#\\&]+", "", self.env.user.company_id.name).lower()

    show_menu = fields.Boolean('Dedicated Menu', compute='_get_show_menu', inverse='_set_show_menu',
                               help="Creates menus Introduction, Location and Book on the page "
                                    " of the deal on the website.", store=True)
    menu_id = fields.Many2one('website.menu', 'Deal Menu', copy=False)

    @api.one
    def _get_new_menu_pages(self):
        todo = [
            (_('Introduction'), 'website_best_deal.template_intro'),
            (_('Location'), 'website_best_deal.template_location')
        ]
        result = []
        for name, path in todo:
            complete_name = name + ' ' + self.name
            newpath = self.env['website'].new_page(complete_name, path, ispage=False)
            url = "/bestdeal/" + slug(self) + "/page/" + newpath
            result.append((name, url))
        result.append((_('Booking'), '/bestdeal/%s/booking' % slug(self)))
        return result

    @api.one
    def _set_show_menu(self):
        if self.menu_id and not self.show_menu:
            self.menu_id.unlink()
        elif self.show_menu and not self.menu_id:
            root_menu = self.env['website.menu'].create({'name': self.name})
            to_create_menus = self._get_new_menu_pages()[0]  # TDE CHECK api.one -> returns a list with one item ?
            seq = 0
            for name, url in to_create_menus:
                self.env['website.menu'].create({
                    'name': name,
                    'url': url,
                    'parent_id': root_menu.id,
                    'sequence': seq,
                })
                seq += 1
            self.menu_id = root_menu

    @api.one
    def _get_show_menu(self):
        self.show_menu = bool(self.menu_id)

    def google_map_img(self, cr, uid, ids, zoom=8, width=298, height=298, context=None):
        best_deal = self.browse(cr, uid, ids[0], context=context)
        if best_deal.address_id:
            return self.browse(cr, SUPERUSER_ID, ids[0], context=context).address_id.google_map_img()
        return None

    def google_map_link(self, cr, uid, ids, zoom=8, context=None):
        best_deal = self.browse(cr, uid, ids[0], context=context)
        if best_deal.address_id:
            return self.browse(cr, SUPERUSER_ID, ids[0], context=context).address_id.google_map_link()
        return None

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'website_published' in init_values and self.website_published:
            return 'website_best_deal.mt_best_deal_published'
        elif 'website_published' in init_values and not self.website_published:
            return 'website_best_deal.mt_best_deal_unpublished'
        return super(BestDeal, self)._track_subtype(init_values)

    @api.multi
    def action_open_badge_editor(self):
        """ open the best_deal badge editor : redirect to the report page of best_deal badge report """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/report/html/%s/%s?enable_editor' % ('best_deal.best_deal_report_template_badge', self.id),
        }
