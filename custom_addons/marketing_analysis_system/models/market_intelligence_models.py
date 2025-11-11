from odoo import models, fields, api
from odoo.exceptions import ValidationError


# --- Merged from competitor module ---
class CompetitorIndustry(models.Model):
    _name = "competitor.industry"
    _description = "Types of Competitor Industries"
    name = fields.Char("Name", required=True)
    active = fields.Boolean("Active", default=True)


class Competitor(models.Model):
    _name = 'competitor.competitor'
    _description = 'Competitor'
    name = fields.Char("Name", required=True)
    description = fields.Text("Description")
    website = fields.Char("Website")
    country_id = fields.Many2one("res.country", "Country", required=True)
    industry_ids = fields.Many2many("competitor.industry", string="Industries")
    phone = fields.Char("Phone", required=True)
    email = fields.Char("Email")
    active = fields.Boolean("Active", default=True)
    company_ids = fields.Many2many("res.company", string="Companies", required=True)
    notes = fields.Html("Notes")


# --- Merged from market_intelligence module ---
class MarketIntelligenceLine(models.Model):
    _name = 'market_intelligence.market_intelligence_line'
    _description = 'Market Intelligence Lines'
    product_id = fields.Many2one("product.product", required=True)
    unit_price = fields.Float(digits=(16, 3), required=True)
    unit_price_uom_id = fields.Many2one("uom.uom", required=True)
    stock = fields.Float(digits=(16, 3))
    stock_uom_id = fields.Many2one("uom.uom")
    market_intelligence_id = fields.Many2one("market_intelligence.market_intelligence")
    mi_date = fields.Date(related="market_intelligence_id.date", store=True)
    competitor_id = fields.Many2one(related="market_intelligence_id.competitor_id", store=True)

    @api.constrains('unit_price')
    def _check_unit_price(self):
        for line in self:
            if not line.unit_price or line.unit_price <= 0:
                raise ValidationError("Unit Price must be greater than 0.")


class MarketIntelligence(models.Model):
    _name = 'market_intelligence.market_intelligence'
    _description = 'Market Intelligence'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    name = fields.Char(string="MI Number", required=True, copy=False, readonly=True, default="New")
    date = fields.Date("Market date", default=fields.Date.today, readonly=True)
    competitor_id = fields.Many2one("competitor.competitor", string="Competitor", required=True)
    company_ids = fields.Many2many("res.company", string="Companies", required=True)
    line_ids = fields.One2many("market_intelligence.market_intelligence_line", "market_intelligence_id", required=True)
    remark = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("market_intelligence.market_intelligence") or "New"
        return super().create(vals_list)

    @api.constrains('line_ids')
    def _check_line_ids(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError("You must add at least one product line.")


# --- Merged from encounter_visit module ---
class VisitTitle(models.Model):
    _name = "encounter.visit.title"
    _description = "Visit Title"
    _order = "sequence, name"
    name = fields.Char(string="Title Name", required=True, translate=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Description")
    _sql_constraints = [('name_uniq', 'unique (name)', 'The title name must be unique!')]


class EncounterVisit(models.Model):
    _name = "encounter.encounter_visit"
    _description = "Encounter Visit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc"

    code = fields.Char(string="Code", required=True, copy=False, readonly=True, default="New")
    title_id = fields.Many2one("encounter.visit.title", string="Title", required=True)
    name = fields.Char(string="Title Name", related="title_id.name", store=True, readonly=True)
    date = fields.Datetime(string="Visit Date", default=fields.Datetime.now, required=True)
    lead_id = fields.Many2one("crm.lead", string="Lead/Opportunity", ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Customer", ondelete="cascade")
    latitude = fields.Float("Latitude", required=True)
    longitude = fields.Float("Longitude", required=True)
    notes = fields.Text("Notes")
    company_ids = fields.Many2many(comodel_name="res.company", string="Companies", readonly=True)
    team_id = fields.Many2one(comodel_name="crm.team", string="Sales Team", readonly=True)
    user_id = fields.Many2one(comodel_name="res.users", string="Responsible", readonly=True,
                              default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["code"] = self.env["ir.sequence"].next_by_code("encounter.encounter_visit") or "New"
        return super().create(vals_list)

    @api.onchange("lead_id")
    def _onchange_lead_id(self):
        if self.lead_id:
            self.partner_id = False
            self.team_id = self.lead_id.team_id
            self.user_id = self.lead_id.user_id
            self.company_ids = self.lead_id.company_ids

    # ... Other methods from encounter_visit.py ...


class ResPartner(models.Model):
    _inherit = "res.partner"

    encounter_visit_ids = fields.One2many("encounter.encounter_visit", "partner_id", string="Encounter Visits")
    encounter_visit_count = fields.Integer(compute="_compute_encounter_visit_count")

    def _compute_encounter_visit_count(self):
        for partner in self:
            partner.encounter_visit_count = len(partner.encounter_visit_ids)

    def action_view_encounter_visits(self):
        # ... action logic from res_partner.py ...
        pass