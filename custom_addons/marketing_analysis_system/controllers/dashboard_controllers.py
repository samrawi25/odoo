# Combined from crm_telemarketing and product_price_log
from odoo import http
from odoo.http import request
from collections import defaultdict
from datetime import datetime, timedelta


class MarketingDashboardControllers(http.Controller):

    @http.route('/telemarketing/dashboard/data', type='json', auth='user')
    def get_telemarketing_dashboard_data(self, start_date=None, end_date=None):
        # ... (Content of crm_telemarketing/controllers/telemarketing_dashboard.py) ...
        # This controller remains largely the same but now has access to other models
        # in the same module without cross-module dependencies.

        # Date filter
        domain = []
        if start_date:
            domain.append(('create_date', '>=', start_date))
        if end_date:
            domain.append(('create_date', '<=', end_date))

        # --- 1. Leads Data ---
        total_leads = request.env['crm.lead'].search_count(domain)
        total_competitors = request.env['competitor.competitor'].search_count([])  # No date domain on competitors
        converted_domain = domain + [('type', '=', 'opportunity')]
        converted_leads = request.env['crm.lead'].search_count(converted_domain)
        conversion_rate = (converted_leads / total_leads) * 100 if total_leads > 0 else 0.0

        # --- 2. Call KPIs from report.telemarketing ---
        Report = request.env['report.telemarketing']
        report_domain = []
        if start_date:
            report_domain.append(('date', '>=', start_date))
        if end_date:
            report_domain.append(('date', '<=', end_date))

        call_data = Report.read_group(
            report_domain,
            fields=['total_calls', 'duration', 'done_calls'],
            groupby=[]
        )
        if call_data:
            kpi_calls = call_data[0]
            total_calls = kpi_calls.get('total_calls', 0)
            avg_duration = kpi_calls.get('duration', 0)
        else:
            total_calls, avg_duration = 0, 0

        # ... (Rest of the original telemarketing_dashboard.py logic) ...
        # (The logic for bar charts, pivot tables, and salesperson data remains valid)

        chart_data_raw = Report.read_group(report_domain, fields=['total_calls'], groupby=['date:day', 'direction'],
                                           lazy=False)
        bar_chart_data = {'labels': [], 'datasets': {}}
        labels_set = set()
        for rec in chart_data_raw:
            day = rec['date:day']
            direction = rec['direction']
            count = rec['total_calls']
            labels_set.add(day)
            if direction not in bar_chart_data['datasets']: bar_chart_data['datasets'][direction] = {}
            bar_chart_data['datasets'][direction][day] = count
        bar_chart_data['labels'] = sorted(list(labels_set))

        pivot_data_raw = Report.read_group(report_domain, fields=['total_calls'], groupby=['user_id', 'direction'],
                                           lazy=False)
        pivot_data = defaultdict(lambda: defaultdict(int))
        for rec in pivot_data_raw:
            user_name = rec['user_id'][1] if rec['user_id'] else 'Unassigned'
            direction = rec['direction']
            pivot_data[user_name][f"{direction}_total"] = rec['total_calls']

        # Salesperson KPI data
        KpiLine = request.env['kpi.target.line']
        kpi_domain = []
        if start_date: kpi_domain.append(('date_start', '>=', start_date))
        if end_date: kpi_domain.append(('date_end', '<=', end_date))

        kpi_lines = KpiLine.search_read(kpi_domain, ['user_id', 'kpi_definition_id', 'target_value', 'actual_value',
                                                     'achievement_percentage'])
        salesperson_data_raw = defaultdict(lambda: {})
        for line in kpi_lines:
            user_name = line['user_id'][1]
            kpi_def = request.env['kpi.definition'].browse(line['kpi_definition_id'][0])
            if kpi_def.kpi_type == 'leads_registered':
                salesperson_data_raw[user_name].update({
                    'leads_registered_target': line['target_value'],
                    'leads_registered_actual': line['actual_value'],
                    'leads_registered_percent': line['achievement_percentage'],
                })
            elif kpi_def.kpi_type == 'data_quality':
                salesperson_data_raw[user_name].update({
                    'data_quality_target': line['target_value'],
                    'data_quality_actual': line['actual_value'],
                    'data_quality_percent': line['achievement_percentage'],
                })

        # Final salesperson data processing
        leads = request.env['crm.lead'].search_read(domain, ['user_id', 'type'])
        sp_lead_data = defaultdict(lambda: {'total_leads': 0, 'converted_leads': 0})
        for lead in leads:
            if lead['user_id']:
                sp_name = lead['user_id'][1]
                sp_lead_data[sp_name]['total_leads'] += 1
                if lead['type'] == 'opportunity':
                    sp_lead_data[sp_name]['converted_leads'] += 1

        salesperson_data = []
        all_salespersons = set(sp_lead_data.keys()) | set(salesperson_data_raw.keys())
        for sp in all_salespersons:
            data = {
                'salesperson': sp,
                'total_leads': sp_lead_data[sp].get('total_leads', 0),
                'converted_leads': sp_lead_data[sp].get('converted_leads', 0),
                'conversion_rate': round(
                    (sp_lead_data[sp].get('converted_leads', 0) / sp_lead_data[sp].get('total_leads', 1)) * 100, 2),
                'leads_registered_target': salesperson_data_raw[sp].get('leads_registered_target', 0),
                'leads_registered_actual': salesperson_data_raw[sp].get('leads_registered_actual', 0),
                'leads_registered_percent': salesperson_data_raw[sp].get('leads_registered_percent', 0),
                'data_quality_target': salesperson_data_raw[sp].get('data_quality_target', 0),
                'data_quality_actual': salesperson_data_raw[sp].get('data_quality_actual', 0),
                'data_quality_percent': salesperson_data_raw[sp].get('data_quality_percent', 0),
            }
            salesperson_data.append(data)

        return {
            'kpis': {
                'total_leads': total_leads,
                'converted_leads': converted_leads,
                'conversion_rate': round(conversion_rate, 2),
                'total_calls': total_calls,
                'avg_duration': round(avg_duration, 2),
                'total_competitors': total_competitors
            },
            'bar_chart': bar_chart_data,
            'pivot_table': {'rows': pivot_data},
            'salesperson_data': salesperson_data,
        }

    @http.route('/price_comparison/data', type='json', auth='user')
    def get_price_comparison_data(self, product_ids=None, competitor_ids=None, start_date=None, end_date=None):
        # This is a simplified version of the method from product_price_log/price_comparison_report.py
        # It's better to keep complex logic in the model and call it from the controller.
        price_data = request.env['price.comparison.report'].get_price_comparison_data(
            product_ids=product_ids,
            competitor_ids=competitor_ids,
            start_date=start_date,
            end_date=end_date
        )
        return price_data