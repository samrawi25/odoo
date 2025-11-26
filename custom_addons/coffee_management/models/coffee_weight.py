# models/coffee_weight.py
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

# custom_addons/coffee_management/models/coffee_weight.py

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class CoffeeWeightHistory(models.Model):
    _name = 'coffee.weight.history'
    _description = 'Coffee Weight History'
    _rec_name = 'arrival_id'

    arrival_id = fields.Many2one(
        'coffee.arrival',
        string='Arrival Record',
        required=True,
        ondelete='cascade',
        help="Reference to the coffee arrival record"
    )

    ## THE FIX: Removed required=True to allow the record to be created first.
    ## The check will be moved to the confirmation button.
    num_of_bags = fields.Integer(
        string='Number of Bags',
        help="Total number of coffee bags received"
    )
    gross_weight = fields.Float(
        string='Gross Weight (KG)',
        help="Total weight including truck and coffee"
    )
    truck_weight = fields.Float(
        string='Truck Weight (KG)',
        help="Weight of the empty truck"
    )

    # These fields can remain as they are
    damage_percentage = fields.Float(string='Damage Percentage (%)', default=0.0)
    damage_bag_count = fields.Integer(string='Damage Bag Count', compute='_compute_damage_bag_count', store=True)
    net_weight = fields.Float(string='Net Weight (KG)', compute='_compute_weights', store=True)
    empty_jute_bag_weight = fields.Float(string='Empty Jute Bag Weight (KG)', default=0.0)
    moisture_loss_adjustment = fields.Float(string='Moisture Loss Adjustment (KG)', default=0.0)
    grand_net_weight = fields.Float(string='Grand Net Weight (KG)', compute='_compute_weights', store=True)
    coffee_tea_weight = fields.Float(string='Final Coffee Weight (KG)', compute='_compute_coffee_tea_weight',
                                     store=True)

    supplier_id = fields.Many2one(related='arrival_id.supplier_id', store=True, readonly=True)
    arrival_date = fields.Date(related='arrival_id.date', store=True, readonly=True)

    @api.depends('num_of_bags', 'damage_percentage')
    def _compute_damage_bag_count(self):
        for record in self:
            record.damage_bag_count = int(record.num_of_bags * (record.damage_percentage / 100.0))

    @api.depends('gross_weight', 'truck_weight', 'empty_jute_bag_weight', 'moisture_loss_adjustment')
    def _compute_weights(self):
        for record in self:
            net_weight = record.gross_weight - record.truck_weight
            if net_weight < 0:
                raise ValidationError(_("Net Weight cannot be negative. Please check Gross and Truck weights."))
            record.net_weight = net_weight
            record.grand_net_weight = record.net_weight - record.moisture_loss_adjustment - record.empty_jute_bag_weight

    @api.depends('grand_net_weight')
    def _compute_coffee_tea_weight(self):
        for record in self:
            record.coffee_tea_weight = record.grand_net_weight

    def action_confirm_weight(self):
        self.ensure_one()

        ## THE FIX: Added validation here to enforce the mandatory fields before confirming.
        if self.num_of_bags <= 0:
            raise UserError(_("You must enter a 'Number of Bags' greater than zero before confirming."))
        if self.gross_weight <= 0:
            raise UserError(_("You must enter a 'Gross Weight' greater than zero before confirming."))

        # Update the parent arrival record's state
        if self.arrival_id.state == 'quality_evaluated':
            self.arrival_id.write({'state': 'weight_recorded'})

        # Log the history
        self.env['coffee.weight.history.log'].create({
            'weight_history_id': self.id,
            'gross_weight': self.gross_weight,
            'truck_weight': self.truck_weight,
            'net_weight': self.net_weight,
            'num_of_bags': self.num_of_bags,
            'damage_percentage': self.damage_percentage,
            'user_id': self.env.user.id,
            'timestamp': fields.Datetime.now(),
        })

        # Close the wizard and refresh the parent view
        return {'type': 'ir.actions.act_window_close'}

    @api.model_create_multi
    def create(self, vals_list):
        # Call the original create method to create the weight history records
        records = super().create(vals_list)

        # Iterate over the newly created records and update the arrival state
        for record in records:
            if record.arrival_id:
                # Check the current state to prevent overwriting 'done' or 'ug_grade'
                if record.arrival_id.state not in ('done', 'ug_grade'):
                    record.arrival_id.state = 'weight_recorded'
                    _logger.info("Arrival %s state updated to 'weight_recorded' after creation of weight record.",
                                 record.arrival_id.coffee_issue_no)
        return records