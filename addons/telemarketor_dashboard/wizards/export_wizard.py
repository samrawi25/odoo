# /crm_telemarketing/wizards/export_wizard.py
from odoo import models, fields, api, _
import csv
import io
from odoo.exceptions import UserError
import base64
from datetime import datetime

try:
    import xlsxwriter
    HAS_XLSX = True
except Exception:
    HAS_XLSX = False


class CrmExportWizard(models.TransientModel):
    _name = "crm.tele_export_wizard"
    _description = "Export Leads / Opportunities / Customers to XLSX or CSV"

    model = fields.Selection([('crm.lead', 'Leads'), ('crm.tele_opportunity', 'Opportunities'), ('res.partner', 'Customers')], string="Model", required=True)
    filename = fields.Char("Filename", default="export")
    file = fields.Binary("File", readonly=True)
    file_name = fields.Char("File Name", readonly=True)
    format = fields.Selection([('xlsx', 'XLSX'), ('csv', 'CSV')], string="Format", default='xlsx')

    def action_export(self):
        model = self.env[self.model]
        active_ids = self.env.context.get('active_ids') or []
        if active_ids:
            records = model.browse(active_ids)
        else:
            records = model.search([])

        if not records:
            raise UserError("No records found to export.")

        # set filename
        base_name = (self.filename or 'export').replace(' ', '_')
        if self.format == 'xlsx' and HAS_XLSX:
            # create xlsx in-memory
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Export')

            # write headers and rows depending on model
            if self.model == 'crm.lead':
                headers = ["id", "name", "company_name", "full_name", "phone_number", "email_from", "assigned_user"]
                for col, h in enumerate(headers):
                    worksheet.write(0, col, h)
                for row_idx, r in enumerate(records, start=1):
                    worksheet.write(row_idx, 0, r.id)
                    worksheet.write(row_idx, 1, r.name or '')
                    worksheet.write(row_idx, 2, r.company_name or '')
                    worksheet.write(row_idx, 3, r.full_name or '')
                    worksheet.write(row_idx, 4, r.phone_number or '')
                    worksheet.write(row_idx, 5, r.email_from or '')
                    worksheet.write(row_idx, 6, r.assigned_user_id.name or '')
            elif self.model == 'crm.tele_opportunity':
                headers = ["id", "name", "lead", "partner", "owner", "expected_total_sales_value", "state"]
                for col, h in enumerate(headers):
                    worksheet.write(0, col, h)
                for row_idx, r in enumerate(records, start=1):
                    worksheet.write(row_idx, 0, r.id)
                    worksheet.write(row_idx, 1, r.name or '')
                    worksheet.write(row_idx, 2, r.lead_id.name or '')
                    worksheet.write(row_idx, 3, r.partner_id.name or '')
                    worksheet.write(row_idx, 4, r.owner_id.name or '')
                    worksheet.write(row_idx, 5, r.expected_total_sales_value or 0)
                    worksheet.write(row_idx, 6, r.state or '')
            elif self.model == 'res.partner':
                headers = ["id", "name", "tin_number", "company_type_custom", "latitude", "longitude", "email"]
                for col, h in enumerate(headers):
                    worksheet.write(0, col, h)
                for row_idx, r in enumerate(records, start=1):
                    worksheet.write(row_idx, 0, r.id)
                    worksheet.write(row_idx, 1, r.name or '')
                    worksheet.write(row_idx, 2, r.tin_number or '')
                    worksheet.write(row_idx, 3, r.company_type_custom or '')
                    worksheet.write(row_idx, 4, r.latitude or '')
                    worksheet.write(row_idx, 5, r.longitude or '')
                    worksheet.write(row_idx, 6, r.email or '')

            workbook.close()
            output.seek(0)
            data = output.read()
            b64 = base64.b64encode(data)
            fname = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self.file = b64
            self.file_name = fname
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'crm.tele_export_wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
            }
        else:
            # fallback to CSV (browser download)
            out = io.StringIO()
            writer = csv.writer(out)
            if self.model == "crm.lead":
                header = ["id", "name", "company_name", "full_name", "phone_number", "email_from", "assigned_user_id"]
                writer.writerow(header)
                for r in records:
                    writer.writerow([r.id, r.name, r.company_name, r.full_name, r.phone_number, r.email_from, r.assigned_user_id.name or ""])
            elif self.model == "crm.tele_opportunity":
                header = ["id", "name", "lead_id", "partner_id", "owner_id", "expected_total_sales_value", "state"]
                writer.writerow(header)
                for r in records:
                    writer.writerow([r.id, r.name, r.lead_id.name or "", r.partner_id.name or "", r.owner_id.name or "", r.expected_total_sales_value, r.state])
            elif self.model == "res.partner":
                header = ["id", "name", "tin_number", "company_type_custom", "latitude", "longitude", "email"]
                writer.writerow(header)
                for r in records:
                    writer.writerow([r.id, r.name, r.tin_number, r.company_type_custom, r.latitude, r.longitude, r.email])

            out.seek(0)
            data = out.read().encode('utf-8')
            return {
                'type': 'ir.actions.act_url',
                'url': 'data:text/csv;charset=utf-8,' + data.decode('utf-8'),
                'target': 'new',
            }
