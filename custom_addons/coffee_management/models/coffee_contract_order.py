from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CoffeeContractOrder(models.Model):
    _name = 'coffee.contract.order'
    _description = 'Coffee Contract Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(string='Contract Number', required=True, readonly=True, copy=False, default=lambda self: 'New')
    # customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        compute='_compute_customer_from_contract',
        store=True,  # Store the value for search/reporting efficiency
        readonly=False,  # Allow manual override if contract_ref_id is empty
    )
    producer_exporter = fields.Many2one('res.company', string='Producer & Exporter',
                                        default=lambda self: self.env.company)

    # 💡 NEW LINE FIELD (Replaces single product_id, quantity, uom_id)
    order_line_ids = fields.One2many(
        'coffee.contract.order.line',
        'order_id',
        string='Order Lines',
        copy=True
    )

    # MO-related fields
    manufacturing_order_ids = fields.One2many('mrp.production', 'coffee_contract_order_id',
                                              string='Manufacturing Orders')
    manufacturing_count = fields.Integer(string='Manufacturing Orders', compute='_compute_manufacturing_count')

    # Contract Link (Source)
    contract_ref_id = fields.Many2one(
        'coffee.contract', string='Source Contract', ondelete='restrict',
        help="The main sales contract this order is detailing production for."
    )
    manufacturing_route_id = fields.Many2one(
        'stock.route', string='Manufacturing Route', domain="[('product_selectable', '=', True)]"
    )

    # Product Details (kept for compatibility with original view, but functionally replaced by lines)
    product_id = fields.Many2one(related='order_line_ids.product_id', string='Coffee Product (Ref)')
    quantity = fields.Float(related='order_line_ids.quantity', string='Product Quantity (Ref)')
    uom_id = fields.Many2one(related='order_line_ids.uom_id', string='Unit of Measure (Ref)')

    # Packaging and Dates
    shipment_date = fields.Date(string='Shipment Date')
    packing = fields.Selection([('bags', 'Jute Bags'), ('bulk', 'Bulk'), ], string='Packing')
    bag_publication_order_no = fields.Char(string='Bag Marking Order No.')
    bag_publication_order_date = fields.Date(string='Bag Marking Order Date')
    sticker_required = fields.Boolean(string='Sticker Required')

    # Certification & Compliance
    green_pro_order = fields.Selection([('yes', 'Yes'), ('no', 'No'), ], string='Green Pro Order', default='yes')
    certified_product = fields.Boolean(string='Certified Product')
    certificate_type = fields.Selection([
        ('fair_trade', 'Fair Trade'), ('organic', 'Organic'), ('rainforest_alliance', 'Rainforest Alliance'),
    ], string='Certificate Type')
    # coffee_grown_area = fields.Char(string='Coffee Grown Area')

    coffee_grown_area = fields.Char(
        string='Coffee Grown Area',
        compute='_compute_coffee_grown_area',
        store=True,  # Store the value for search/reporting efficiency
        readonly=False,  # Allow manual override if computed value is wrong or needs refinement
    )

    farmers_names = fields.Text(string='Farmers’ Name(s)')
    eudr_compliant = fields.Boolean(string='EUDR Compliant')
    ico_certificate_number = fields.Char(string='ICO & Certificate Number')
    production_urgency = fields.Selection([('regular', 'Regular'), ('urgent', 'Urgent'), ], string='Production Urgency',
                                          default='regular')

    # Workflow States
    state = fields.Selection([('draft', 'Draft'), ('checked', 'Checked'), ('approved', 'Approved'), ],
                             string='Status', default='draft', tracking=True)

    # 💡 NEW COMPUTED METHOD
    @api.depends('contract_ref_id')
    def _compute_customer_from_contract(self):
        for order in self:
            # Inherit the buyer_id from the linked contract
            if order.contract_ref_id and order.contract_ref_id.buyer_id:
                order.customer_id = order.contract_ref_id.buyer_id
            # If the contract link is removed, keep the existing value or clear it
            elif not order.contract_ref_id and not order._origin.contract_ref_id:
                # Only clear if it was a new record or if it was manually cleared
                # If you want to keep the old customer when the contract is unlinked,
                # you can skip this 'else' block entirely.
                order.customer_id = False

    # Sequence Number Generation
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('coffee.contract.order') or 'New'
        return super(CoffeeContractOrder, self).create(vals)

    # 💡 ONCHANGE TO INHERIT CONTRACT LINES
    @api.onchange('contract_ref_id')
    def _onchange_contract_ref_id(self):
        # Existing line creation logic...
        if not self.contract_ref_id:
            self.order_line_ids = [(5, 0, 0)]
            self.customer_id = False  # Explicitly clear customer on unlinking contract
            return

        # Explicitly call the computation to ensure the customer field updates immediately in the UI
        self._compute_customer_from_contract()

        new_lines = []
        for line in self.contract_ref_id.contract_line_ids:
            new_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity_kg,
                'uom_id': line.product_id.uom_id.id,
                'contract_line_id': line.id,
            }))

        self.order_line_ids = new_lines

    # --- MO Logic ---
    @api.depends('manufacturing_order_ids')
    def _compute_manufacturing_count(self):
        for order in self:
            order.manufacturing_count = len(order.manufacturing_order_ids)

    def _should_create_mo_for_product(self, product):
        bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('type', '=', 'normal'),
            ('active', '=', True)
        ], limit=1)
        return bool(bom)

    def _check_components_availability(self, bom, quantity):
        unavailable_components = []
        for line in bom.bom_line_ids:
            required_qty = line.product_qty * quantity / bom.product_qty
            available_qty = line.product_id.free_qty
            if available_qty < required_qty:
                unavailable_components.append({
                    'product': line.product_id.name,
                    'required': required_qty,
                    'available': available_qty,
                    'shortage': required_qty - available_qty
                })
        return unavailable_components

    def _create_manufacturing_order(self, warehouse, order_line):
        product = order_line.product_id
        bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('type', '=', 'normal'),
            ('active', '=', True)
        ], limit=1)

        if not bom:
            _logger.warning("No BOM found for product %s for contract order %s", product.name, self.name)
            return self.env['mrp.production']

        quantity_needed = order_line.quantity  # Assuming quantity is in KG
        unavailable = self._check_components_availability(bom, quantity_needed)

        mo_vals = {
            'product_id': product.id,
            'product_qty': quantity_needed,
            'product_uom_id': order_line.uom_id.id,
            'bom_id': bom.id,
            'origin': self.name,
            'coffee_contract_id': self.contract_ref_id.id if self.contract_ref_id else False,
            'coffee_contract_order_id': self.id,  # Link back to this order
            'picking_type_id': warehouse.manu_type_id.id,
            'location_src_id': warehouse.lot_stock_id.id,
            'location_dest_id': warehouse.lot_stock_id.id,
            'state': 'draft',
        }

        mo = self.env['mrp.production'].create(mo_vals)

        if unavailable:
            self._create_component_shortage_activity(unavailable, mo)
        else:
            mo.action_confirm()

        return mo

    def _create_component_shortage_activity(self, unavailable_components, mo):
        note = _("Component shortages for Manufacturing Order %s:\n\n") % mo.name
        for comp in unavailable_components:
            note += _("- %s: Required %.2f, Available %.2f, Shortage %.2f\n") % (
                comp['product'], comp['required'], comp['available'], comp['shortage']
            )

        self.activity_schedule(
            'mail.mail_activity_data_warning',
            note=note,
            user_id=self.env.user.id,
            summary=_("Component Shortage for MO")
        )

    # --- Button Methods for State Changes ---
    def action_check(self):
        self.ensure_one()
        self.write({'state': 'checked'})

    def action_approve(self):
        self.ensure_one()
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        if not warehouse:
            raise UserError(_("No warehouse is configured for this company."))

        # Create MO for EACH line
        for line in self.order_line_ids:
            if self._should_create_mo_for_product(line.product_id):
                self._create_manufacturing_order(warehouse, line)

        self.write({'state': 'approved'})

    def action_view_manufacturing_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('mrp.mrp_production_action')
        action['domain'] = [('id', 'in', self.manufacturing_order_ids.ids)]
        action['context'] = {
            'create': False,
            'default_coffee_contract_order_id': self.id,
            'default_origin': self.name
        }
        if len(self.manufacturing_order_ids) == 1:
            action['views'] = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            action['res_id'] = self.manufacturing_order_ids.id
        return action

        # 💡 NEW COMPUTED METHOD

    @api.depends('order_line_ids.product_id')
    def _compute_coffee_grown_area(self):
        for order in self:
            # We look only at the product of the first order line
            first_line_product = order.order_line_ids and order.order_line_ids[0].product_id

            if first_line_product:
                # Example: 'Processed_Jima_Washed_G2_Coffee'
                product_name = first_line_product.name

                # Split the name by the underscore '_'
                parts = product_name.split('_')

                # Check if there are at least 3 parts (i.e., at least two underscores)
                # If so, the required area is the second element (index 1)
                if len(parts) > 2:
                    order.coffee_grown_area = parts[1]  # 'Jima'
                else:
                    # Clear if the naming convention is not followed
                    order.coffee_grown_area = False
            else:
                order.coffee_grown_area = False
