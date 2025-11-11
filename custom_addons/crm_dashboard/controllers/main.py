from odoo import http
from odoo.http import request

class CrmDashboardController(http.Controller):
    
    @http.route('/crm_dashboard/get_data', type='json', auth='user')
    def get_dashboard_data(self, lead_id):
        """Example endpoint for dashboard data"""
        lead = request.env['crm.lead'].browse(lead_id)
        return {
            'call_count': lead.call_count,
            'visit_count': lead.visit_count,
            'last_interaction': lead.last_interaction
        }

    # Add more endpoints as needed for dashboard functionality
