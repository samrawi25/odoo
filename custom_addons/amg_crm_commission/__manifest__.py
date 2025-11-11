{
    'name': 'AMG CRM Sales Commission',
    'version': '17.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Manage sales commissions for salespeople.',
    'depends': ['crm', 'sale_management', 'account', 'sales_team',],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_commission_plan_views.xml',
        'views/crm_commission_record_views.xml',
        'views/res_users_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    "license": "AGPL-3",
}