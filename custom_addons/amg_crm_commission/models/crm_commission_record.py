from odoo import models, fields

class CrmCommissionRecord(models.Model):
    _name = 'crm.commission.record'
    # [FIXED] Added mail.thread to support the chatter and field tracking.
    _inherit = ['mail.thread']
    _description = 'Sales Commission Record'
    _order = 'create_date desc'

    salesperson_id = fields.Many2one('res.users', string='Salesperson', required=True, readonly=True, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', required=True, readonly=True, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, tracking=True)
    commission_amount = fields.Monetary(string='Commission Amount', readonly=True, tracking=True)
    currency_id = fields.Many2one(related='sale_order_id.currency_id', readonly=True)
    state = fields.Selection([
        ('draft', 'To Invoice'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='State', default='draft', readonly=True, tracking=True)