from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockBarcode(models.Model):
    _inherit = 'stock.picking'

    def action_open_barcode_scanner(self):
        _logger.info("Opening barcode scanner for picking: %s", self.name)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Barcode Scanner',
            'res_model': 'stock.barcode.scanner',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_picking_id': self.id},
        }
