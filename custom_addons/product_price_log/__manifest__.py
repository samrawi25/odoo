{
    'name': "product_price_log",
    'version': '0.1',
    'summary': "Product Price Logging & Price Comparison Dashboard",
    'description': "Tracks product price changes and provides a dashboard comparing AMG vs competitor prices",
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    "license": "AGPL-3",
    'category': 'Tools',
    'depends': ['base', 'product', 'market_intelligence', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_price_log_views.xml',
        'views/price_comparison_report.xml',
        'views/price_comparison_dashboard_views.xml',
    ],
    "assets": {
        "web.assets_backend": [
            # Chart.js library
            "product_price_log/static/src/css/select2.min.css",
            "product_price_log/static/src/js/select2.min.js",

            #"product_price_log/static/lib/chartjs/chart.umd.min.js",
            "product_price_log/static/lib/chartjs/Chart.js",
            # JavaScript file
            "product_price_log/static/src/js/price_comparison_dashboard.js",
            # XML template file
            "product_price_log/static/src/xml/price_comparison_dashboard.xml",
            "product_price_log/static/src/css/price_comparison_dashboard.scss",
        ],
    },
    'installable': True,
    'application': True,
}