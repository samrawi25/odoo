{
    'name': 'Marketing Analysis System',
    'version': '17.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'A unified system for market intelligence, KPI tracking, and advanced CRM functionalities.',
    'author': 'AMG holdings',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'crm',
        'calendar',
        'sales_team',
        'product',
        'uom',
        'mail',
        'resource',
        'sale_management',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/groups.xml',
        'security/record_rules.xml',

        # Data
        'data/crm_lead_sequences.xml',
        'data/market_intelligence_sequences.xml',
        'data/kpi_data.xml',
        'data/sample_users.xml',

        # Views
        'views/crm_lead_views.xml',
        'views/crm_phonecall_views.xml',
        'views/product_views.xml',
        'views/market_intelligence_views.xml',
        'views/encounter_visit_views.xml',
        'views/kpi_views.xml',
        'views/reporting_views.xml',

        # Menus (loaded last)
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Libraries (de-duplicated)
            'marketing_analysis_system/static/lib/select2.min.css',
            'marketing_analysis_system/static/lib/select2.min.js',
            'marketing_analysis_system/static/lib/Chart.js',

            # Custom CSS/SCSS
            'marketing_analysis_system/static/src/css/price_comparison_dashboard.scss',

            # Custom JavaScript
            'marketing_analysis_system/static/src/js/leaflet_map_controller.js',
            'marketing_analysis_system/static/src/js/leaflet_map_renderer.js',
            'marketing_analysis_system/static/src/js/leaflet_map_view.js',
            'marketing_analysis_system/static/src/js/crm_lead_geo_capture.js',
            'marketing_analysis_system/static/src/js/encounter_visit_geo_capture.js',
            'marketing_analysis_system/static/src/js/price_comparison_dashboard.js',
            'marketing_analysis_system/static/src/js/telemarketing_dashboard.js',
        ],
        'web.assets_qweb': [
            'marketing_analysis_system/static/src/xml/leaflet_map_templates.xml',
            'marketing_analysis_system/static/src/xml/price_comparison_dashboard.xml',
            'marketing_analysis_system/static/src/xml/telemarketing_dashboard_templates.xml',
        ],
    },
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}