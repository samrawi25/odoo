# document_page/__manifest__.py
{
    'name': 'Document Page',
    'version': '17.0.1.0.0',
    'summary': 'Create and manage documentation pages.',
    'author': 'Samrawi',
    'website': 'https://www.yourcompany.com',
    'category': 'Quality control',
    'description': """
This module allows you to create and manage documentation pages.
===============================================================

This module allows you to create and manage documentation pages. You can create categories and pages, and assign access rights to them. You can also add images and files to the pages.

The module also includes a search function that allows you to search for pages by name or content.

This module is part of the Management System application.
    """,
    # MODIFIED: Added 'custom_base' as a dependency.
    'depends': ['base'],
    'data': [
        # Views must be loaded before the access rights that refer to them
        'views/document_page_views.xml',
        'views/document_page_category_views.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
