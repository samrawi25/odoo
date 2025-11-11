from odoo import models, fields

class CrmCommissionPlan(models.Model):
    _name = 'crm.commission.plan'
    _description = 'Sales Commission Plan'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    commission_rate = fields.Float(
        string="Commission Rate (%)",
        required=True,
        help="The percentage of the untaxed total to be paid as commission."
    )