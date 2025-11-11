{
    'name': 'CRM Dashboard',
    'version': '1.0',
    'summary': 'Enhanced CRM dashboard views and functionality',
    'description': """
        Adds dashboard views and functionality to the CRM module
        including sales funnel tracking.
    """,
    'author': 'AMG Holdings',
    'depends': ['crm', 'sale'],
    'data': [
        'views/crm_dashboard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
