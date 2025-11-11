{
    "name": "CRM Probability Cleaner",
    "version": "17.0.1.0.0",
    "summary": "Remove probability field occurrences from CRM views (safe dynamic cleanup)",
    "category": "Technical",
    "author": "AutoFix",
    "depends": ["crm", 'crm_phonecall'],
    "data": [
        "views/crm_lead_views.xml"
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
    "website": "https://www.autofix.com",

    # This key tells Odoo to run your Python script
    "post_init_hook": "post_init_remove_probability",

    "description": """
This module removes the probability field occurrences from CRM views (safe dynamic cleanup).

This module is safe to use and does not modify any data. It only removes the probability field occurrences from CRM views.

This module is useful when you want to remove the probability field from CRM views and you don't want to lose any data.

This module is not necessary if you want to keep the probability field in CRM views.""",
}