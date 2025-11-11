# /crm_telemarketing/models/res_partner.py
from odoo import fields, models, api
import re
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    company_type_custom = fields.Selection(
        [("private", "Private"), ("trader", "Trader"), ("government", "Government")],
        string="Company Type",
        help="Extended company type for AMG.",
    )
    tin_number = fields.Char(string="TIN / Tax ID")
    date_of_establishment = fields.Date(string="Date of Establishment")
    capital = fields.Monetary(string="Capital")
    contractor_grade = fields.Char(string="Contractor Grade")
    latitude = fields.Float(string="Latitude", digits=(16, 6))
    longitude = fields.Float(string="Longitude", digits=(16, 6))
    # link to opportunities for quick access
    tele_opportunity_ids = fields.One2many("crm.tele_opportunity", "partner_id", string="Opportunities")
