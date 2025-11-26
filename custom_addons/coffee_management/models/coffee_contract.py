from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CoffeeContract(models.Model):
    _name = 'coffee.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Coffee Master Contract'
    _rec_name = 'contract_number'
    _order = 'contract_date desc, contract_number desc'

    contract_number = fields.Char(string='Contract Number', required=True, copy=False, readonly=True,
                                  default=lambda self: _('New'))
    buyer_id = fields.Many2one('res.partner', string='Buyer Name', required=True, tracking=True)
    contract_date = fields.Date(string='Date of Contract', default=fields.Date.today, required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    contract_line_ids = fields.One2many('coffee.contract.line', 'contract_id', string='Contract Lines', copy=True)

    # Smart Buttons
    contract_order_ids = fields.One2many('coffee.contract.order', 'contract_ref_id', string='Contract Orders')
    contract_order_count = fields.Integer(string='Contract Orders Count', compute='_compute_contract_order_count')

    picking_ids = fields.One2many(related='contract_order_ids.picking_ids', string='Deliveries', readonly=True)#, search=True)
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_delivery_count')
    manufacturing_order_ids = fields.One2many(related='contract_order_ids.manufacturing_order_ids',
                                              string='Manufacturing Orders', readonly=True)
    manufacturing_count = fields.Integer(string='Manufacturing Orders Count', compute='_compute_manufacturing_count')

    # Fulfillment Fields
    delivered_kg = fields.Float(string="Total Delivered (KG)", compute='_compute_fulfillment', store=True)
    fulfillment_percentage = fields.Float(string="Fulfillment (%)", compute='_compute_fulfillment', store=True,
                                          digits=(16, 2))
    shipment_status = fields.Selection([
        ('pending', 'Pending'), ('partial', 'Partially Shipped'), ('fulfilled', 'Fulfilled'),
        ('over_fulfilled', 'Over Fulfilled'), ('cancelled', 'Cancelled'),
    ], string='Shipment Status', compute='_compute_fulfillment', store=True)

    expected_delivery_date = fields.Date(string='Expected Delivery Date', tracking=True)
    actual_delivery_date = fields.Date(string='Actual Delivery Date', compute='_compute_actual_delivery_date',
                                       store=True)

    shipment_period_month = fields.Selection([
        ('jan', 'January'), ('feb', 'February'), ('mar', 'March'), ('apr', 'April'),
        ('may', 'May'), ('jun', 'June'), ('jul', 'July'), ('aug', 'August'),
        ('sep', 'September'), ('oct', 'October'), ('nov', 'November'), ('dec', 'December'),
    ], string='Shipment Period (Month)', required=True)
    shipment_period_year = fields.Integer(string='Shipment Period (Year)',
                                          default=lambda self: fields.Date.today().year, required=True)
    notes = fields.Text(string='Internal Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('contract_number', _('New')) == _('New'):
                vals['contract_number'] = self.env['ir.sequence'].next_by_code('coffee.contract') or _('New')
        return super().create(vals_list)

    @api.depends('contract_order_ids')
    def _compute_contract_order_count(self):
        for contract in self:
            contract.contract_order_count = len(contract.contract_order_ids)

    @api.depends('picking_ids')
    def _compute_delivery_count(self):
        for contract in self:
            contract.delivery_count = len(contract.picking_ids)

    @api.depends('manufacturing_order_ids')
    def _compute_manufacturing_count(self):
        for contract in self:
            contract.manufacturing_count = len(contract.manufacturing_order_ids)

    @api.depends('contract_line_ids.quantity_kg', 'picking_ids.state', 'picking_ids.move_line_ids.quantity')
    def _compute_fulfillment(self):
        for contract in self:
            total_ordered_kg = sum(contract.contract_line_ids.mapped('quantity_kg'))
            done_pickings = contract.picking_ids.filtered(lambda p: p.state == 'done')
            total_delivered_kg = sum(done_pickings.move_line_ids.mapped('quantity'))

            contract.delivered_kg = total_delivered_kg
            contract.fulfillment_percentage = (
                        total_delivered_kg / total_ordered_kg * 100.0) if total_ordered_kg > 0 else 0.0

            if contract.state == 'cancelled':
                contract.shipment_status = 'cancelled'
            elif total_delivered_kg <= 0:
                contract.shipment_status = 'pending'
            elif total_delivered_kg < total_ordered_kg:
                contract.shipment_status = 'partial'
            elif total_delivered_kg == total_ordered_kg:
                contract.shipment_status = 'fulfilled'
            else:
                contract.shipment_status = 'over_fulfilled'

    @api.depends('picking_ids.date_done')
    def _compute_actual_delivery_date(self):
        for contract in self:
            done_pickings = contract.picking_ids.filtered(lambda p: p.state == 'done' and p.date_done)
            contract.actual_delivery_date = max(done_pickings.mapped('date_done')) if done_pickings else False

    def action_confirm_contract(self):
        self.ensure_one()
        if not self.contract_line_ids:
            raise UserError(_("You cannot confirm a contract with no product lines."))
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        self.contract_order_ids.filtered(lambda o: o.state not in ['shipped', 'cancelled']).action_cancel()

    def action_done(self):
        self.write({'state': 'done'})

    def action_reset_to_draft(self):
        if any(order.state != 'cancelled' for order in self.contract_order_ids):
            raise UserError(
                _("You cannot reset a contract to draft if it has active orders. Please cancel the orders first."))
        self.write({'state': 'draft'})

    # --- View Actions (Smart Buttons) ---
    def action_view_delivery(self):
        return {'name': _('Delivery Orders'), 'type': 'ir.actions.act_window', 'res_model': 'stock.picking',
                'view_mode': 'tree,form', 'domain': [('id', 'in', self.picking_ids.ids)]}

    def action_view_manufacturing_orders(self):
        return {'name': _('Manufacturing Orders'), 'type': 'ir.actions.act_window', 'res_model': 'mrp.production',
                'view_mode': 'tree,form', 'domain': [('id', 'in', self.manufacturing_order_ids.ids)]}

    def action_view_contract_orders(self):
        return {'name': _('Contract Orders'), 'type': 'ir.actions.act_window', 'res_model': 'coffee.contract.order',
                'view_mode': 'tree,form', 'domain': [('id', 'in', self.contract_order_ids.ids)]}