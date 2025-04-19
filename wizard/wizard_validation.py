from odoo import api, fields, models, _
import csv
import io
import base64
from odoo.exceptions import ValidationError


class WizardValidationEstate(models.TransientModel):
    _name = 'wizard.validation.estate'
    _description = 'Property Validation'

    start_date = fields.Date(string="From: ", required=1)
    end_date = fields.Date(string="To: ", required=True, default=fields.Date.context_today)
    property_buyer = fields.Many2one('res.partner', string="Buyer Name")
    total_property = fields.Integer(string="Total Property", readonly=True)
    total_amount = fields.Float(string="Total Property Amount", readonly=True)
    download_format = fields.Selection([('csv', 'CSV')], string='Download Format', default='csv')

    def action_validate_property(self):
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]

        count = self.env['real.estate'].search(domain)
        total = count.mapped('selling_price')
        total_amount = sum(total)
        total_property = len(total)
        self.write({'total_property': total_property, 'total_amount': total_amount})
        return {
            'name': _('Total Property Created Within Given Date'),
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'res_model': 'wizard.validation.estate',
            'target': 'new',
            'effect': {
                'fadeout': 'medium',
                'message': f"{total_property} Property Record Fetched Successfully!!! ",
                'type': 'rainbow_man',
            }
        }

    def action_cancel(self):
        return {
            'effect': {
                'fadeout': 'fast',
                'message': "Closed!!! \n Successfully Closed Wizard 😡",
                'type': 'rainbow_man',
            }
        }

    @api.constrains('end_date')
    def check_end_date(self):
        today = fields.Date.today()
        if self.end_date > today:
            raise ValidationError(_("Input Error in End Date Field \n You can Choose end Date Till Today"))

    # CSV DATA FORMAT
    def generate_csv_data(self, records):
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        header = ['Property Name', 'Price', 'Status', 'Date', 'Floors', 'Bedrooms',
                  'living_area', 'Garden', 'Garden Area', 'Orientation', 'Garage', 'Total Areas (Sqm)']
        csv_writer.writerow(header)

        for record in records:
            data_row = [record.name, record.selling_price, record.state, record.date_availability,
                        record.floors, record.bedrooms, record.living_area,
                        record.garden, record.garden_area, record.garden_orientation,
                        record.garage, record.total_area]
            csv_writer.writerow(data_row)

        return csv_data.getvalue().encode('utf-8')

    def action_download_data(self):
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]
        records = self.env['real.estate'].search(domain)

        if self.download_format == 'csv':
            data = self.generate_csv_data(records)
            file_name = 'mcit_egp_property_records.csv'
            content_type = 'text/csv'
        else:
            raise ValidationError('Invalid download format please select CSV')

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(data),
            'res_model': 'real.estate.download.wizard',
            'res_id': self.id,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
            'effect': {
                'fadeout': 'medium',
                'message': f"Your CSV file has been downloaded successfully!",
                'type': 'rainbow_man',
            }
        }

    # action to print searched property report
    def action_print_report(self):
        domain = [
            ('create_date', '>=', self.start_date),
            ('create_date', '<=', self.end_date)
        ]
        if self.property_buyer:
            domain.append(('buyer_id', '=', self.property_buyer.id))
        return self.env.ref('egp_property.action_property_report_pdf').report_action(self, data={'domain': domain})


class PropertyReportAbstract(models.AbstractModel):
    _name = "report.egp_property.report_action_property_template"
    _description = "property Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = data.get('domain', [])
        docs = self.env['real.estate'].search(domain, limit=100)
        return {
            "docs": docs
        }


# For Download Filtered Record In Transient model > real_estate module
"""
    def action_download_data(self):
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]
        records = self.env['real.estate'].search(domain)
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        header = ['Property Name', 'Price', 'Status']  # Replace with your actual field names
        csv_writer.writerow(header)

        for record in records:
            data_row = [record.name, record.selling_price, record.state]
            csv_writer.writerow(data_row)
        data_file = csv_data.getvalue().encode('utf-8')
        file_name = 'mcit_egp_property_records.csv'
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(data_file),
            'res_model': 'real.estate.download.wizard',
            'res_id': self.id,
        })

        # Return an action to download the file
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
"""
