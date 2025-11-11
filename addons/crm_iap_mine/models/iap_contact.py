def _iap_contact_mining(self, params, timeout=300):
    endpoint = self.env['ir.config_parameter'].sudo().get_param('reveal.endpoint', DEFAULT_ENDPOINT)
    # The original code appends another path, which leads to the error.
    # To use a custom local endpoint, you should define it here directly.
    # Change the endpoint to what you want.
    # For example, if your new endpoint is just 'http://localhost:8069/my_custom_service',
    # you can hardcode it here or get it from a configuration parameter.
    
    # Example of a fix:
    # Remove the second part of the URL from the original code
    # endpoint = self.env['ir.config_parameter'].sudo().get_param('reveal.endpoint', DEFAULT_ENDPOINT) + '/iap/clearbit/2/lead_mining_request'
    
    # A potential fix could be:
    # endpoint = 'http://localhost:8069/iap/clearbit/2/lead_mining_request' # Or your desired custom path

    # For your specific error, the issue is that it's appending to an already full path.
    # The fix is to use a corrected full path.
    endpoint = self.env['ir.config_parameter'].sudo().get_param('reveal.endpoint', 'http://localhost:8069') + '/iap/clearbit/2/lead_mining_request'
    
    return iap_tools.iap_jsonrpc(endpoint, params=params, timeout=timeout)