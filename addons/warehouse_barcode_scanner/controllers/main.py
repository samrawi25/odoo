from odoo import http
from odoo.http import request

class BarcodeScannerController(http.Controller):

    @http.route('/warehouse_barcode_scanner/scan_barcode', type='json', auth='user')
    def scan_barcode(self, barcode, picking_id):
        picking = request.env['stock.picking'].browse(int(picking_id))
        if not picking.exists():
            return {'error': 'Picking not found.'}

        # Search for a product with the scanned barcode
        product = request.env['product.product'].search([('barcode', '=', barcode)], limit=1)

        if product:
            # Check if the product is in the picking
            move_line = picking.move_line_ids.filtered(lambda ml: ml.product_id == product)
            if move_line:
                move_line.qty_done += 1
                return {
                    'success': True,
                    'message': f'Added {product.name}',
                    'product_name': product.name,
                    'qty_done': move_line.qty_done,
                    'product_id': product.id,
                }
            else:
                return {'error': f'Product {product.name} not in this transfer.'}

        # You can add logic here to scan locations, lots, etc.

        return {'error': 'No product, location, or command found for this barcode.'}