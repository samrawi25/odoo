from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    commission_plan_id = fields.Many2one('crm.commission.plan', string='Commission Plan')