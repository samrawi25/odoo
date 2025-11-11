from odoo import fields, models, tools, api


# --- From crm_phonecall ---
class CrmPhonecallReport(models.Model):
    _name = "crm.phonecall.report"
    _auto = False
    _description = "Phonecalls Analysis Report"

    # ... (All fields from original file) ...
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'crm_phonecall_report')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW crm_phonecall_report AS (
                -- ... SQL from original file ...
            )
        """)


# --- From crm_telemarketing ---
class ReportTelemarketing(models.Model):
    _name = "report.telemarketing"
    _description = "Telemarketing Report"
    _auto = False

    # ... (All fields from original file) ...
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_telemarketing AS (
                -- ... SQL from original file, combining crm_telemarketing_call and crm_phonecall ...
            )
        """)


class ReportTelemarketingDashboard(models.TransientModel):
    _name = "report.telemarketing_dashboard.dashboard"
    _description = "Telemarketing Dashboard Data"
    # ... (All fields and methods from original file) ...


# --- From product_price_log ---
class PriceComparisonReport(models.Model):
    _name = 'price.comparison.report'
    _description = 'Price Comparison Report'
    _auto = False

    # ... (All fields from original file) ...

    @api.model
    def get_price_comparison_data(self, product_ids=None, competitor_ids=None, start_date=None, end_date=None):
        # ... (Full logic from original file) ...
        pass

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW price_comparison_report AS (
                -- ... SQL from original file combining product_price_log and market_intelligence_line ...
            )
        """)
