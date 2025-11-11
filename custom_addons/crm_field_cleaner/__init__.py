import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Simple debug hook"""
    _logger.info("=== CRM Field Cleaner: Hook STARTED ===")

    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Count CRM views
    crm_views = env['ir.ui.view'].search([('model', '=', 'crm.lead')])
    _logger.info("Found %d CRM lead views", len(crm_views))

    # Test field removal
    test_views = env['ir.ui.view'].search([('arch_db', 'ilike', 'probability')], limit=1)
    _logger.info("Found %d views with probability", len(test_views))

    _logger.info("=== CRM Field Cleaner: Hook COMPLETED ===")