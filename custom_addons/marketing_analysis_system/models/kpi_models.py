# Merged from kpi_management_framework module
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class KpiDefinition(models.Model):
    _name = 'kpi.definition'
    _description = 'KPI Definition (KPI Library)'
    _order = 'name'

    name = fields.Char(string='KPI Name', required=True)
    description = fields.Text(string='Description')
    assigned_target_count = fields.Integer(string="Assigned Targets", compute="_compute_assigned_target_count")
    kpi_type = fields.Selection([
        ('leads_registered', 'Leads Registered'),
        ('data_quality', 'Data Quality'),
    ], string='KPI Type', required=True, default='leads_registered')
    confirmation_fields = fields.Selection([
        ('name_confirmed', 'Name Confirmation'),
        ('address_confirmed', 'Address Confirmation'),
        ('phone', 'Phone Confirmation'),
    ], string='Confirmation Type', help="Which data quality metric to track")

    def _compute_assigned_target_count(self):
        for rec in self:
            rec.assigned_target_count = self.env['kpi.target.line'].search_count([('kpi_definition_id', '=', rec.id)])

    def action_view_assigned_targets(self):
        self.ensure_one()
        return {
            'name': f"KPI Targets for {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.target.line',
            'view_mode': 'tree,form',
            'domain': [('kpi_definition_id', '=', self.id)],
        }

    @api.constrains('kpi_type', 'confirmation_fields')
    def _check_confirmation_fields(self):
        for record in self:
            if record.kpi_type == 'data_quality' and not record.confirmation_fields:
                raise ValidationError("Confirmation Type is required for Data Quality KPIs.")


