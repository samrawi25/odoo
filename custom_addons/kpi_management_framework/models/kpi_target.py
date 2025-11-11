from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


# Add signal registration for automatic updates
# def _register_hook(self):
#     super(KpiTarget, self)._register_hook()
#     self.env['crm.lead']._fields['create_date']._triggers.add(
#         (self._update_targets_on_lead_change, ['crm.lead'])
#     )


class KpiTarget(models.Model):
    _name = 'kpi.target'
    _description = 'KPI Target Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', compute='_compute_name', store=True, readonly=True)
    user_id = fields.Many2one('res.users', string='Assigned To', required=True, tracking=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    # holiday_schedule_id = fields.Many2one('holiday.schedule', string='Holiday Schedule')
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

    # Data Quality Count Field
    data_quality_count = fields.Integer(
        string="Data Quality Activities",
        compute='_compute_data_quality_count',
        store=True
    )
    # Add new fields for separate achievement calculations
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
        """Compute separate achievement percentages for each KPI type"""
        for record in self:
            leads_lines = record.target_line_ids.filtered(
                lambda l: l.kpi_definition_id.kpi_type == 'leads_registered'
            )
            data_quality_lines = record.target_line_ids.filtered(
                lambda l: l.kpi_definition_id.kpi_type == 'data_quality'
            )

            # Calculate leads achievement
            if leads_lines:
                record.overall_achievement_leads = sum(
                    leads_lines.mapped('achievement_percentage')
                ) / len(leads_lines)
            else:
                record.overall_achievement_leads = 0.0

            # Calculate data quality achievement
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

            # Check for all required fields
            if rec.date_start and rec.date_end and calendar:

                # Convert Date fields to Datetime in UTC for calendar methods
                start_dt = fields.Datetime.to_datetime(rec.date_start)
                # To include the entire end day, add a full day to end_dt
                end_dt = fields.Datetime.to_datetime(rec.date_end) + timedelta(days=1)

                # Use the standard Odoo resource.calendar method
                # to get the duration data (including days and hours)
                duration_data = calendar.get_work_duration_data(
                    start_dt,
                    end_dt,
                    compute_leaves=True
                )

                # 'days' is a float representing the working time.
                # We round it to the nearest integer for 'working_days'
                rec.working_days = round(duration_data.get('days', 0.0))
            else:
                rec.working_days = 0

    @api.depends('history_ids')
    def _compute_activity_count(self):
        for target in self:
            target.activity_count = len(target.history_ids)

    @api.depends('history_ids.data_quality_type')
    def _compute_data_quality_count(self):
        """Compute number of data quality activities - FIXED VERSION"""
        for target in self:
            # Count history records that have data_quality_type set (not False)
            target.data_quality_count = len(target.history_ids.filtered(
                lambda h: h.data_quality_type and h.data_quality_type != False
            ))

    def _get_target_line_id(self, target, kpi):
        """Helper method to get the target line ID for a specific KPI"""
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
        """Action to view data quality activities"""
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
        """Button to manually trigger recalculation for all lines."""
        self._recalculate_values()

    def _recalculate_values(self):
        """Recalculate all KPI values for the target document."""
        KpiHistory = self.env['kpi.history']

        for target in self:
            _logger.info(f"Recalculating KPI Target: {target.name} for user {target.user_id.name}")

            # Clear all old history for this entire target document
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

                # Update the line with calculated value
                line.actual_value = calculated_value
                _logger.info(f"KPI '{kpi.name}' calculated value: {calculated_value}")

            # Create all history records in one batch
            if history_vals_list:
                KpiHistory.create(history_vals_list)
                _logger.info(f"Created {len(history_vals_list)} history records")

            # Update the master record's timestamp
            target.last_computed_date = fields.Datetime.now()
            _logger.info(f"Completed recalculation for KPI Target '{target.name}'.")

    def _calculate_leads_registered(self, target, kpi, history_vals_list):
        """Calculate count of leads registered by user"""
        date_from = fields.Datetime.to_datetime(target.date_start)
        date_to = fields.Datetime.to_datetime(target.date_end) + timedelta(days=1) - timedelta(seconds=1)

        domain = [
            ('user_id', '=', target.user_id.id),
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to),
        ]

        try:
            leads = self.env['crm.lead'].search(domain)

            # Create history records
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
        """Calculate data quality percentage based on telemarketer confirmations
        Modified to use 'leads_registered' count as the denominator."""
        date_from = fields.Datetime.to_datetime(target.date_start)
        date_to = fields.Datetime.to_datetime(target.date_end) + timedelta(days=1) - timedelta(seconds=1)

        # 1. Get the data quality scores (Numerator)
        confirmation_domain = [
            ('telemarketer_id', '=', target.user_id.id),
            ('confirmation_date', '>=', date_from),
            ('confirmation_date', '<=', date_to),
        ]

        try:
            # Get all telemarketing confirmation records for this user and period
            confirmations = self.env['telemarketing.confirmation'].search(confirmation_domain)

            total_score = 0
            for confirmation in confirmations:
                # Use the overall_score from telemarketing confirmation
                score = confirmation.overall_score
                total_score += score

                # Create history record WITH data_quality_type (unchanged)
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

            # 2. Get the lead count (Denominator)
            lead_domain = [
                ('user_id', '=', target.user_id.id),
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to),
            ]
            lead_count = self.env['crm.lead'].search(lead_domain)

            # 3. Return the average score: total_score / lead_count
            if len(lead_count) > 0:
                # The actual value of data quality is the average of individual data quality scores
                # divided by the number of leads the user registered.
                return total_score / len(lead_count)
            print("the total_score=",total_score/lead_count)

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
        """Update KPI targets for a user when related records change"""
        if not user_id or not model_name:
            return

        _logger.info(f"Updating KPI targets for user {user_id} due to {model_name} change")

        # Find active targets for this user
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

    @api.model
    def _update_targets_on_lead_change(self, lead):
        """Automatically update targets when a lead is created or modified"""
        if lead.user_id:
            self._update_targets_for_user(lead.user_id.id, 'crm.lead')
