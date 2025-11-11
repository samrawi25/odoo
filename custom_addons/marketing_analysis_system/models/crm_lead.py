from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import re


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # --- From crm_lead_code ---
    code = fields.Char(
        string="Lead Number", required=True, default="New", readonly=True, copy=False
    )
    _sql_constraints = [
        ("crm_lead_unique_code", "UNIQUE (code)", _("The code must be unique!")),
    ]

    # --- From crm_lead_geolocation ---
    latitude = fields.Float("Latitude", digits=(16, 6))
    longitude = fields.Float("Longitude", digits=(16, 6))
    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
        help="Companies associated with this lead."
    )

    # --- From crm_telemarketing ---
    telemarketing_call_ids = fields.One2many(
        "crm.telemarketing.call",
        "lead_id",
        string="Telemarketing Calls"
    )
    data_quality_score = fields.Integer(
        string="Data Quality Score (%)",
        compute="_compute_data_quality_score",
        store=True,
    )

    # --- From encounter_visit ---
    encounter_visit_ids = fields.One2many("encounter.encounter_visit", "lead_id", string="Encounter Visits")
    encounter_visit_count = fields.Integer(compute="_compute_encounter_visit_count", string="Visit Count")

    # --- From custom_crm ---
    tin_number = fields.Char(string="TIN Number", size=20)

    # --- MERGED create method from crm_lead_code and kpi_management_framework ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "New") == "New":
                sequence = self.env.ref("marketing_analysis_system.sequence_lead", raise_if_not_found=False)
                if sequence:
                    vals["code"] = sequence.next_by_id()
                else:
                    vals["code"] = "New"

        records = super(CrmLead, self).create(vals_list)

        for rec in records:
            # Trigger KPI update
            if rec.user_id:
                self.env['kpi.target'].sudo()._update_targets_for_user(rec.user_id.id, 'crm.lead')

        return records

    # --- From custom_crm ---
    @api.constrains('tin_number', 'email_from')
    def _check_tin_number_and_email(self):
        for lead in self:
            if lead.tin_number and not lead.tin_number.isdigit():
                raise ValidationError(_("TIN Number must only contain digits."))
            if lead.email_from and not re.match(r"[^@]+@[^@]+\.[^@]+", lead.email_from):
                raise ValidationError(_("Invalid email format."))

    # --- From crm_telemarketing ---
    @api.depends(
        'phonecall_ids.name_confirmed', 'phonecall_ids.address_confirmed', 'phonecall_ids.phone_confirmed',
        'telemarketing_call_ids.name_confirmed', 'telemarketing_call_ids.address_confirmed',
        'telemarketing_call_ids.phone_confirmed'
    )
    def _compute_data_quality_score(self):
        for lead in self:
            # ... (Full logic from crm_lead_telemarketing.py) ...
            latest_call = self.env['crm.telemarketing.call'].search([('lead_id', '=', lead.id)], order='date desc',
                                                                    limit=1)
            if not latest_call:
                lead.data_quality_score = 0
                continue
            score = 0
            if latest_call.name_confirmed: score += 1
            if latest_call.address_confirmed: score += 1
            if latest_call.phone_confirmed: score += 1
            lead.data_quality_score = int((score / 3.0) * 100)

    def action_view_data_quality_calls(self):
        # ... (Logic from crm_lead_telemarketing.py) ...
        return {
            'name': 'Data Quality History',
            'type': 'ir.actions.act_window',
            'res_model': 'report.telemarketing',
            'view_mode': 'tree',
            'domain': [('lead_id', '=', self.id)],
        }

    # --- From encounter_visit ---
    def _compute_encounter_visit_count(self):
        for lead in self:
            lead.encounter_visit_count = len(lead.encounter_visit_ids)

    def action_view_encounter_visits(self):
        return {
            "name": "Encounter Visits",
            "type": "ir.actions.act_window",
            "res_model": "encounter.encounter_visit",
            "view_mode": "tree,form,lmap",
            "domain": [("lead_id", "=", self.id)],
            "context": {"default_lead_id": self.id},
        }