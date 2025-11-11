from odoo import models, fields, api


class VisitTitle(models.Model):
    _name = "encounter.visit.title"
    _description = "Visit Title"
    _order = "sequence, name"

    name = fields.Char(string="Title Name", required=True, translate=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Description")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The title name must be unique!'),
    ]