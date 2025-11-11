# document_page/models/document_page_category.py
from odoo import models, fields

class DocumentPageCategory(models.Model):
    _name = 'document.page.category'
    _description = 'Document Page Category'

    name = fields.Char(string='Category Name', required=True)
