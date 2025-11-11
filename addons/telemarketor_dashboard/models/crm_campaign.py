# /crm_telemarketing/models/crm_campaign.py
from odoo import models, fields


class CrmTeleCampaign(models.Model):
    _name = "crm.tele_campaign"
    _description = "Telemarketing Campaign"

    name = fields.Char(required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    budget = fields.Monetary()
    campaign_type = fields.Selection([("email", "Email"), ("sms", "SMS"), ("event", "Event")], string="Type")
    description = fields.Text()
    lead_ids = fields.One2many("crm.lead", "campaign_id", string="Leads")
