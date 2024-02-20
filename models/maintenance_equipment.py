from odoo import models, fields, api
from odoo.odoo.exceptions import ValidationError


class CustomMaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    equipment_assign_to = fields.Selection(
        selection=[
            ('property', 'Property'),
            ('department', 'Department'),
            ('employee', 'Employee'),
            ('other', 'Other'),
            # ... add other values as needed
        ],
    )
    property_id = fields.Many2one(
        'real.estate',
        store=True,
        compute='_compute_equipment_assign',
        string='Property',
        readonly=False
    )

    buildingPart_id = fields.Many2one('building.part', string='Building Part', compute='_compute_equipment_assign',
                                      store=True, readonly=False)
    # complete_name = fields.Char(string="Complete Name", related='buildingPart_id.complete_name', store=True)

    product_category_type = fields.Selection([
        ('document', 'مکتوب'),
        ('inquiry', 'استعلام'),
        ('offer', 'پيشنهاد')
    ], required=True, default='document', string='Product Category Type')

    # Define a Many2many field to store attachments/files for each product
    attachments = fields.Many2many('ir.attachment',
                                   domain="[('res_model', '=', 'maintenance.equipment')]")

    order_office = fields.Char(string="Order Office")
    document_number = fields.Char(string="Document Number")
    date = fields.Date(string="Date", default=fields.Date.context_today)

    offer_number = fields.Char(string="Offer Number")
    offer_date = fields.Date(string="Offer Date")

    inquiry_number = fields.Char(string="Inquiry Number")
    card_number = fields.Char(string="Card Number")
    inquiry_details = fields.Text(string="Details")
    inquiry_date = fields.Date(string="Date")

    book_name = fields.Char(string="Book Name", store=True)
    book_year = fields.Char(string='Year', store=True)
    book_vol = fields.Char(string="Book Volume", store=True)
    book_page = fields.Char(string="Book Page", store=True)
    quantity = fields.Integer(string="Quantity", store=True)
    total_amount = fields.Integer(string="Total Amount", compute='calculate_total_amount', tracking=True)

    # compute total amount  based on cost and quantity
    @api.onchange('cost', 'quantity')
    def calculate_total_amount(self):
        for rec in self:
            if rec.cost:
                rec.total_amount = rec.cost * rec.quantity
            else:
                rec.total_amount = 0

    # reset field after selecting selection field
    @api.depends('equipment_assign_to')
    def _compute_equipment_assign(self):
        for equipment in self:
            if equipment.equipment_assign_to == 'employee':
                equipment.department_id = False
                equipment.property_id = False
                equipment.buildingPart_id = False
                equipment.employee_id = equipment.employee_id
            elif equipment.equipment_assign_to == 'department':
                equipment.employee_id = False
                equipment.property_id = False
                equipment.buildingPart_id = False
                equipment.department_id = equipment.department_id
            elif equipment.equipment_assign_to == 'property':
                equipment.employee_id = False
                equipment.department_id = False
                equipment.property_id = equipment.property_id
                equipment.buildingPart_id = equipment.buildingPart_id
            else:
                equipment.department_id = equipment.department_id
                equipment.employee_id = equipment.employee_id
