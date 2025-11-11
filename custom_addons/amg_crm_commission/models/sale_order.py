from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_record_ids = fields.One2many('crm.commission.record', 'sale_order_id', string='Commission Records')

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            _logger.info(
                f"Confirming order {order.name}, User: {order.user_id}, Commission Plan: {order.user_id.commission_plan_id if order.user_id else 'No user'}")

            if order.user_id and order.user_id.commission_plan_id:
                # Check if commission record already exists
                existing_records = self.env['crm.commission.record'].search_count([('sale_order_id', '=', order.id)])
                _logger.info(f"Existing commission records: {existing_records}")

                if not existing_records:
                    rate = order.user_id.commission_plan_id.commission_rate / 100.0
                    commission_amount = order.amount_untaxed * rate
                    _logger.info(
                        f"Creating commission record: Amount Untaxed: {order.amount_untaxed}, Rate: {rate}, Commission: {commission_amount}")

                    commission_record = self.env['crm.commission.record'].create({
                        'salesperson_id': order.user_id.id,
                        'sale_order_id': order.id,
                        'commission_amount': commission_amount,
                    })
                    _logger.info(f"Commission record created: {commission_record.id}")
            else:
                _logger.warning(f"No commission record created - missing user or commission plan")
        return res