from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Ensure the fixed_discount field is defined here or in another inheritance.
    fixed_discount = fields.Float(string='Fixed Discount', default=0.0)

    def _prepare_invoice_line(self, **optional_values):
        # This method prepares the values for the invoice line.
        # We call super() to get the standard values.
        res = super()._prepare_invoice_line(**optional_values)

        # Ensure the fixed_discount field is also defined in the account.move.line model.
        # If not, define it there or handle the absence appropriately.

        # We add our custom fixed discount value to the dictionary.
        # Check if the fixed_discount field exists and is greater than 0.
        if self.fixed_discount > 0:
            res['fixed_discount'] = self.fixed_discount

        return res
