# document_page/models/document_page.py
from odoo import models, fields


class DocumentPage(models.Model):
    _name = 'document.page'
    _description = 'Document Page'

    # Adding parent/child support for hierarchical documents as required by dependent modules
    _parent_store = True
    _parent_name = "parent_id"  # Defines the field to use for the hierarchy

    name = fields.Char(string='Title', required=True)

    # ADD THIS: The field mgmtsystem_manual needs for its domain and context
    parent_id = fields.Many2one(
        'document.page',
        string='Parent Page',
        ondelete='cascade',
        index=True
    )

    # ADD THIS: An optional but highly recommended field for performance with _parent_store
    parent_path = fields.Char(index=True, unaccent=False)

    category_id = fields.Many2one(
        'document.page.category',
        string='Category',
        required=False
    )
    template = fields.Html(string='Content')
    type = fields.Char(string='Type')
