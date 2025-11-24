from odoo import models, fields


class CoffeeContractOrderLine(models.Model):
    _name = 'coffee.contract.order.line'
    _description = 'Coffee Contract Order Line'

    order_id = fields.Many2one(
        'coffee.contract.order', string='Contract Order', required=True, ondelete='cascade', index=True
    )
    product_id = fields.Many2one(
        'product.product', string='Product', required=True
    )
    quantity = fields.Float(
        string='Quantity (KG)', required=True
    )
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', required=True, default=lambda self: self.env.ref('uom.uom_kgm')
    )
    contract_line_id = fields.Many2one(
        'coffee.contract.line', string='Source Contract Line', ondelete='set null'
    )