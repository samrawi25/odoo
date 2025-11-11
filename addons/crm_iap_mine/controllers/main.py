import json
from odoo import http
from odoo.http import request

class IapClearbitController(http.Controller):

    @http.route('/iap/clearbit/2/lead_mining_request', type='json', auth='none', methods=['POST'], csrf=False)
    def lead_mining_request(self, **kwargs):
        # Your custom logic to handle the lead mining request
        # You can simulate the response of the external service here.
        
        # Example of a dummy response
        response_data = {
            'data': [
                {
                    'company_data': {
                        'name': 'AMG Holdings',
                        'email': 'info@amgholdings.com',
                        'website': 'www.amgholdings.com',
                        'website': 'www.customcorp.com',
                        'reveal_id': 'unique_id_123',
                        'location': 'Addis Ababa, Ethiopia',
                        'size': 1000000,
                        'industry': 'Multi-company',
                    },
                    'people_data': [],
                },
            ],
            'status': 'success',
        }
        
        return json.dumps(response_data)