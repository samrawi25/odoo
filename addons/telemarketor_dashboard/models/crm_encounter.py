# /crm_telemarketing/models/crm_encounter.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CrmTeleEncounter(models.Model):
    _name = "crm.tele_encounter"
    _description = "Encounter / Interaction (call, meeting, site visit)"
    _order = "date desc"
    _inherit = ["mail.thread"]

    encounter_type = fields.Selection([("call", "Call"), ("email", "Email"), ("meeting", "Meeting"), ("site_visit", "Site Visit")], required=True, string="Encounter Type")
    date = fields.Datetime(string="Date", required=True, default=fields.Datetime.now)
    notes = fields.Text(string="Notes")
    latitude = fields.Float(string="Latitude", digits=(16, 6))
    longitude = fields.Float(string="Longitude", digits=(16, 6))
    lead_id = fields.Many2one("crm.lead", string="Lead")
    opportunity_id = fields.Many2one("crm.tele_opportunity", string="Opportunity")
    partner_id = fields.Many2one("res.partner", string="Customer")
    user_id = fields.Many2one("res.users", string="Logged by", default=lambda self: self.env.uid)

    @api.model
    def create(self, vals):
        # Basic validation: must be linked to either lead/opportunity/partner
        if not (vals.get("lead_id") or vals.get("opportunity_id") or vals.get("partner_id")):
            raise ValidationError("Encounter must be linked to a Lead, Opportunity or Customer.")
        return super().create(vals)
