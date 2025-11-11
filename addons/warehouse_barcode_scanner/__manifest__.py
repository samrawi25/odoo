{
    'name': 'Warehouse Barcode Scanner',
    'version': '17.0.1.0',
    'category': 'Inventory',
    'summary': 'Adds a barcode scanning interface to the warehouse module for Community Edition. s',
    'description': """
This module adds a barcode scanning interface to the warehouse module for Community Edition.

The barcode scanner allows users to quickly add products to their warehouse by scanning barcodes. The barcode scanner can be used in combination with the barcode scanner app on Android or iOS devices.

The barcode scanner can be accessed from the Warehouse app by clicking on the "Scan barcode" button in the top right corner.

The barcode scanner works by using the device's camera to scan barcodes and then sending the barcode data to the server for validation and processing. The barcode scanner can be configured to use different barcode types and barcode formats.

The barcode scanner can be customized to include additional features such as product variants, serial numbers, and location assignment.

This module is compatible with Odoo Community Edition 17.0.
""",
    'author': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'license': 'AGPL-3',
    'depends': ['stock', 'web'],
    'data': [
        'views/stock_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Ensure the CSS is loaded first
            #'warehouse_barcode_scanner/static/src/css/barcode_scanner.css',
            # Bundle JS and XML together
            'warehouse_barcode_scanner/static/src/components/barcode_scanner.js',
            'warehouse_barcode_scanner/static/src/xml/barcode_scanner.xml',
        ],
    },
    'installable': True,
    'application': True,
}