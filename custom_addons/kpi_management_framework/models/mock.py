from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class KpiTargetLine(models.Model):
    _name = 'kpi.target.line'
    _description = 'KPI Target Line'

    target_id = fields.Many2one('kpi.target', string='KPI Target', required=True, ondelete='cascade')
    kpi_definition_id = fields.Many2one('kpi.definition', string='KPI Definition', required=True)
    actual_value = fields.Float(string='Actual Value', compute='_compute_actual_value', store=True)

    @api.depends('kpi_definition_id', 'target_id.date_start', 'target_id.date_end')
    def _compute_actual_value(self):
        for line in self:
            if line.kpi_definition_id.kpi_type == 'leads_registered':
                line.actual_value = line.target_id._calculate_leads_registered(line.target_id, line.kpi_definition_id, [])
            elif line.kpi_definition_id.kpi_type == 'data_quality':
                line.actual_value = line.target_id._calculate_data_quality(line.target_id, line.kpi_definition_id, [])
            else:
                line.actual_value = 0.0

    @api.model
    def create(self, vals):
        record = super(KpiTargetLine, self).create(vals)
        record.target_id._recalculate_values()
        return record

    def write(self, vals):
        result = super(KpiTargetLine, self).write(vals)
        for line in self:
            line.target_id._recalculate_values()
        return result