class KpiTarget(models.Model):
    _name = 'kpi.target'
    _description = 'KPI Target Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', compute='_compute_name', store=True, readonly=True)
    user_id = fields.Many2one('res.users', string='Assigned To', required=True, tracking=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    working_days = fields.Integer(string='Working Days (Calculated)', compute='_compute_working_days', store=True)
    target_line_ids = fields.One2many('kpi.target.line', 'target_id', string='KPI Lines')
    overall_achievement = fields.Float(string='Overall Achievement (%)', compute='_compute_overall_achievement',
                                       store=True)
    history_ids = fields.One2many('kpi.history', 'target_id', string='Activity History')
    activity_count = fields.Integer(string="Activity Count", compute='_compute_activity_count')
    last_computed_date = fields.Datetime(string='Last Computed On', readonly=True)
    data_quality_count = fields.Integer(string="Data Quality Activities", compute='_compute_data_quality_count',
                                        store=True)
    overall_achievement_leads = fields.Float(string='Leads Achievement (%)', compute='_compute_separate_achievements',
                                             store=True)
    overall_achievement_data_quality = fields.Float(string='Data Quality Achievement (%)',
                                                    compute='_compute_separate_achievements', store=True)

    @api.depends('target_line_ids.achievement_percentage', 'target_line_ids.kpi_definition_id.kpi_type')
    def _compute_separate_achievements(self):
        for record in self:
            leads_lines = record.target_line_ids.filtered(lambda l: l.kpi_definition_id.kpi_type == 'leads_registered')
            data_quality_lines = record.target_line_ids.filtered(
                lambda l: l.kpi_definition_id.kpi_type == 'data_quality')
            record.overall_achievement_leads = sum(leads_lines.mapped('achievement_percentage')) / len(
                leads_lines) if leads_lines else 0.0
            record.overall_achievement_data_quality = sum(data_quality_lines.mapped('achievement_percentage')) / len(
                data_quality_lines) if data_quality_lines else 0.0

    @api.depends('user_id.name', 'date_start', 'date_end')
    def _compute_name(self):
        for rec in self:
            if rec.user_id and rec.date_start and rec.date_end:
                rec.name = f"KPIs for {rec.user_id.name} ({rec.date_start.strftime('%b %Y')})"
            else:
                rec.name = _("New KPI Assignment")

    @api.depends('target_line_ids.achievement_percentage')
    def _compute_overall_achievement(self):
        for rec in self:
            rec.overall_achievement = sum(rec.target_line_ids.mapped('achievement_percentage')) / len(
                rec.target_line_ids) if rec.target_line_ids else 0.0

    @api.depends('date_start', 'date_end', 'user_id.resource_calendar_id')
    def _compute_working_days(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.user_id.resource_calendar_id:
                start_dt = fields.Datetime.to_datetime(rec.date_start)
                end_dt = fields.Datetime.to_datetime(rec.date_end) + timedelta(days=1)
                duration_data = rec.user_id.resource_calendar_id.get_work_duration_data(start_dt, end_dt,
                                                                                        compute_leaves=True)
                rec.working_days = round(duration_data.get('days', 0.0))
            else:
                rec.working_days = 0

    # ... Other compute and action methods from kpi_target.py ...

    def _recalculate_values(self):
        """Recalculate all KPI values for the target document."""
        # ... (Full logic from kpi_management_framework/models/kpi_target.py) ...
        pass

    @api.model
    def _cron_update_actual_values(self):
        _logger.info("Starting nightly KPI update cron job...")
        active_targets = self.search([('date_end', '>=', fields.Date.today())])
        active_targets._recalculate_values()
        _logger.info("Finished nightly KPI update cron job.")

    @api.model
    def _update_targets_for_user(self, user_id, model_name):
        # ... (Full logic from kpi_management_framework/models/kpi_target.py) ...
        pass


class KpiTargetLine(models.Model):
    _name = 'kpi.target.line'
    _description = 'KPI Target Line'
    _order = 'sequence, id'

    # ... (All fields and methods from kpi_management_framework/models/kpi_target_line.py) ...
    target_id = fields.Many2one('kpi.target', string='KPI Target', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    kpi_definition_id = fields.Many2one('kpi.definition', string='KPI Definition', required=True, ondelete='cascade')
    user_id = fields.Many2one(related='target_id.user_id', store=True, string='Assigned User')
    target_value = fields.Float(string='Target Value', required=True, default=0.0)
    actual_value = fields.Float(string='Actual Value', readonly=True, default=0.0)
    achievement_percentage = fields.Float(string='Achievement (%)', digits=(5, 2),
                                          compute='_compute_achievement_percentage', store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')], string='Status',
                             default='draft')
    date_start = fields.Date(related='target_id.date_start', store=True)
    date_end = fields.Date(related='target_id.date_end', store=True)

    @api.depends('actual_value', 'target_value', 'kpi_definition_id.kpi_type')
    def _compute_achievement_percentage(self):
        # ... (Full logic from kpi_target_line.py) ...
        pass


class KpiHistory(models.Model):
    _name = 'kpi.history'
    _description = 'KPI Activity History Log'
    _order = 'activity_date desc, id desc'

    # ... (All fields and methods from kpi_management_framework/models/kpi_history.py) ...
    target_id = fields.Many2one('kpi.target', string='KPI Target', required=True, ondelete='cascade')
    source_document = fields.Reference(
        selection=[('crm.lead', 'Lead/Opportunity'), ('telemarketing.confirmation', 'Telemarketing Confirmation')],
        string='Source Document')
    activity_date = fields.Datetime(string='Activity Date', readonly=True)
    description = fields.Text(string='Description', readonly=True)
    # ...


class TelemarketingConfirmation(models.Model):
    _name = 'telemarketing.confirmation'
    _description = 'Telemarketing Data Quality Confirmation'
    _order = 'confirmation_date desc'

    # ... (All fields and methods from kpi_management_framework/models/telemarketing_confirmation.py) ...
    name = fields.Char(required=True, default=lambda self: _('New'))
    lead_id = fields.Many2one('crm.lead', required=True, ondelete='cascade')
    telemarketer_id = fields.Many2one('res.users', required=True)
    # ...