from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fixed_discount = fields.Monetary(
        string="Fixed Discount",
        default=0.0,
        help="The fixed monetary discount amount applied to this line.",
    )

    # Use the correct, modern method for Odoo 17
    # This also corrects the fundamental calculation logic
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
                                            move_type):
        # Apply the fixed discount correctly by dividing it over the quantity
        price_unit_after_fixed_discount = price_unit
        if self.fixed_discount > 0 and quantity != 0:
            price_unit_after_fixed_discount = price_unit - (self.fixed_discount / quantity)

        # Call super with the adjusted price unit
        return super(AccountMoveLine, self)._get_price_total_and_subtotal_model(
            price_unit_after_fixed_discount,
            quantity,
            discount,
            currency,
            product,
            partner,
            taxes,
            move_type
        )
