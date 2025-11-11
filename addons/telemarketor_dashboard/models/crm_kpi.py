# /crm_telemarketing/models/crm_kpi.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, date


class CrmKpiTarget(models.Model):
    _name = "crm.kpi_target"
    _description = "KPI Target"

    name = fields.Char(required=True)
    user_id = fields.Many2one("res.users", string="Assigned To")
    kpi_type = fields.Selection([
        ("leads_per_day", "Leads per day"),
        ("lead_quality", "Lead data quality"),
        ("calls_made", "Calls made"),
        ("orders_generated", "Orders generated"),
    ], string="KPI Type", required=True)
    period_start = fields.Date()
    period_end = fields.Date()
    target_value = fields.Float()
    achieved_value = fields.Float(compute="_compute_achieved", store=True)

    @api.depends("user_id", "period_start", "period_end", "kpi_type")
    def _compute_achieved(self):
        for rec in self:
            rec.achieved_value = 0.0
            start = rec.period_start
            end = rec.period_end
            if not (start and end):
                continue
            # convert to datetime for comparisons
            start_dt = fields.Datetime.to_datetime(start.strftime("%Y-%m-%d") + " 00:00:00") if isinstance(start, date) else fields.Datetime.to_datetime(str(start) + " 00:00:00")
            end_dt = fields.Datetime.to_datetime(end.strftime("%Y-%m-%d") + " 23:59:59") if isinstance(end, date) else fields.Datetime.to_datetime(str(end) + " 23:59:59")

            if rec.kpi_type == "leads_per_day" and rec.user_id:
                leads = self.env["crm.lead"].search([
                    ("assigned_user_id", "=", rec.user_id.id),
                    ("create_date", ">=", start_dt),
                    ("create_date", "<=", end_dt)
                ])
                days = max(1, (end - start).days + 1)
                rec.achieved_value = len(leads) / days

            elif rec.kpi_type == "lead_quality" and rec.user_id:
                # lead quality = % of leads with phone_number & email filled
                leads = self.env["crm.lead"].search([
                    ("assigned_user_id", "=", rec.user_id.id),
                    ("create_date", ">=", start_dt),
                    ("create_date", "<=", end_dt)
                ])
                if not leads:
                    rec.achieved_value = 0.0
                else:
                    good = 0
                    for l in leads:
                        if l.phone_number and l.email_from:
                            good += 1
                    rec.achieved_value = (good / len(leads)) * 100.0

            elif rec.kpi_type == "calls_made" and rec.user_id:
                # count encounters of type 'call' logged by user
                encounters = self.env["crm.tele_encounter"].search([
                    ("user_id", "=", rec.user_id.id),
                    ("encounter_type", "=", "call"),
                    ("date", ">=", start_dt),
                    ("date", "<=", end_dt)
                ])
                rec.achieved_value = len(encounters)

            elif rec.kpi_type == "orders_generated" and rec.user_id:
                # count sale orders created for partner(s) where user is owner of opportunity or lead assigned
                # Simple heuristic: sale.order where create_uid is the user AND date between range
                orders = self.env["sale.order"].search([
                    ("create_uid", "=", rec.user_id.id),
                    ("confirmation_date", ">=", start_dt) if self._field_exists("sale.order", "confirmation_date") else ("date_order", ">=", start_dt),
                    ("confirmation_date", "<=", end_dt) if self._field_exists("sale.order", "confirmation_date") else ("date_order", "<=", end_dt),
                ])
                rec.achieved_value = len(orders)

    def _field_exists(self, model_name, field_name):
        Model = self.env.registry.get(self.env.uid).get(model_name)
        # safe check for presence of field in registry, fallback True if unclear
        try:
            return field_name in self.env[model_name]._fields
        except Exception:
            return True
