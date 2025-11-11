from odoo import fields, models, api

# --- Merged from crm_phonecall, crm_phonecall_summary_predefined, crm_telemarketing ---

class CrmPhonecall(models.Model):
    _name = 'crm.phonecall'
    _inherit = 'mail.thread'
    _description = "Phone Call"
    _order = "date desc"

    # --- Original fields from crm_phonecall ---
    date = fields.Datetime('Date', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', 'Contact')
    company_id = fields.Many2one('res.company', 'Company')
    description = fields.Text('Description')
    opportunity_id = fields.Many2one('crm.lead', 'Lead/Opportunity', domain="[('type', '=', 'opportunity')]")
    state = fields.Selection([
        ('open', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('pending', 'Pending'),
        ('done', 'Held'),
    ], string='Status', default='open', tracking=True)
    duration = fields.Float('Duration')
    inbound = fields.Boolean('Inbound')
    # ... and other base fields ...

    # --- Modified/Added by crm_phonecall_summary_predefined ---
    name = fields.Char(related="summary_id.name", store=True, readonly=True)
    summary_id = fields.Many2one(
        comodel_name="crm.phonecall.summary",
        string="Summary",
        required=True,
        ondelete="restrict",
    )

    # --- Added by crm_telemarketing ---
    service_rating = fields.Selection([('1', 'Poor'), ('2', 'Fair'), ('3', 'Good'), ('4', 'Very Good'), ('5', 'Excellent')], string="Service Satisfaction")
    product_rating = fields.Selection([('1', 'Poor'), ('2', 'Fair'), ('3', 'Good'), ('4', 'Very Good'), ('5', 'Excellent')], string="Product Satisfaction")
    name_confirmed = fields.Boolean(string="Name Confirmed")
    address_confirmed = fields.Boolean(string="Address Confirmed")
    phone_confirmed = fields.Boolean(string="Phone Confirmed")
    email_confirmed = fields.Boolean(string="Email Confirmed")

class CrmPhonecallSummary(models.Model):
    _name = "crm.phonecall.summary"
    _description = "Crm Phonecall Summary"
    _sql_constraints = [("name_unique", "UNIQUE (name)", "Name must be unique")]

    name = fields.Char(required=True)
    phonecall_ids = fields.One2many(
        comodel_name="crm.phonecall",
        inverse_name="summary_id",
        string="Phonecalls",
    )

# ... Wizard and other related models from crm_phonecall modules ...
class CrmPhonecall2phonecall(models.TransientModel):
    _name = 'crm.phonecall2phonecall'
    _description = 'Action Schedule/Log Call'

    # ... Original wizard logic ...
    # Inherited fields
    summary_id = fields.Many2one(
        comodel_name="crm.phonecall.summary",
        string="Summary",
        required=True,
    )