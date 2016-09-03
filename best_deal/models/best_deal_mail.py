# -*- coding: utf-8 -*-
##############################################################################
#
#    3D2N, Discounts and Coupons
#    Copyright (C) 2016
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Discounts and Coupons and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################




from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import api, fields, models, tools


_INTERVALS = {
    'hours': lambda interval: relativedelta(hours=interval),
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'now': lambda interval: relativedelta(hours=0),
}


class BestDealMail(models.Model):
    """ Deal automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on deals since Odoo 9. A cron exists
    that periodically checks for mailing to run. """
    _name = 'best.deal.mail'

    best_deal_id = fields.Many2one('best.deal', string='Deal', required=True, ondelete='cascade')
    sequence = fields.Integer('Display order')
    interval_nbr = fields.Integer('Interval', default=1)
    interval_unit = fields.Selection([
        ('now', 'Immediately'),
        ('hours', 'Hour(s)'), ('days', 'Day(s)'),
        ('weeks', 'Week(s)'), ('months', 'Month(s)')],
        string='Unit', default='hours', required=True)
    interval_type = fields.Selection([
        ('after_booking', 'After each booking'),
        ('before_deal', 'Before the deal'),
        ('after_deal', 'After the deal')],
        string='When to Run ', default="before_deal", required=True)
    template_id = fields.Many2one(
        'mail.template', string='Email to Send',
        domain=[('model', '=', 'best.deal.booking')], required=True, ondelete='restrict',
        help='This field contains the template of the mail that will be automatically sent')
    scheduled_date = fields.Datetime('Scheduled Sent Mail', compute='_compute_scheduled_date', store=True)
    mail_booking_ids = fields.One2many('best.deal.mail.booking', 'scheduler_id')
    mail_sent = fields.Boolean('Mail Sent on Deal')
    done = fields.Boolean('Sent', compute='_compute_done', store=True)

    @api.one
    @api.depends('mail_sent', 'interval_type', 'best_deal_id.booking_ids', 'mail_booking_ids')
    def _compute_done(self):
        if self.interval_type in ['before_deal', 'after_deal']:
            self.done = self.mail_sent
        else:
            self.done = len(self.mail_booking_ids) == len(self.best_deal_id.booking_ids) and all(filter(lambda line: line.mail_sent, self.mail_booking_ids))

    @api.one
    @api.depends('best_deal_id.state', 'best_deal_id.date_begin', 'interval_type', 'interval_unit', 'interval_nbr')
    def _compute_scheduled_date(self):
        if self.best_deal_id.state not in ['confirm', 'done']:
            self.scheduled_date = False
        else:
            if self.interval_type == 'after_booking':
                date, sign = self.best_deal_id.create_date, 1
            elif self.interval_type == 'before_deal':
                date, sign = self.best_deal_id.date_begin, -1
            else:
                date, sign = self.best_deal_id.date_end, 1

            self.scheduled_date = datetime.strptime(date, tools.DEFAULT_SERVER_DATETIME_FORMAT) + _INTERVALS[self.interval_unit](sign * self.interval_nbr)

    @api.one
    def execute(self):
        if self.interval_type == 'after_booking':
            # update booking lines
            lines = []
            for booking in filter(lambda item: item not in [mail_reg.booking_id for mail_reg in self.mail_booking_ids], self.best_deal_id.booking_ids):
                lines.append((0, 0, {'booking_id': booking.id}))
            if lines:
                self.write({'mail_booking_ids': lines})
            # execute scheduler on bookings
            self.mail_booking_ids.filtered(lambda booking: booking.scheduled_date and booking.scheduled_date <= datetime.strftime(fields.datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT)).execute()
        else:
            if not self.mail_sent:
                self.best_deal_id.mail_bookings(self.template_id.id)
                self.write({'mail_sent': True})
        return True

    @api.model
    def run(self, autocommit=False):
        schedulers = self.search([('done', '=', False), ('scheduled_date', '<=', datetime.strftime(fields.datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT))])
        for scheduler in schedulers:
            scheduler.execute()
            if autocommit:
                self.env.cr.commit()
        return True


class BestDealMailBooking(models.Model):
    _name = 'best.deal.mail.booking'
    _description = 'Booking Mail Scheduler'
    _rec_name = 'scheduler_id'
    _order = 'scheduled_date DESC'

    scheduler_id = fields.Many2one('best.deal.mail', 'Mail Scheduler', required=True, ondelete='cascade')
    booking_id = fields.Many2one('best.deal.booking', 'Customer', required=True, ondelete='cascade')
    scheduled_date = fields.Datetime('Scheduled Time', compute='_compute_scheduled_date', store=True)
    mail_sent = fields.Boolean('Mail Sent')

    @api.one
    def execute(self):
        if self.booking_id.state in ['open', 'done'] and not self.mail_sent:
            self.scheduler_id.template_id.send_mail(self.booking_id.id)
            self.write({'mail_sent': True})

    @api.one
    @api.depends('booking_id', 'scheduler_id.interval_unit', 'scheduler_id.interval_type')
    def _compute_scheduled_date(self):
        if self.booking_id:
            date_open = self.booking_id.date_open
            date_open_datetime = date_open and datetime.strptime(date_open, tools.DEFAULT_SERVER_DATETIME_FORMAT) or fields.datetime.now()
            self.scheduled_date = date_open_datetime + _INTERVALS[self.scheduler_id.interval_unit](self.scheduler_id.interval_nbr)
        else:
            self.scheduled_date = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
