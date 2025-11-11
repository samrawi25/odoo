# /crm_telemarketing/models/crm_lead.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


PHONE_REGEX = re.compile(r"^(\+251|0)?9\d{8}$")  # Ethiopian formats like +2519..., 09... (basic)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    company_name = fields.Char(string="Company Name")
    company_type = fields.Selection([("private", "Private"), ("trader", "Trader"), ("government", "Government")], string="Company Type")
    full_name = fields.Char(string="Full Name")
    phone_number = fields.Char(string="Phone Number")
    remark = fields.Text(string="Remark")
    assigned_user_id = fields.Many2one("res.users", string="Brand Representative")
    # link to our custom Opportunity (one lead -> 0..1 opportunity)
    tele_opportunity_id = fields.Many2one("crm.tele_opportunity", string="Tele Opportunity")
    campaign_id = fields.Many2one("crm.tele_campaign", string="Campaign")

    _sql_constraints = [
        ('lead_phone_unique', 'unique(phone_number)', 'A lead with this phone number already exists.')
    ]

    @api.constrains("phone_number")
    def _check_phone_number(self):
        for rec in self:
            if rec.phone_number:
                if not PHONE_REGEX.match(rec.phone_number.strip()):
                    raise ValidationError("Phone number must be in Ethiopian format, e.g. +2519xxxxxxxx or 09xxxxxxxx.")

    @api.model
    def create(self, vals):
        # ensure assigned_user_id is set to current user if not provided
        if not vals.get("assigned_user_id"):
            vals["assigned_user_id"] = self.env.uid
        return super().create(vals)

    def action_convert_to_opportunity(self):
        """Create a crm.tele_opportunity from a lead, copy key fields."""
        for lead in self:
            if lead.tele_opportunity_id:
                continue
            opp_vals = {
                "name": lead.name or (lead.company_name or lead.full_name),
                "expected_total_sales_value": 0.0,
                "expected_total_sales_volume": 0.0,
                "lead_id": lead.id,
                "partner_id": lead.partner_id.id or False,
                "owner_id": lead.assigned_user_id.id or lead.user_id.id or self.env.uid,
                "tin_number": lead.partner_id.tin_number or False,
            }
            opp = self.env["crm.tele_opportunity"].create(opp_vals)
            lead.tele_opportunity_id = opp.id
        return True
