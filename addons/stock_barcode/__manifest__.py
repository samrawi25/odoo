{
    'name': 'Barcode Scanner for Warehouses',
    'version': '17.0.1.0',
    'summary': 'Barcode scanner for warehouses',
    'description': """
        This module allows you to use barcode scanners in your warehouses to track inventory more efficiently.
    """,
    'author': 'Samrawi AMG',
    'category': 'Inventory',
    'depends': ['base', 'stock'],
    'data': [
       # 'security/ir.model.access.csv',
        'views/stock_barcode_views.xml',
        'report/stock_barcode_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',  # Use the appropriate license
}
