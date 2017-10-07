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

import pytz

from odoo import _, api, fields, models, tools
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from dateutil.relativedelta import relativedelta

from . import best_deal_image

class BestDealType(models.Model):
    """ Best Deal Type """
    _name = 'best.deal.type'
    _description = 'Best Deal Type'

    name = fields.Char('Best Deal Type', required=True, translate=True)
    default_reply_to = fields.Char('Reply To')
    default_booking_min = fields.Integer(
        'Default Minimum Bookings', default=0,
        help="It will select this default minimum value when you choose this deal")
    default_booking_max = fields.Integer(
        'Default Maximum Bookings', default=0,
        help="It will select this default maximum value when you choose this deal")
        
class BestDealCategory(models.Model):
    """ Best Deal Type of Service"""
    _name = 'best.deal.category'
    _description = 'Best Deal Category'

    name = fields.Char('Best Deal Category', required=True, translate=True)



class BestDeal(models.Model):
    """Best Deal"""
    _name = 'best.deal'
    _description = 'Best Deal'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date_begin'

    name = fields.Char(
        string='Best Deal Name', translate=True, required=True,
        readonly=False, states={'done': [('readonly', True)]})
    active = fields.Boolean(default=True, track_visibility="onchange")
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        default=lambda self: self.env.user,
        readonly=False, states={'done': [('readonly', True)]})
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('best.deal'),
        required=False, readonly=False, states={'done': [('readonly', True)]})
    partner_id = fields.Many2one(
        'res.partner', string='Local Partner',
        default=lambda self: self.env.user.company_id.partner_id)
    best_deal_type_id = fields.Many2one(
        'best.deal.type', string='Category',
        readonly=False, states={'done': [('readonly', True)]})
    color = fields.Integer('Kanban Color Index')
    best_deal_mail_ids = fields.One2many('best.deal.mail', 'best_deal_id', 
        string='Mail Schedule', default=lambda self: self._default_best_deal_mail_ids())

    @api.model
    def _default_best_deal_mail_ids(self):
        return [(0, 0, {
            'interval_unit': 'now',
            'interval_type': 'after_booking',
            'template_id': self.env.ref('best_deal.best_deal_booking')
        })]

    # Coupons and computation
    coupons_max = fields.Integer(
        string='Maximum Coupons',
        readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="For each deal you can define a maximum coupons to be booked, above this numbers the bookings are not accepted.")
    coupons_availability = fields.Selection(
        [('limited', 'Limited'), ('unlimited', 'Unlimited')],
        'Coupons Availability', required=True, default='unlimited')
    coupons_min = fields.Integer(
        string='Minimum Coupons',
        help="For each deal you can define a minimum booked coupons, if it does not reach the mentioned bookings the deal can not be offered nor booked (keep 0 to ignore this rule)")
    coupons_reserved = fields.Integer(
        string='Reserved Coupons',
        store=True, readonly=True, compute='_compute_coupons')
    coupons_available = fields.Integer(
        string='Maximum Coupons',
        store=True, readonly=True, compute='_compute_coupons')
    coupons_unconfirmed = fields.Integer(
        string='Unconfirmed Reserved Coupons',
        store=True, readonly=True, compute='_compute_coupons')
    coupons_used = fields.Integer(
        string='Number of Coupons Used',
        store=True, readonly=True, compute='_compute_coupons')
    coupons_expected = fields.Integer(
        string='Number of Expected Bookings',
        readonly=True, compute='_compute_coupons')

    @api.multi
    @api.depends('coupons_max', 'booking_ids.state')
    def _compute_coupons(self):
        """ Determine reserved, available, reserved but unconfirmed and used coupons. """
        # initialize fields to 0
        for best_deal in self:
            best_deal.coupons_unconfirmed = best_deal.coupons_reserved = best_deal.coupons_used = best_deal.coupons_available = 0
        # aggregate coupons by deal and by state
        if self.ids:
            state_field = {
                'draft': 'coupons_unconfirmed',
                'open': 'coupons_reserved',
                'done': 'coupons_used',
            }
            query = """ SELECT best_deal_id, state, count(best_deal_id)
                        FROM best_deal_booking
                        WHERE best_deal_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY best_deal_id, state
                    """
            self._cr.execute(query, (tuple(self.ids),))
            for best_deal_id, state, num in self._cr.fetchall():
                best_deal = self.browse(best_deal_id)
                best_deal[state_field[state]] += num
        # compute coupons_available
        for best_deal in self:
            if best_deal.coupons_max > 0:
                best_deal.coupons_available = best_deal.coupons_max - (best_deal.coupons_reserved + best_deal.coupons_used)
            best_deal.coupons_expected = best_deal.coupons_unconfirmed + best_deal.coupons_reserved + best_deal.coupons_used

    # Booking fields
    booking_ids = fields.One2many(
        'best.deal.booking', 'best_deal_id', string='Coupons',
        readonly=False, states={'done': [('readonly', True)]})
    # Date fields
    date_tz = fields.Selection('_tz_get', string='Timezone', default=lambda self: self.env.user.tz)
    date_begin = fields.Datetime(
        string='Start Date', required=True,
        track_visibility='onchange', states={'done': [('readonly', True)]})
    date_end = fields.Datetime(
        string='End Date', required=True,
        track_visibility='onchange', states={'done': [('readonly', True)]})
    date_begin_located = fields.Datetime(string='Start Date Located', compute='_compute_date_begin_tz')
    date_end_located = fields.Datetime(string='End Date Located', compute='_compute_date_end_tz')

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    @api.one
    @api.depends('date_tz', 'date_begin')
    def _compute_date_begin_tz(self):
        if self.date_begin:
            self_in_tz = self.with_context(tz=(self.date_tz or 'UTC'))
            date_begin = fields.Datetime.from_string(self.date_begin)
            self.date_begin_located = fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, date_begin))
        else:
            self.date_begin_located = False

    @api.one
    @api.depends('date_tz', 'date_end')
    def _compute_date_end_tz(self):
        if self.date_end:
            self_in_tz = self.with_context(tz=(self.date_tz or 'UTC'))
            date_end = fields.Datetime.from_string(self.date_end)
            self.date_end_located = fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, date_end))
        else:
            self.date_end_located = False

    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'), ('done', 'Done')],
        string='Status', default='draft', readonly=True, required=True, copy=False,
        help="If best deal is created, the status is 'Draft'. If best deal is confirmed for the particular dates the status is set to 'Confirmed'. If the best deal is over, the status is set to 'Done'. If best deal is cancelled the status is set to 'Cancelled'.")
    auto_confirm = fields.Boolean(string='Confirmation not required', compute='_compute_auto_confirm')

    @api.one
    def _compute_auto_confirm(self):
        self.auto_confirm = self.env['ir.values'].get_default('best_deal.config.settings', 'auto_confirmation')

    reply_to = fields.Char(
        'Reply-To Email', readonly=False, states={'done': [('readonly', True)]},
        help="The email address of the organizer is likely to be put here, with the effect to be in the 'Reply-To' of the mails sent automatically at best deal or bookings confirmation. You can also put the email address of your mail gateway if you use one.")
    address_id = fields.Many2one(
        'res.partner', string='Location', default=lambda self: self.env.user.company_id.partner_id,
        readonly=False, states={'done': [('readonly', True)]})
    country_id = fields.Many2one('res.country', 'Country',  related='address_id.country_id', store=True)
    state_id = fields.Many2one('res.country.state', 'State',  related='address_id.state_id', store=True)
    
    country_name = fields.Char('Country Name',  related='address_id.country_id.name', store=True)
    state_name = fields.Char('State Name',  related='address_id.state_id.name', store=True)
    
    
    #image
    image = fields.Binary("Image", attachment=True,
        help="This field holds the image used as image for the deal, limited to 1280x960px.")
        
    image_icon = fields.Binary("Icon image", attachment=True,
        help="Medium-sized image of the deal. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved, "\
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
 
    image_wide = fields.Binary("Icon image", attachment=True,
        help="Medium-sized image of the deal. It is automatically "\
             "resized as a 1280 × 720 image, with aspect ratio preserved, "\
             "only when the image exceeds one of those sizes. Use this field in slides, banner or full background")
 
    @api.model
    def _get_default_image(self, colorize=False):
        if getattr(threading.currentThread(), 'testing', False) or self.env.context.get('install_mode'):
            return False

        img_path = openerp.modules.get_module_resource(
            'best_deal', 'static/src/img', 'best_deal.png')
        
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize deal
        if colorize:
            image = tools.image_colorize(image)

        return best_deal_image.deal_image_resize_image_banner(image.encode('base64'))
    
    description = fields.Html(
        string='Description', translate=True,
        readonly=False, states={'done': [('readonly', True)]})
        
    # badge fields
    badge_front = fields.Html(string='Badge Front')
    badge_back = fields.Html(string='Badge Back')
    badge_innerleft = fields.Html(string='Badge Innner Left')
    badge_innerright = fields.Html(string='Badge Inner Right')
    best_deal_logo = fields.Html(string='Best Deal Logo')

    @api.multi
    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for best_deal in self:
            date_begin = fields.Datetime.from_string(best_deal.date_begin)
            date_end = fields.Datetime.from_string(best_deal.date_end)
            dates = [fields.Date.to_string(fields.Datetime.context_timestamp(best_deal, dt)) for dt in [date_begin, date_end] if dt]
            dates = sorted(set(dates))
            result.append((best_deal.id, '%s (%s)' % (best_deal.name, ' - '.join(dates))))
        return result

    @api.one
    @api.constrains('coupons_max', 'coupons_available')
    def _check_coupons_limit(self):
        if self.coupons_availability == 'limited' and self.coupons_max and self.coupons_available < 0:
            raise UserError(_('No more available coupons.'))

    @api.one
    @api.constrains('date_begin', 'date_end')
    def _check_closing_date(self):
        if self.date_end < self.date_begin:
            raise UserError(_('Closing Date cannot be set before Beginning Date.'))

    @api.model
    def create(self, vals):
        
        #if not vals.get('image'):
            ## force no colorize for images with no transparency
            #vals['image'] = self._get_default_image(False)
        
        best_deal_image.deal_image_resize_images(vals)
        
        res = super(BestDeal, self).create(vals)
        
        if res.partner_id:
            res.message_subscribe([res.partner_id.id])
        if res.auto_confirm:
            res.button_confirm()
        return res

    @api.multi
    def write(self, vals):
        
        best_deal_image.deal_image_resize_images(vals)
        
        res = super(BestDeal, self).write(vals)
        
        if vals.get('partner_id'):
            self.message_subscribe([vals['partner_id']])
        return res

    @api.one
    def button_draft(self):
        self.state = 'draft'

    @api.one
    def button_cancel(self):
        for best_deal_booking in self.booking_ids:
            if best_deal_booking.state == 'done':
                raise UserError(_("You have already set a booking for this deal as 'Used'. Please reset it to draft if you want to cancel this deal."))
        self.booking_ids.write({'state': 'cancel'})
        self.state = 'cancel'

    @api.one
    def button_done(self):
        self.state = 'done'

    @api.one
    def button_confirm(self):
        self.state = 'confirm'

    @api.onchange('best_deal_type_id')
    def _onchange_type(self):
        if self.best_deal_type_id:
            self.coupons_min = self.best_deal_type_id.default_booking_min
            self.coupons_max = self.best_deal_type_id.default_booking_max
            self.reply_to = self.best_deal_type_id.default_reply_to

    @api.multi
    def action_best_deal_booking_report(self):
        res = self.env['ir.actions.act_window'].for_xml_id('best_deal', 'action_report_best_deal_booking')
        res['context'] = {
            "search_default_best_deal_id": self.id,
            "group_by": ['create_date:day'],
        }
        return res

    @api.one
    def mail_bookings(self, template_id, force_send=False, filter_func=lambda self: True):
        for booking in self.booking_ids.filtered(filter_func):
            self.env['mail.template'].browse(template_id).send_mail(booking.id, force_send=force_send)

    @api.multi
    def _is_deal_registrable(self):
        return True
        
class BestDealBooking(models.Model):
    _name = 'best.deal.booking'
    _description = 'Bookings'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name, create_date desc'

    origin = fields.Char(
        string='Source Document', readonly=True,
        help="Reference of the document that created the booking, for example a sale order")
    best_deal_id = fields.Many2one(
        'best.deal', string='Best Deal', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(
        'res.partner', string='Contact',
        states={'done': [('readonly', True)]})
    date_open = fields.Datetime(string='Booking Date', readonly=True, default=lambda self: fields.datetime.now())  # weird crash is directly now
    date_closed = fields.Datetime(string='Consumed Date', readonly=True)
    best_deal_begin_date = fields.Datetime(string="Best Deal Start Date", related='best_deal_id.date_begin', readonly=True)
    best_deal_end_date = fields.Datetime(string="Best Deal End Date", related='best_deal_id.date_end', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', related='best_deal_id.company_id',
        store=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('open', 'Confirmed'), ('done', 'Consumed')],
        string='Status', default='draft', readonly=True, copy=False, track_visibility='onchange')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    name = fields.Char(string='Client Name', index=True)

    @api.one
    @api.constrains('best_deal_id', 'state')
    def _check_coupons_limit(self):
        if self.best_deal_id.coupons_availability == 'limited' and self.best_deal_id.coupons_max and self.best_deal_id.coupons_available < (1 if self.state == 'draft' else 0):
            raise UserError(_('No more coupons available for this deal.'))

    @api.multi
    def _check_auto_confirmation(self):
        if self._context.get('booking_force_draft'):
            return False
        if any(booking.best_deal_id.state != 'confirm' or
               not booking.best_deal_id.auto_confirm or
               (not booking.best_deal_id.coupons_available and booking.best_deal_id.coupons_availability == 'limited') for booking in self):
            return False
        return True

    @api.model
    def create(self, vals):
        booking = super(BestDealBooking, self).create(vals)
        if booking._check_auto_confirmation():
            booking.sudo().confirm_booking()
        return booking

    @api.model
    def _prepare_customer_values(self, booking):
        """ Method preparing the values to create new customers based on a
        sale order line. It takes some booking data (dict-based) that are
        optional values coming from an external input like a web page. This method
        is meant to be inherited in various addons that sell deals. """
        partner_id = booking.pop('partner_id', self.env.user.partner_id)
        best_deal_id = booking.pop('best_deal_id', False)
        data = {
            'name': booking.get('name', partner_id.name),
            'phone': booking.get('phone', partner_id.phone),
            'email': booking.get('email', partner_id.email),
            'partner_id': partner_id.id,
            'best_deal_id': best_deal_id and best_deal_id.id or False,
        }
        data.update({key: booking[key] for key in booking.keys() if key in self._fields})
        return data

    @api.one
    def do_draft(self):
        self.state = 'draft'

    @api.one
    def confirm_booking(self):
        self.state = 'open'

        # auto-trigger after_booking (on subscribe) mail schedulers, if needed
        onbook_schedulers = self.best_deal_id.best_deal_mail_ids.filtered(
            lambda s: s.interval_type == 'after_booking')
        onbook_schedulers.execute()

    @api.one
    def button_booking_close(self):
        """ Close Registration """
        today = fields.Datetime.now()
        if self.best_deal_id.date_begin <= today:
            self.write({'state': 'done', 'date_closed': today})
        else:
            raise UserError(_("You must wait for the starting day of the deal to do this action."))

    @api.one
    def button_booking_cancel(self):
        self.state = 'cancel'

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            contact_id = self.partner_id.address_get().get('contact', False)
            if contact_id:
                contact = self.env['res.partner'].browse(contact_id)
                self.name = self.name or contact.name
                self.email = self.email or contact.email
                self.phone = self.phone or contact.phone

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(BestDealBooking, self).message_get_suggested_recipients()
        try:
            for customer in self:
                if customer.partner_id:
                    customer._message_add_suggested_recipient(recipients, partner=customer.partner_id, reason=_('Customer'))
                elif customer.email:
                    customer._message_add_suggested_recipient(recipients, email=customer.email, reason=_('Customer Email'))
        except AccessError:     # no read access rights -> ignore suggested recipients
            pass
        return recipients

    @api.multi
    def action_send_badge_email(self):
        """ Open a window to compose an email, with the template - 'best_deal_badge'
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('best_deal.best_deal_booking_mail_template_badge')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='best.deal.booking',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
