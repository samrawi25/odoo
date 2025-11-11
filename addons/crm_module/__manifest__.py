{
    'name': 'CRM Category Enabler',
    'version': '17.0.1.0.0',
    'category': 'CRM',
    'summary': 'Enables CRM category in Apps menu',
    'description': 'This module ensures the CRM category appears in the Apps menu',
    'depends': ['crm'],  # This is crucial - depends on the CRM app
    'data': [],
    'demo': [],     
    'data': [
        'views/crm_category.xml',
        ],
    'installable': True,
    'application': True,  # Must be True to appear in Apps
    'auto_install': False,
    'license': 'LGPL-3',
}