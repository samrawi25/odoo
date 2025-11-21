# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CoffeeContract(models.Model):
    _name = 'coffee.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Coffee Contract'
    _rec_name = 'contract_number'
    _order = 'contract_date desc, contract_number desc'

    contract_number = fields.Char(string='Contract Number', required=True, copy=False, readonly=True, default='New')
    buyer_id = fields.Many2one('res.partner', string='Buyer Name', required=True, tracking=True)
    contract_date = fields.Date(string='Date of Contract', default=fields.Date.today(), required=True, tracking=True)

    # Fulfillment Fields
    delivered_kg = fields.Float(string="Delivered KG", compute='_compute_fulfillment', store=True)
    fulfillment_percentage = fields.Float(string="Fulfillment (%)", compute='_compute_fulfillment', store=True,
                                          digits=(16, 2))
    shipment_status = fields.Selection([
        ('pending', 'Pending'), ('partial', 'Partially Shipped'), ('fulfilled', 'Fulfilled'),
        ('over_fulfilled', 'Over Fulfilled'), ('cancelled', 'Cancelled'),
    ], string='Shipment Status', compute='_compute_delivered_quantity', store=True)

    # Date & Period
    shipment_period_month = fields.Selection([
        ('jan', 'January'), ('feb', 'February'), ('mar', 'March'), ('apr', 'April'),
        ('may', 'May'), ('jun', 'June'), ('jul', 'July'), ('aug', 'August'),
        ('sep', 'September'), ('oct', 'October'), ('nov', 'November'), ('dec', 'December'),
    ], string='Shipment Period (Month)', required=True)
    shipment_period_year = fields.Integer(string='Shipment Period (Year)',
                                          default=lambda self: fields.Date.today().year, required=True)
    expected_delivery_date = fields.Date(string='Expected Delivery Date', tracking=True)
    actual_delivery_date = fields.Date(string='Actual Delivery Date', compute='_compute_actual_delivery_date')
    notes = fields.Text(string='Internal Notes')

    state = fields.Selection([
        ('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    contract_line_ids = fields.One2many('coffee.contract.line', 'contract_id', string='Contract Lines', copy=True,
                                        auto_join=True)

    # Smart Button Fields
    picking_ids = fields.One2many('stock.picking', 'coffee_contract_id', string='Deliveries')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_delivery_count')
    manufacturing_order_ids = fields.One2many('mrp.production', 'coffee_contract_id', string='Manufacturing Orders')
    manufacturing_count = fields.Integer(string='Manufacturing Orders', compute='_compute_manufacturing_count')

    # MO-related fields (Kept for compatibility, but creation logic is moved to Order)
    manufacturing_route_id = fields.Many2one(
        'stock.route', string='Manufacturing Route', domain="[('product_selectable', '=', True)]",
        help="Route to use for manufacturing products"
    )
    auto_create_mo = fields.Boolean(
        string='Auto Create MO (Legacy)', default=False, help="This flag is now managed on the Contract Order model."
    )

    # Add security fields at the beginning of the class
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        tracking=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('contract_number') or vals.get('contract_number') == 'New':
                vals['contract_number'] = self.env['ir.sequence'].next_by_code('coffee.contract') or 'New'
        return super().create(vals_list)

    @api.depends('contract_line_ids.quantity_tons', 'picking_ids.state',
                 'picking_ids.move_ids.product_uom_qty', 'picking_ids.move_ids.state')
    def _compute_fulfillment(self):
        KG_PER_TON = 1000
        for contract in self:
            total_ordered_kg = sum(line.quantity_tons * KG_PER_TON for line in contract.contract_line_ids)
            total_delivered_kg = 0.0

            done_pickings = contract.picking_ids.filtered(
                lambda p: p.picking_type_code == 'outgoing' and p.state == 'done'
            )
            contract_product_ids = contract.contract_line_ids.mapped('product_id').ids

            for picking in done_pickings:
                for move in picking.move_ids.filtered(lambda m: m.state == 'done'):
                    if move.product_id.id in contract_product_ids:
                        # Assumes KG is the base unit of measure for stock moves in this scenario
                        total_delivered_kg += move.product_uom_qty

            contract.delivered_kg = total_delivered_kg
            contract.fulfillment_percentage = (
                (total_delivered_kg / total_ordered_kg) * 100.0
                if total_ordered_kg > 0 else 0.0
            )

    @api.depends('delivered_kg', 'contract_line_ids.quantity_tons', 'state')
    def _compute_delivered_quantity(self):
        KG_PER_TON = 1000
        for contract in self:
            total_ordered_kg = sum(line.quantity_tons * KG_PER_TON for line in contract.contract_line_ids)

            if contract.state == 'cancelled':
                contract.shipment_status = 'cancelled'
            elif contract.delivered_kg >= total_ordered_kg and total_ordered_kg > 0:
                contract.shipment_status = 'fulfilled' if contract.delivered_kg == total_ordered_kg else 'over_fulfilled'
            elif contract.delivered_kg > 0 and contract.delivered_kg < total_ordered_kg:
                contract.shipment_status = 'partial'
            else:
                contract.shipment_status = 'pending'

    @api.depends('picking_ids')
    def _compute_delivery_count(self):
        for contract in self:
            contract.delivery_count = len(contract.picking_ids)

    @api.depends('manufacturing_order_ids')
    def _compute_manufacturing_count(self):
        for contract in self:
            contract.manufacturing_count = len(contract.manufacturing_order_ids)

    @api.depends('picking_ids.date_done')
    def _compute_actual_delivery_date(self):
        for contract in self:
            done_pickings = contract.picking_ids.filtered(
                lambda p: p.picking_type_code == 'outgoing' and p.state == 'done'
            )
            contract.actual_delivery_date = done_pickings and max(done_pickings.mapped('date_done')) or False

    def action_confirm_contract(self):
        self.ensure_one()
        if not self.contract_line_ids:
            raise UserError(_("You cannot confirm a contract with no lines."))
        if self.state != 'draft':
            raise UserError(_("Only draft contracts can be confirmed."))

        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        if not warehouse:
            raise UserError(_("No warehouse is configured for this company."))

        # Create delivery order
        picking_type = warehouse.out_type_id
        picking = self.env['stock.picking'].create({
            'partner_id': self.buyer_id.id,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': self.buyer_id.property_stock_customer.id or self.env.ref(
                'stock.stock_location_customers').id,
            'origin': self.contract_number,
            'coffee_contract_id': self.id,
            'scheduled_date': self.expected_delivery_date or fields.Datetime.now(),
        })

        KG_PER_TON = 1000
        for line in self.contract_line_ids:
            # Create stock move for delivery
            self.env['stock.move'].create({
                'name': line.name or line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity_tons * KG_PER_TON,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            })

        picking.action_confirm()
        self.write({'state': 'confirmed'})
        return True

    def action_cancel(self):
        self.ensure_one()
        if self.picking_ids:
            self.picking_ids.filtered(lambda p: p.state != 'done').action_cancel()
        self.write({'state': 'cancelled'})
        return True

    def action_done(self):
        self.ensure_one()
        if self.fulfillment_percentage < 100:
            raise UserError(_("Cannot mark as done until fulfillment is 100%"))
        self.write({'state': 'done'})
        return True

    def action_reset_to_draft(self):
        self.ensure_one()
        if any(picking.state != 'cancel' for picking in self.picking_ids):
            raise UserError(_("Cannot reset to draft with active deliveries"))
        self.write({'state': 'draft'})
        return True

    def action_view_delivery(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        action['domain'] = [('id', 'in', self.picking_ids.ids)]
        action['context'] = {'create': False}
        return action

    def action_view_manufacturing_orders(self):
        action = self.env['ir.actions.act_window']._for_xml_id('mrp.mrp_production_action')
        action['domain'] = [('id', 'in', self.manufacturing_order_ids.ids)]
        action['context'] = {
            'create': False,
            'default_coffee_contract_id': self.id,
            'default_origin': self.contract_number
        }
        if len(self.manufacturing_order_ids) == 1:
            action['views'] = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            action['res_id'] = self.manufacturing_order_ids.id
        return action
