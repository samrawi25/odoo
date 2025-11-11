# quality_control_oca/models/mrp_production.py
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_confirm(self):
        # First, run the original confirmation logic from Odoo
        res = super(MrpProduction, self).action_confirm()

        # Check if our integration setting is enabled
        if not self.env.user.has_group('quality_control_oca.group_quality_control_oca_mrp_integration'):
            return res

        # A robust, two-step search for quality points using the CORRECT field names.
        # Step 1: Find the 'Manufacturing Operation' trigger record by its 'name'.
        mrp_trigger = self.env['qc.trigger'].search([
            ('name', '=', 'Manufacturing Operation')
        ], limit=1)

        # If no such trigger exists, log a warning and do nothing.
        if not mrp_trigger:
            _logger.warning("OCA Quality: Could not find a QC Trigger with name 'Manufacturing Operation'. Skipping inspection creation.")
            return res

        for order in self:
            # Step 2: Now, search for tests using the ID of the trigger we just found.
            # The field on 'qc.test' that links to the trigger is named 'trigger'.
            qc_points = self.env['qc.test'].search([
                ('trigger', '=', mrp_trigger.id),
                '|',
                ('product_ids', 'in', order.product_id.id),
                '|',
                ('product_category_ids', 'in', order.product_id.categ_id.id),
                '&',
                ('product_ids', '=', False),
                ('product_category_ids', '=', False),
            ])

            if qc_points:
                _logger.info(f"OCA Quality: Found {len(qc_points)} quality points for MO {order.name}. Creating inspections.")

            # For each relevant Quality Point, create a new Inspection
            for point in qc_points:
                self.env['qc.inspection'].create({
                    'name': f"Inspection for {order.name}",
                    'test': point.id,
                    'product_id': order.product_id.id,
                    # Link the inspection to the manufacturing order
                    'reference': f'mrp.production,{order.id}',
                    'state': 'draft',
                })

        return res
