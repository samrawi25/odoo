from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Sales related fields
    sales_funnel = fields.Many2one(
        'sale.order',
        string='Sales Funnel',
        compute='_compute_sales_funnel',
        store=True
    )
    sale_order_count = fields.Integer(
        string='Sale Orders',
        compute='_compute_sales_metrics',
        store=True
    )

    # Marketing related fields
    campaign_performance = fields.Float(
        string='Campaign Performance',
        compute='_compute_campaign_metrics',
        store=True
    )

    # Visitor/engagement metrics
    visitor_page_count = fields.Integer(
        string='Page Views',
        compute='_compute_visitor_metrics',
        store=True
    )
    visitor_sessions_count = fields.Integer(
        string='Sessions',
        compute='_compute_visitor_metrics',
        store=True
    )

    # Lead/conversion metrics
    lead_count = fields.Integer(
        string='Leads',
        default=1
    )
    conversion_rate = fields.Float(
        string='Conversion Rate',
        compute='_compute_conversion_metrics',
        store=True
    )
    registration_count = fields.Integer(
        string='Registrations',
        compute='_compute_event_metrics',
        store=True
    )

    # Computation methods
    @api.depends('order_ids')
    def _compute_sales_funnel(self):
        for lead in self:
            lead.sales_funnel = lead.order_ids[:1] if lead.order_ids else False

    @api.depends('order_ids')
    def _compute_sales_metrics(self):
        for lead in self:
            lead.sale_order_count = len(lead.order_ids)

    @api.depends('campaign_id', 'probability')
    def _compute_campaign_metrics(self):
        for lead in self:
            lead.campaign_performance = lead.probability * 0.8 if lead.campaign_id else 0.0

    @api.depends('visitor_ids')
    def _compute_visitor_metrics(self):
        for lead in self:
            lead.visitor_page_count = len(lead.visitor_ids)
            lead.visitor_sessions_count = 0  # Default until proper field found

    @api.depends('probability', 'stage_id')
    def _compute_conversion_metrics(self):
        for lead in self:
            lead.conversion_rate = lead.probability if lead.probability else 0.0

    @api.depends('event_lead_ids')
    def _compute_event_metrics(self):
        for lead in self:
            lead.registration_count = len(lead.event_lead_ids)
