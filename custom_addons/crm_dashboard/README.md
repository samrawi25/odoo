# CRM Dashboard Module

## Installation
1. Copy the `crm_dashboard` folder to your Odoo custom addons directory
2. Update your addons path in Odoo configuration
3. Restart the Odoo server
4. Go to Apps → Update Apps List
5. Search for "CRM Dashboard" and install the module

## Usage
After installation:
1. Open any CRM lead/opportunity
2. The dashboard will appear below the main form
3. All sections are automatically populated with relevant data

## Testing
To verify the dashboard is working:
1. Create or open a CRM lead
2. Check that all dashboard sections are visible
3. Verify data is displayed correctly in each section
4. Test any interactive elements

## Customization
To modify the dashboard:
1. Edit the views in `views/crm_dashboard_views.xml`
2. Add custom widgets in `static/src/js/`
3. Extend models in `models/` as needed

## Support
For assistance, contact your Odoo administrator or developer.
