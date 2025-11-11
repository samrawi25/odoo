# models/crm_lead_extension.py

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

class LeadExtension(models.Model):
    _inherit = 'crm.lead'

    # ... (your other fields like company_type and tin_number remain the same) ...
    company_type = fields.Selection([
        ('manufacturing', 'Manufacturing'),
        ('service', 'Service'),
        ('retail', 'Retail'),
        ('agriculture', 'Agriculture'),
        ('construction', 'Construction'),
        ('other', 'Other'),
    ], string="Industry / Company Type")
    tin_number = fields.Char(string="TIN Number")


    # --- THIS IS THE CORRECTED METHOD ---
    @api.constrains('phone', 'mobile')
    def _check_phone_number(self):
        """ 
        Validates phone and mobile numbers for Ethiopian format, 
        including both existing carriers (09...) and Safaricom (07...).
        """
        for lead in self:
            # This regex now accepts a 9 OR a 7 as the first digit.
            # The pattern is: optional country code, then 0, then 9 or 7, then 8 digits.
            phone_pattern = re.compile(r'^(?:\+251|251|0)?(9|7)\d{8}$')
            
            # A more flexible pattern that allows for optional spaces or hyphens:
            # phone_pattern_flexible = re.compile(r'^(?:\+251|251|0)?(9|7)[ -]?\d{2}[ -]?\d{3}[ -]?\d{3}$')
            
            if lead.phone:
                # Clean the number of spaces and hyphens before testing
                cleaned_phone = lead.phone.replace(' ', '').replace('-', '')
                if not phone_pattern.match(cleaned_phone):
                    raise ValidationError(_(
                        "Invalid Phone Number format for '%s'. Please use a valid Ethiopian format (e.g., 09... or 07...)."
                    ) % lead.phone)
            
            if lead.mobile:
                # Clean the number of spaces and hyphens before testing
                cleaned_mobile = lead.mobile.replace(' ', '').replace('-', '')
                if not phone_pattern.match(cleaned_mobile):
                    raise ValidationError(_(
                        "Invalid Mobile Number format for '%s'. Please use a valid Ethiopian format (e.g., 09... or 07...)."
                    ) % lead.mobile)
    # --- END OF CORRECTION ---


    @api.constrains('email_from')
    def _check_email_format(self):
        """ A simple email validation. """
        for lead in self:
            if lead.email_from and '@' not in lead.email_from:
                raise ValidationError(_("'%s' is not a valid email address.") % lead.email_from)