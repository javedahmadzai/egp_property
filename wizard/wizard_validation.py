from odoo import api, fields, models, _
import csv
import io
import os
import base64
from odoo.exceptions import ValidationError

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


class WizardValidationEstate(models.TransientModel):
    _name = 'wizard.validation.estate'
    _description = 'Property Validation'

    start_date = fields.Date(string="From: ", required=1)
    end_date = fields.Date(string="To: ", required=True, default=fields.Date.context_today)
    property_buyer = fields.Many2one('res.partner', string="Buyer Name")
    total_property = fields.Integer(string="Total Property", readonly=True)
    total_amount = fields.Float(string="Total Property Amount", readonly=True)
    download_format = fields.Selection([('csv', 'CSV'), ('pdf', 'PDF')], string='Download Format', default='csv')

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
        header = ['Property Name', 'Price', 'Status', 'Floors', 'Bedrooms',
                  'living_area', 'Garden', 'Garden Area', 'Orientation', 'Garage', 'Total Areas (Sqm)']
        csv_writer.writerow(header)

        for record in records:
            data_row = [record.name, record.selling_price, record.state, record.date_availability,
                        record.floors, record.bedrooms, record.living_area,
                        record.garden, record.garden_area, record.garden_orientation,
                        record.garage, record.total_area]
            csv_writer.writerow(data_row)

        return csv_data.getvalue().encode('utf-8')

    # PDF DATA FORMAT
    def generate_pdf_data(self, records):
        pdf_data = io.BytesIO()
        doc = SimpleDocTemplate(pdf_data, pagesize=letter)

        # Define table headers and data
        table_data = [['Property Name', 'Price', 'Status', 'Total Areas', 'Floors',
                       'Bedrooms', 'Garden Area', 'Orientation', 'Garage']]

        for record in records:
            data_row = [record.name,
                        record.selling_price,
                        record.state,
                        record.total_area,
                        record.floors,
                        record.bedrooms,
                        record.garden_area,
                        record.garden_orientation,
                        record.garage]
            table_data.append(data_row)

        # Register an Arabic font
        # pdfmetrics.registerFont(TTFont('Arabic',
        #                                'E:\\OdooDevelopment\\odoo-16.0\\custom_addons\\egp_property\\static\\src\\fonts\\tt-cufonfonts\\TTReg.ttf'))

        # Create the table and set style with Arabic font
        table = Table(table_data)
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                         #   ('FONTNAME', (0, 0), (-1, 0), 'Arabic'),  # Use Arabic font
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(style)

        # Build the PDF document with the table
        doc.build([table])
        pdf_data.seek(0)

        return pdf_data.getvalue()

    def action_download_data(self):
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]
        records = self.env['real.estate'].search(domain)

        if self.download_format == 'csv':
            data = self.generate_csv_data(records)
            file_name = 'mcit_egp_property_records.csv'
            content_type = 'text/csv'
        elif self.download_format == 'pdf':
            data = self.generate_pdf_data(records)
            file_name = 'mcit_egp_property_records.pdf'
            content_type = 'application/pdf'
        else:
            raise ValueError('Invalid download format')

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
                'message': f" Your {self.download_format} File Downloaded Successfully!",
                'type': 'rainbow_man',
            }
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
