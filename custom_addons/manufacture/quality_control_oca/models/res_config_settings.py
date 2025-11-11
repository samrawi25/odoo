# quality_control_oca/models/res_config_settings.py
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # This field will be our new checkbox in the settings.
    # The implied_group makes Odoo automatically manage adding/removing users
    # from the group when the checkbox is ticked/unticked.
    group_quality_control_oca_mrp_integration = fields.Boolean(
        "OCA Quality Integration",
        implied_group='quality_control_oca.group_quality_control_oca_mrp_integration'
    )
