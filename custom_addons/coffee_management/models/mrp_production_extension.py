from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    coffee_contract_id = fields.Many2one('coffee.contract', string='Source Coffee Contract', copy=False, index=True, readonly=True)
    coffee_contract_order_id = fields.Many2one(
        'coffee.contract.order',
        string='Coffee Contract Order',
        ondelete='set null',
    )