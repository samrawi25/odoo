# /crm_telemarketing/models/crm_opportunity.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CrmTeleOpportunity(models.Model):
    _name = "crm.tele_opportunity"
    _description = "Telemarketing Opportunity (AMG custom)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Opportunity Reference", required=True, tracking=True)
    lead_id = fields.Many2one("crm.lead", string="Source Lead", ondelete="set null")
    partner_id = fields.Many2one("res.partner", string="Customer", ondelete="set null")
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.uid, tracking=True)
    expected_total_sales_value = fields.Monetary(string="Expected Sales Value")
    expected_total_sales_volume = fields.Float(string="Expected Sales Volume")
    tin_number = fields.Char(string="TIN Number")
    date_of_establishment = fields.Date(string="Date of Establishment")
    capital = fields.Monetary(string="Capital")
    state = fields.Selection([("draft", "Draft"), ("qualified", "Qualified"), ("won", "Won"), ("lost", "Lost")], default="draft", string="Status", tracking=True)
    encounter_ids = fields.One2many("crm.tele_encounter", "opportunity_id", string="Encounters")

    def action_confirm_as_customer(self):
        """Convert opportunity into a res.partner customer (basic)."""
        partner_obj = self.env["res.partner"]
        for rec in self:
            if rec.partner_id:
                # already customer
                continue
            partner_vals = {
                "name": rec.name,
                "tin_number": rec.tin_number,
                "date_of_establishment": rec.date_of_establishment,
                "capital": rec.capital,
                "company_type_custom": "private",
            }
            partner = partner_obj.create(partner_vals)
            rec.partner_id = partner.id
            rec.state = "won"
        return True