class KpiTarget(models.Model):
    _name = 'kpi.target'
    _description = 'KPI Target Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', compute='_compute_name', store=True, readonly=True)
    user_id = fields.Many2one('res.users', string='Assigned To', required=True, tracking=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    working_days = fields.Integer(
        string='Working Days (Calculated)',
        compute='_compute_working_days',
        store=True
    )

    target_line_ids = fields.One2many('kpi.target.line', 'target_id', string='KPI Lines')

    overall_achievement = fields.Float(
        string='Overall Achievement (%)',
        compute='_compute_overall_achievement',
        store=True
    )

    history_ids = fields.One2many('kpi.history', 'target_id', string='Activity History')
    activity_count = fields.Integer(string="Activity Count", compute='_compute_activity_count')
    last_computed_date = fields.Datetime(string='Last Computed On', readonly=True)

    data_quality_count = fields.Integer(
        string="Data Quality Activities",
        compute='_compute_data_quality_count',
        store=True
    )

    overall_achievement_leads = fields.Float(
        string='Overall Achievement (Leads)',
        compute='_compute_separate_achievements',
        store=True
    )

    overall_achievement_data_quality = fields.Float(
        string='Overall Achievement (Data Quality)',
        compute='_compute_separate_achievements',
        store=True
    )

    @api.depends('target_line_ids.achievement_percentage', 'target_line_ids.kpi_definition_id.kpi_type')
    def _compute_separate_achievements(self):
        for record in self:
            leads_lines = record.target_line_ids.filtered(
                lambda l: l.kpi_definition_id.kpi_type == 'leads_registered'
            )
            data_quality_lines = record.target_line_ids.filtered(
                lambda l: l.kpi_definition_id.kpi_type == 'data_quality'
            )

            if leads_lines:
                record.overall_achievement_leads = sum(
                    leads_lines.mapped('achievement_percentage')
                ) / len(leads_lines)
            else:
                record.overall_achievement_leads = 0.0

            if data_quality_lines:
                record.overall_achievement_data_quality = sum(
                    data_quality_lines.mapped('achievement_percentage')
                ) / len(data_quality_lines)
            else:
                record.overall_achievement_data_quality = 0.0

    @api.depends('user_id.name', 'date_start', 'date_end')
    def _compute_name(self):
        for record in self:
            if record.user_id and record.date_start and record.date_end:
                record.name = f"KPIs for {record.user_id.name} ({record.date_start.strftime('%b %Y')})"
            else:
                record.name = "New KPI Assignment"

    @api.depends('target_line_ids.achievement_percentage')
    def _compute_overall_achievement(self):
        for record in self:
            if record.target_line_ids:
                record.overall_achievement = sum(record.target_line_ids.mapped('achievement_percentage')) / len(
                    record.target_line_ids)
            else:
                record.overall_achievement = 0.0

    @api.depends('date_start', 'date_end', 'user_id.resource_calendar_id')
    def _compute_working_days(self):
        for rec in self:
            calendar = rec.user_id.resource_calendar_id

            if rec.date_start and rec.date_end and calendar:
                start_dt = fields.Datetime.to_datetime(rec.date_start)
                end_dt = fields.Datetime.to_datetime(rec.date_end) + timedelta(days=1)
                duration_data = calendar.get_work_duration_data(
                    start_dt,
                    end_dt,
                    compute_leaves=True
                )
                rec.working_days = round(duration_data.get('days', 0.0))
            else:
                rec.working_days = 0

    @api.depends('history_ids')
    def _compute_activity_count(self):
        for target in self:
            target.activity_count = len(target.history_ids)

    @api.depends('history_ids.data_quality_type')
    def _compute_data_quality_count(self):
        for target in self:
            target.data_quality_count = len(target.history_ids.filtered(
                lambda h: h.data_quality_type and h.data_quality_type != False
            ))

    def _get_target_line_id(self, target, kpi):
        line = target.target_line_ids.filtered(lambda l: l.kpi_definition_id == kpi)
        return line.id if line else False

    def action_view_activities(self):
        self.ensure_one()
        return {
            'name': _('Tracked Activities for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.history',
            'view_mode': 'tree,form',
            'domain': [('target_id', '=', self.id)],
        }

    def action_view_data_quality(self):
        self.ensure_one()
        return {
            'name': _('Data Quality Activities'),
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.history',
            'view_mode': 'tree,form',
            'domain': [('target_id', '=', self.id), ('data_quality_type', '!=', False)],
            'context': {'create': False},
        }

    def action_recalculate_values(self):
        self._recalculate_values()

    def _recalculate_values(self):
        KpiHistory = self.env['kpi.history']

        for target in self:
            _logger.info(f"Recalculating KPI Target: {target.name} for user {target.user_id.name}")

            target.history_ids.unlink()
            history_vals_list = []

            for line in target.target_line_ids:
                kpi = line.kpi_definition_id
                _logger.info(f"Processing KPI line: {kpi.name} with type: {kpi.kpi_type}")

                calculated_value = 0.0

                if kpi.kpi_type == 'leads_registered':
                    calculated_value = self._calculate_leads_registered(target, kpi, history_vals_list)
                elif kpi.kpi_type == 'data_quality':
                    calculated_value = self._calculate_data_quality(target, kpi, history_vals_list)

                line.actual_value = calculated_value
                _logger.info(f"KPI '{kpi.name}' calculated value: {calculated_value}")

            if history_vals_list:
                KpiHistory.create(history_vals_list)
                _logger.info(f"Created {len(history_vals_list)} history records")

            target.last_computed_date = fields.Datetime.now()
            _logger.info(f"Completed recalculation for KPI Target '{target.name}'.")

    def _calculate_leads_registered(self, target, kpi, history_vals_list):
        date_from = fields.Datetime.to_datetime(target.date_start)
        date_to = fields.Datetime.to_datetime(target.date_end) + timedelta(days=1) - timedelta(seconds=1)

        domain = [
            ('user_id', '=', target.user_id.id),
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to),
        ]

        try:
            leads = self.env['crm.lead'].search(domain)

            for lead in leads:
                history_vals_list.append({
                    'target_id': target.id,
                    'target_line_id': self._get_target_line_id(target, kpi),
                    'kpi_definition_id': kpi.id,
                    'source_document_model': 'crm.lead',
                    'source_document_id': lead.id,
                    'activity_date': lead.create_date,
                    'description': f"Lead Registered: {lead.name}"
                })

            return len(leads)

        except Exception as e:
            _logger.error(f"Error counting leads for KPI '{kpi.name}': {e}")
            return 0

    def _calculate_data_quality(self, target, kpi, history_vals_list):
        date_from = fields.Datetime.to_datetime(target.date_start)
        date_to = fields.Datetime.to_datetime(target.date_end) + timedelta(days=1) - timedelta(seconds=1)

        domain = [
            ('telemarketer_id', '=', target.user_id.id),
            ('confirmation_date', '>=', date_from),
            ('confirmation_date', '<=', date_to),
        ]

        try:
            confirmations = self.env['telemarketing.confirmation'].search(domain)

            total_score = 0
            confirmation_count = len(confirmations)

            for confirmation in confirmations:
                score = confirmation.overall_score
                total_score += score

                history_vals_list.append({
                    'target_id': target.id,
                    'target_line_id': self._get_target_line_id(target, kpi),
                    'kpi_definition_id': kpi.id,
                    'source_document_model': 'telemarketing.confirmation',
                    'source_document_id': confirmation.id,
                    'activity_date': confirmation.confirmation_date,
                    'description': f"Data Quality Check: {confirmation.name} - Score: {score:.1f}%",
                    'data_quality_score': score,
                    'data_quality_type': kpi.confirmation_fields,
                })

            if confirmation_count > 0:
                return total_score / confirmation_count
            return 0.0

        except Exception as e:
            _logger.error(f"Error calculating data quality for KPI '{kpi.name}': {e}")
            return 0.0

    @api.model
    def _cron_update_actual_values(self):
        _logger.info("Starting nightly KPI update cron job...")
        active_targets = self.search([('date_end', '>=', fields.Date.today())])
        active_targets._recalculate_values()
        _logger.info("Finished nightly KPI update cron job.")

    @api.model
    def _update_targets_for_user(self, user_id, model_name):
        if not user_id or not model_name:
            return

        _logger.info(f"Updating KPI targets for user {user_id} due to {model_name} change")

        active_targets = self.search([
            ('user_id', '=', user_id),
            ('date_end', '>=', fields.Date.today()),
            ('date_start', '<=', fields.Date.today()),
        ])

        if active_targets:
            _logger.info(f"Found {len(active_targets)} active targets to update")
            active_targets._recalculate_values()
        else:
            _logger.info("No active targets found to update")
