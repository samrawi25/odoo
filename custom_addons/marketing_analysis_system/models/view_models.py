# Merged from leaflet_map module
from odoo import fields, models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(selection_add=[("lmap", "Leaflet Map")])


class IrActionsActWindowView(models.Model):
    _inherit = "ir.actions.act_window.view"

    view_mode = fields.Selection(selection_add=[("lmap", "Leaflet Map")], ondelete={"lmap": "cascade"})