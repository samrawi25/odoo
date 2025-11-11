from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()
        for invoice in self.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.invoice_origin):
            comm_records = self.env['crm.commission.record'].search([
                ('sale_order_id.name', '=', invoice.invoice_origin),
                ('state', '=', 'draft')
            ])
            if comm_records:
                comm_records.write({'state': 'invoiced', 'invoice_id': invoice.id})
        return res

    def write(self, vals):
        # We need to check the payment_state before the write, because it will be changed
        # by the super() call.
        invoices_to_check = self.filtered(
            lambda inv: inv.state == 'posted' and 'payment_state' in vals and vals['payment_state'] in ('paid', 'in_payment')
        )
        res = super().write(vals)
        for invoice in invoices_to_check:
            comm_records = self.env['crm.commission.record'].search([
                ('invoice_id', '=', invoice.id),
                ('state', '=', 'invoiced')
            ])
            if comm_records:
                comm_records.write({'state': 'paid'})
        return res