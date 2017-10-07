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

from odoo import models, fields, api, _
from odoo.addons.website.models.website import slug


class BestDealStyle(models.Model):
    _name = "best.deal.style"
    name = fields.Char('Style Name', required=True)
    html_class = fields.Char('HTML Classes')
    

class BestDeal(models.Model):
    _name = 'best.deal'
    _inherit = ['best.deal', 'website.seo.metadata', 'website.published.mixin']
    
    def _default_hashtag(self):
        return re.sub("[- \\.\\(\\)\\@\\#\\&]+", "", self.env.user.company_id.name).lower()

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

    show_menu = fields.Boolean('Dedicated Menu', compute='_get_show_menu', inverse='_set_show_menu',
                               help="Creates menus Introduction, Location and Book on the page "
                                    " of the deal on the website.", store=True)
    menu_id = fields.Many2one('website.menu', 'Deal Menu', copy=False)
    
    @api.multi
    @api.depends('name')
    def _compute_website_url(self):
        super(BestDeal, self)._compute_website_url()
        for best_deal in self:
            if best_deal.id:  # avoid to perform a slug on a not yet saved record in case of an onchange.
                best_deal.website_url = '/bestdeal/%s' % slug(best_deal)

    @api.multi
    def _get_new_menu_pages(self):
        """ Retuns a list of tuple ('Page name', 'relative page url') for the deal """
        self.ensure_one()
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
        result.append((_('Register'), '/bestdeal/%s/booking' % slug(self)))
        return result
        
    @api.multi
    def _set_show_menu(self):
        for best_deal in self:
            if best_deal.menu_id and not best_deal.show_menu:
                best_deal.menu_id.unlink()
            elif best_deal.show_menu and not best_deal.menu_id:
                root_menu = self.env['website.menu'].create({'name': best_deal.name})
                to_create_menus = best_deal._get_new_menu_pages()
                seq = 0
                for name, url in to_create_menus:
                    self.env['website.menu'].create({
                        'name': name,
                        'url': url,
                        'parent_id': root_menu.id,
                        'sequence': seq,
                    })
                    seq += 1
                best_deal.menu_id = root_menu

    @api.multi
    def _get_show_menu(self):
        for best_deal in self:
            best_deal.show_menu = bool(best_deal.menu_id)

    @api.multi
    def google_map_img(self, zoom=8, width=298, height=298):
        self.ensure_one()
        if self.address_id:
            return self.sudo().address_id.google_map_img(zoom=zoom, width=width, height=height)
        return None
        
    @api.multi
    def google_map_link(self, zoom=8):
        self.ensure_one()
        if self.address_id:
            return self.sudo().address_id.google_map_link(zoom=zoom)
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
