from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockBarcodeScanner(models.TransientModel):
    _name = 'stock.barcode.scanner'
    _description = 'Barcode Scanner'

    barcode = fields.Char(string='Barcode', required=True)
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True)

    def action_scan_barcode(self):
        _logger.info("Scanning barcode: %s", self.barcode)
        picking = self.env['stock.picking'].search([('name', '=', self.barcode)], limit=1)
        if picking:
            _logger.info("Picking found: %s", picking.name)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Barcode Scanned',
                    'message': f'Picking {picking.name} has been found.',
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        else:
            _logger.info("No picking found for barcode: %s", self.barcode)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Barcode Not Found',
                    'message': f'No picking associated with barcode {self.barcode} found.',
                    'type': 'danger',
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }

    def action_cancel(self):
        _logger.info("Barcode scanner action cancelled")
        return {'type': 'ir.actions.act_window_close'}
