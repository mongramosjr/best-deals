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


import babel.dates
import time
import re
import werkzeug.urls
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from openerp import http
from openerp import tools, SUPERUSER_ID
from openerp.addons.website.models.website import slug
from openerp.http import request
from openerp.tools.translate import _


class website_best_deal(http.Controller):
    @http.route(['/bestdeal', '/bestdeal/page/<int:page>', '/bestdeals', '/bestdeals/page/<int:page>'], type='http', auth="public", website=True)
    def bestdeals(self, page=1, **searches):
        cr, uid, context = request.cr, request.uid, request.context
        best_deal_obj = request.registry['best.deal']
        best_deal_type_obj = request.registry['best.deal.type']
        country_obj = request.registry['res.country']
        country_state_obj = request.registry['res.country.state']
        

        searches.setdefault('date', 'all')
        searches.setdefault('type', 'all')
        searches.setdefault('country', 'all')
        searches.setdefault('country_state', 'all')

        domain_search = {}

        def sdn(date):
            return date.replace(hour=23, minute=59, second=59).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        def sd(date):
            return date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        today = datetime.today()
        dates = [
            ['all', _('Next Deals'), [("date_end", ">", sd(today))], 0],
            ['today', _('Today'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
                0],
            ['week', _('This Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=6-today.weekday())))],
                0],
            ['nextweek', _('Next Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=7-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=13-today.weekday())))],
                0],
            ['month', _('This month'), [
                ("date_end", ">=", sd(today.replace(day=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['nextmonth', _('Next month'), [
                ("date_end", ">=", sd(today.replace(day=1) + relativedelta(months=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=2)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['old', _('Old Deals'), [
                ("date_end", "<", today.strftime('%Y-%m-%d 00:00:00'))],
                0],
        ]

        # search domains
        # TDE note: WTF ???
        current_date = None
        current_type = None
        current_country = None
        current_country_state = None
        
        for date in dates:
            if searches["date"] == date[0]:
                domain_search["date"] = date[2]
                if date[0] != 'all':
                    current_date = date[1]
        if searches["type"] != 'all':
            current_type = best_deal_type_obj.browse(cr, uid, int(searches['type']), context=context)
            domain_search["type"] = [("best_deal_type_id", "=", int(searches["type"]))]

        if searches["country_state"] != 'all':
            current_country_state = country_state_obj.browse(cr, uid, int(searches['country_state']), context=context)
            domain_search["country_state"] = [("state_id", "=", int(searches["country_state"]))]
            
        if searches["country"] != 'all' and searches["country"] != 'online':
            current_country = country_obj.browse(cr, uid, int(searches['country']), context=context)
            domain_search["country"] = ['|', ("country_id", "=", int(searches["country"])), ("country_id", "=", False)]
        elif searches["country"] == 'online':
            domain_search["country"] = [("country_id", "=", False)]
            
        def dom_without(without):
            domain = [('state', "in", ['draft', 'confirm', 'done'])]
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search
        for date in dates:
            if date[0] != 'old':
                date[3] = best_deal_obj.search(
                    request.cr, request.uid, dom_without('date') + date[2],
                    count=True, context=request.context)

        domain = dom_without('type')
        types = best_deal_obj.read_group(
            request.cr, request.uid, domain, ["id", "best_deal_type_id"], groupby="best_deal_type_id",
            orderby="best_deal_type_id", context=request.context)
        type_count = best_deal_obj.search(request.cr, request.uid, domain,
                                      count=True, context=request.context)
        types.insert(0, {
            'best_deal_type_id_count': type_count,
            'best_deal_type_id': ("all", _("All Categories"))
        })

        #country
        domain = dom_without('country')
        countries = best_deal_obj.read_group(
            request.cr, request.uid, domain, ["id", "country_id"],
            groupby="country_id", orderby="country_id", context=request.context)
        country_id_count = best_deal_obj.search(request.cr, request.uid, domain,
                                            count=True, context=request.context)
        countries.insert(0, {
            'country_id_count': country_id_count,
            'country_id': ("all", _("All Countries"))
        })
        
        #state
        domain = dom_without('country_state')
        country_states = best_deal_obj.read_group(
            request.cr, request.uid, domain, ["id", "state_id"],
            groupby="state_id", orderby="state_id", context=request.context)
        country_state_id_count = best_deal_obj.search(request.cr, request.uid, domain,
                                            count=True, context=request.context)
        country_states.insert(0, {
            'country_state_id_count': country_state_id_count,
            'country_state_id': ("all", _("All States/Provinces"))
        })

        step = 8  # Number of deals per page
        best_deal_count = best_deal_obj.search(
            request.cr, request.uid, dom_without("none"), count=True,
            context=request.context)
        pager = request.website.pager(
            url="/bestdeal",
            url_args={
                'date': searches.get('date'), 
                'type': searches.get('type'), 
                'country': searches.get('country'),
                'country_state': searches.get('country_state')
                },
            total=best_deal_count,
            page=page,
            step=step,
            scope=5)

        order = 'website_published desc, date_begin'
        if searches.get('date', 'all') == 'old':
            order = 'website_published desc, date_begin desc'
        obj_ids = best_deal_obj.search(
            request.cr, request.uid, dom_without("none"), limit=step,
            offset=pager['offset'], order=order, context=request.context)
        best_deal_ids = best_deal_obj.browse(request.cr, request.uid, obj_ids,
                                      context=request.context)

        values = {
            'current_date': current_date,
            'current_country': current_country,
            'current_country_state': current_country_state,
            'current_type': current_type,
            'best_deal_ids': best_deal_ids,
            'dates': dates,
            'types': types,
            'countries': countries,
            'country_states': country_states,
            'pager': pager,
            'searches': searches,
            'search_path': "?%s" % werkzeug.url_encode(searches),
        }

        return request.website.render("website_best_deal.index", values)

    @http.route(['/bestdeal/<model("best.deal"):best_deal>/page/<path:page>'], type='http', auth="public", website=True)
    def bestdeal_page(self, best_deal, page, **post):
        values = {
            'best_deal': best_deal,
            'main_object': best_deal
        }

        if '.' not in page:
            page = 'website_best_deal.%s' % page

        try:
            request.website.get_template(page)
        except ValueError:
            # page not found
            values['path'] = re.sub(r"^website_best_deal\.", '', page)
            values['from_template'] = 'website_best_deal.default_page'  # .strip('website_best_deal.')
            page = 'website.page_404'

        return request.website.render(page, values)

    @http.route(['/bestdeal/<model("best.deal"):best_deal>'], type='http', auth="public", website=True)
    def bestdeal(self, best_deal, **post):
        if best_deal.menu_id and best_deal.menu_id.child_id:
            target_url = best_deal.menu_id.child_id[0].url
        else:
            target_url = '/bestdeal/%s/booking' % str(best_deal.id)
        if post.get('enable_editor') == '1':
            target_url += '?enable_editor=1'
        return request.redirect(target_url)

    @http.route(['/bestdeal/<model("best.deal"):best_deal>/booking'], type='http', auth="public", website=True)
    def bestdeal_booking(self, best_deal, **post):
        values = {
            'best_deal': best_deal,
            'main_object': best_deal,
            'range': range,
        }
        return request.website.render("website_best_deal.best_deal_description_full", values)

    @http.route('/bestdeal/add_bestdeal', type='http', auth="user", methods=['POST'], website=True)
    def add_bestdeal(self, best_deal_name="New Deal", **kwargs):
        return self._add_bestdeal(best_deal_name, request.context, **kwargs)

    def _add_bestdeal(self, best_deal_name=None, context={}, **kwargs):
        if not best_deal_name:
            best_deal_name = _("New Deal")
        Best_Deal = request.registry.get('best.deal')
        date_begin = datetime.today() + timedelta(days=(14))
        vals = {
            'name': best_deal_name,
            'date_begin': date_begin.strftime('%Y-%m-%d'),
            'date_end': (date_begin + timedelta(days=(1))).strftime('%Y-%m-%d'),
            'coupons_available': 1000,
        }
        best_deal_id = Best_Deal.create(request.cr, request.uid, vals, context=context)
        best_deal = Best_Deal.browse(request.cr, request.uid, best_deal_id, context=context)
        return request.redirect("/bestdeal/%s/booking?enable_editor=1" % slug(best_deal))

    def get_formated_date(self, best_deal):
        context = request.context
        start_date = datetime.strptime(best_deal.date_begin, tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
        end_date = datetime.strptime(best_deal.date_end, tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
        month = babel.dates.get_month_names('abbreviated', locale=context.get('lang', 'en_US'))[start_date.month]
        return _('%(month)s %(start_day)s%(end_day)s') % {
            'month': month,
            'start_day': start_date.strftime("%e"),
            'end_day': (end_date != start_date and ("-"+end_date.strftime("%e")) or "")
        }

    @http.route('/bestdeal/get_country_best_deal_list', type='http', auth='public', website=True)
    def get_country_best_deals(self, **post):
        cr, uid, context, best_deal_ids = request.cr, request.uid, request.context, []
        country_obj = request.registry['res.country']
        best_deal_obj = request.registry['best.deal']
        country_code = request.session['geoip'].get('country_code')
        result = {'best_deals': [], 'country': False}
        if country_code:
            country_ids = country_obj.search(cr, uid, [('code', '=', country_code)], context=context)
            best_deal_ids = best_deal_obj.search(cr, uid, ['|', ('address_id', '=', None), ('country_id.code', '=', country_code), ('date_begin', '>=', time.strftime('%Y-%m-%d 00:00:00')), ('state', '=', 'confirm')], order="date_begin", context=context)
        if not best_deal_ids:
            best_deal_ids = best_deal_obj.search(cr, uid, [('date_begin', '>=', time.strftime('%Y-%m-%d 00:00:00')), ('state', '=', 'confirm')], order="date_begin", context=context)
        for best_deal in best_deal_obj.browse(cr, uid, best_deal_ids, context=context)[:6]:
            if country_code and best_deal.country_id.code == country_code:
                result['country'] = country_obj.browse(cr, uid, country_ids[0], context=context)
            result['best_deals'].append({
                "date": self.get_formated_date(best_deal),
                "best_deal": best_deal,
                "url": best_deal.website_url})
        return request.website.render("website_best_deal.country_best_deals_list", result)

    def _process_coupons_details(self, data):
        nb_booking = int(data.get('nb_booking-0', 0))
        if nb_booking:
            return [{'id': 0, 'name': 'Subscription', 'quantity': nb_booking, 'price': 0}]
        return []

    @http.route(['/bestdeal/<model("best.deal"):best_deal>/booking/new'], type='json', auth="public", methods=['POST'], website=True)
    def booking_new(self, best_deal, **post):
        coupons = self._process_coupons_details(post)
        if not coupons:
            return request.redirect("/bestdeal/%s" % slug(best_deal))
        return request.website._render("website_best_deal.booking_customer_details", {'coupons': coupons, 'best_deal': best_deal})

    def _process_booking_details(self, details):
        ''' Process data posted from the attendee details form. '''
        bookings = {}
        global_values = {}
        for key, value in details.iteritems():
            counter, field_name = key.split('-', 1)
            if counter == '0':
                global_values[field_name] = value
            else:
                bookings.setdefault(counter, dict())[field_name] = value
        for key, value in global_values.iteritems():
            for booking in bookings.values():
                booking[key] = value
        return bookings.values()

    @http.route(['/bestdeal/<model("best.deal"):best_deal>/booking/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def booking_confirm(self, best_deal, **post):
        cr, uid, context = request.cr, request.uid, request.context
        Booking = request.registry['best.deal.booking']
        bookings = self._process_booking_details(post)

        booking_ids = []
        for booking in bookings:
            booking['best_deal_id'] = best_deal
            booking_ids.append(
                Booking.create(
                    cr, SUPERUSER_ID,
                    Booking._prepare_customer_values(cr, uid, booking),
                    context=context))

        customers = Booking.browse(cr, uid, booking_ids, context=context)
        return request.website.render("website_best_deal.booking_complete", {
            'customers': customers,
            'best_deal': best_deal,
        })
