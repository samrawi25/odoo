# Merged from product_price_log module
from odoo import models, fields, api

class ProductPriceLog(models.Model):
    _name = "product.price.log"
    _description = "Product Price Log"
    _order = "changed_date desc"

    product_id = fields.Many2one('product.product', string="Product", required=True, ondelete='cascade')
    old_price = fields.Float(string="Old Price")
    new_price = fields.Float(string="New Price")
    changed_date = fields.Datetime(string="Changed On", default=fields.Datetime.now, readonly=True)
    changed_by = fields.Many2one('res.users', string="Changed By", default=lambda self: self.env.user, readonly=True)

class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        if 'lst_price' in vals:
            price_logs = self.env['product.price.log']
            for product in self:
                if product.lst_price != vals['lst_price']:
                    price_logs.create({
                        'product_id': product.id,
                        'old_price': product.lst_price,
                        'new_price': vals['lst_price'],
                    })
        return super().write(vals)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        if 'list_price' in vals:
            price_logs = self.env['product.price.log']
            for template in self:
                if template.list_price != vals['list_price']:
                    for product in template.product_variant_ids:
                        price_logs.create({
                            'product_id': product.id,
                            'old_price': template.list_price,
                            'new_price': vals['list_price'],
                        })
        return super().write(vals)