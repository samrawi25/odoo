from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CoffeeContractOrder(models.Model):
    _name = 'coffee.contract.order'
    _description = 'Coffee Contract Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # --- Basic Information ---
    name = fields.Char(string='Order Number', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer', related='contract_ref_id.buyer_id', store=True,
                                  readonly=True)
    producer_exporter = fields.Many2one('res.company', string='Producer & Exporter',
                                        default=lambda self: self.env.company)

    # --- Order Lines ---
    order_line_ids = fields.One2many('coffee.contract.order.line', 'order_id', string='Order Lines', copy=True,
                                     readonly=True, states={'draft': [('readonly', False)]})

    # --- Document Links & Smart Buttons ---
    contract_ref_id = fields.Many2one(
        'coffee.contract', string='Source Contract', ondelete='restrict', required=True,
        tracking=True, readonly=True, states={'draft': [('readonly', False)]},
        domain="[('state', '=', 'confirmed')]"
    )
    manufacturing_order_ids = fields.One2many('mrp.production', 'coffee_contract_order_id',
                                              string='Manufacturing Orders')
    manufacturing_count = fields.Integer(string='Manufacturing Orders Count', compute='_compute_manufacturing_count')

    picking_ids = fields.One2many('stock.picking', compute='_compute_picking_ids', string="Shipments")
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')

    # --- Packaging and Dates ---
    shipment_date = fields.Date(string='Shipment Date', tracking=True)
    packing = fields.Selection([('bags', 'Jute Bags'), ('bulk', 'Bulk')], string='Packing')
    bag_publication_order_no = fields.Char(string='Bag Marking Order No.')
    bag_publication_order_date = fields.Date(string='Bag Marking Order Date')
    sticker_required = fields.Boolean(string='Sticker Required')

    # --- Certification & Compliance ---
    green_pro_order = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Green Pro Order', default='yes')
    certified_product = fields.Boolean(string='Certified Product')
    certificate_type = fields.Selection([
        ('fair_trade', 'Fair Trade'), ('organic', 'Organic'), ('rainforest_alliance', 'Rainforest Alliance'),
    ], string='Certificate Type')
    coffee_grown_area = fields.Char(string='Coffee Grown Area', compute='_compute_coffee_grown_area', store=True,
                                    readonly=False)
    farmers_names = fields.Text(string='Farmers Name(s)')
    eudr_compliant = fields.Boolean(string='EUDR Compliant')
    ico_certificate_number = fields.Char(string='ICO & Certificate Number')
    production_urgency = fields.Selection([('regular', 'Regular'), ('urgent', 'Urgent')], string='Production Urgency',
                                          default='regular')

    # --- Workflow State ---
    state = fields.Selection([
        ('draft', 'Draft'),
        ('checked', 'Checked'),
        ('approved', 'Approved'),
        ('production_done', 'Production Done'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False, compute='_compute_state', store=True, readonly=True)

    # --- Sequence Generation ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('coffee.contract.order') or _('New')
        return super().create(vals_list)

    # --- Onchange Method (FIXED: Now correctly copies the FINISHED product from contract) ---
    @api.onchange('contract_ref_id')
    def _onchange_contract_ref_id(self):
        """When a Source Contract is selected, automatically populate the order lines."""
        if self.contract_ref_id:
            self.order_line_ids = [(5, 0, 0)]
            lines_to_create = []
            for line in self.contract_ref_id.contract_line_ids:
                # Ensure we are linking to the correct product variant if the contract uses a template
                product_variant = self.env['product.product'].search([('product_tmpl_id', '=', line.product_id.id)],
                                                                     limit=1)
                if not product_variant:
                    # Fallback to the first variant if search fails
                    product_variant = line.product_id.product_variant_id

                lines_to_create.append((0, 0, {
                    'product_id': product_variant.id,
                    'quantity': line.quantity_kg,
                    'uom_id': self.env.ref('uom.product_uom_kgm').id,
                    'contract_line_id': line.id,
                }))
            self.order_line_ids = lines_to_create
        else:
            self.order_line_ids = [(5, 0, 0)]

    # --- Compute Methods ---
    @api.depends('manufacturing_order_ids')
    def _compute_manufacturing_count(self):
        for order in self:
            order.manufacturing_count = len(order.manufacturing_order_ids)

    @api.depends('manufacturing_order_ids.move_finished_ids.move_dest_ids.picking_id')
    def _compute_picking_ids(self):
        for order in self:
            finished_moves = order.manufacturing_order_ids.move_finished_ids
            pickings = finished_moves.move_dest_ids.picking_id
            order.picking_ids = pickings
            order.delivery_count = len(pickings)

    @api.depends('manufacturing_order_ids.state', 'picking_ids.state')
    def _compute_state(self):
        for order in self:
            if order.state in ('cancelled', 'shipped'):
                continue
            if not order.manufacturing_order_ids:
                if order.state not in ('draft', 'checked'):
                    order.state = 'approved'
                continue
            mo_states = set(order.manufacturing_order_ids.mapped('state'))
            if all(s == 'done' for s in mo_states):
                picking_states = set(order.picking_ids.mapped('state'))
                if picking_states and all(s == 'done' for s in picking_states):
                    order.state = 'shipped'
                else:
                    order.state = 'production_done'
            elif any(s in ('progress', 'to_close') for s in mo_states):
                order.state = 'in_production'

    @api.depends('order_line_ids.product_id')
    def _compute_coffee_grown_area(self):
        for order in self:
            first_product = order.order_line_ids[:1].product_id
            if first_product and first_product.name:
                parts = first_product.name.split('_')
                order.coffee_grown_area = parts[1] if len(parts) > 2 else False
            else:
                order.coffee_grown_area = False

    # --- Button Actions ---
    def action_check(self):
        self.ensure_one()
        self.write({'state': 'checked'})

    def action_approve(self):
        """Move to approved state and create manufacturing orders."""
        self.ensure_one()

        if self.state != 'checked':
            raise UserError(_("Only checked orders can be approved."))

        if not self.order_line_ids:
            raise UserError(_("Cannot approve an order with no product lines."))

        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        if not warehouse:
            raise UserError(_("No default warehouse is configured for your company."))

        created_mos = self.env['mrp.production']
        failed_products_log = []

        for line in self.order_line_ids:
            # --- THE FIX: Use the standard, robust BOM lookup method ---
            # It returns a dictionary, so we get the value for our specific product.
            bom = self.env['mrp.bom']._bom_find(line.product_id, company_id=self.env.company.id, bom_type='normal').get(
                line.product_id)

            if not bom:
                failed_products_log.append(
                    f"- {line.product_id.display_name}: {_('No valid Bill of Materials found.')}"
                )
                _logger.warning("No BOM found for finished product %s", line.product_id.display_name)
                continue

            mo = self.env['mrp.production'].create({
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'product_uom_id': line.uom_id.id,
                'bom_id': bom.id,
                'origin': self.name,
                'coffee_contract_order_id': self.id,
                'coffee_contract_id': self.contract_ref_id.id,
            })
            created_mos |= mo

        if failed_products_log:
            # If any MO creations failed, raise an error with all the details.
            error_message = _("Failed to create all manufacturing orders:\n\n") + "\n".join(failed_products_log)
            raise UserError(error_message)

        if created_mos:
            created_mos.action_confirm()
            created_mos.action_assign()
            self.message_post(body=_("Created %d Manufacturing Order(s): %s") % (len(created_mos),
                                                                                 ', '.join(created_mos.mapped('name'))))

        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        mos_to_cancel = self.manufacturing_order_ids.filtered(lambda mo: mo.state not in ('done', 'cancel'))
        if mos_to_cancel:
            mos_to_cancel.action_cancel()

    def action_reset_to_draft(self):
        if any(mo.state not in ('draft', 'cancel') for mo in self.manufacturing_order_ids):
            raise UserError(_("Cannot reset to draft because manufacturing has already started."))
        self.manufacturing_order_ids.unlink()
        self.write({'state': 'draft'})

    # --- View Actions ---
    def action_view_manufacturing_orders(self):
        self.ensure_one()
        return {
            'name': _('Manufacturing Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.manufacturing_order_ids.ids)],
            'context': {'create': False}
        }

    def action_view_delivery_orders(self):
        self.ensure_one()
        return {
            'name': _('Delivery Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.picking_ids.ids)],
            'context': {'create': False}
        }