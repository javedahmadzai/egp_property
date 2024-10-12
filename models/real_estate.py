# -*- coding: utf-8 -*-
import datetime
import random
import calendar
import re
from datetime import timedelta
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import os


class RealEstate(models.Model):
    _name = 'real.estate'
    _inherit = ['mail.thread', 'mail.activity.mixin', ]
    _description = 'Real Estate'
    _order = "state, id desc"
    _rec_name = "name"

    name = fields.Char(required=True, string="Title", tracking=True)
    property_type_id = fields.Many2one('estate.property.type', tracking=True, ondelete='restrict')
    # for many selections
    property_type = fields.Many2many('estate.property.type', tracking=True, ondelete='restrict')
    description = fields.Text(tracking=True)
    # postcode = fields.Char(tracking=True)
    # date_availability = fields.Date(default=lambda self: _default_date())
    date_availability = fields.Date(default=fields.Date.context_today)
    deed_number = fields.Text(string="Deed or title deed number")
    # add four sides fields
    north = fields.Char(string="North")
    east = fields.Char(string="East")
    west = fields.Char(string="West")
    south = fields.Char(string="South")

    building_type = fields.Selection([
        ('pokhta', 'Pokhta'),
        ('nema_pokhta', 'Nema Pokhta'),
        ('raw', 'Khama'),
        ('Concrete', 'Concrete')
    ], tracking=True, default='pokhta', string="Building Type")

    property_area_type = fields.Selection([
        ('ground', 'Ground'),
        ('building', 'Building'),
        ('fort', 'Fort Qala')
    ], tracking=True, default='building', string="Property Type")

    expected_price = fields.Float(tracking=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, tracking=True)
    bedrooms = fields.Integer(default=0, tracking=True)
    living_area = fields.Integer(string="Living Area(sqm)", tracking=True)
    # facades = fields.Integer(tracking=True)
    document_property = fields.Selection([
        ('legal_deed', 'قباله شرعي'),
        ('legar_protocol', 'پروتوکول شرعي'),
        ('legal_agreement', 'تفاهم نامه'),
        ('Official booklet', 'کتابچه رسمي')
    ], tracking=True, default='legal_deed', string="Document Property")
    property_location = fields.Text(string="Property location")
    # current_status = fields.Char(string="حالت فعلی")
    # current_status = fields.Selection([
    #     ('0', '------'),
    #     ('use', 'ّIn Use'),
    #     ('not_use', 'Excess')
    # ], required=True, default='0', string='Current Status')

    # for printing the display value in xml report
    # def get_current_status_label(self):
    #     label_mapping = {
    #         'use': 'In Use',
    #         'not_use': 'Excess'
    #     }
    #     return label_mapping.get(self.current_status, '')

    garage = fields.Boolean()
    garden = fields.Boolean()
    tag_ids = fields.Many2many('property.type.tag', tracking=True, ondelete='cascade')
    garden_area = fields.Integer(string="Garden Area(sqm)", tracking=True)
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
                                          tracking=True)
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Excess'),
        ('offer_accepted', 'In Use'),
        ('cancel', 'Cancelled')],
        string="Status", tracking=True, default='new', readonly=True)
    floors = fields.Char(string="Floors")
    grade_type_property = fields.Selection([
        ('first_grade', 'First Grade'),
        ('second_grade', 'Second Grade'),
        ('third_grade', 'Third Grade'),
    ])
    # Define a Many2many field to store attachments/files for each Property
    property_attachments = fields.Many2many('ir.attachment', string='Attachments',
                                            domain="[('res_model', '=', 'real.estate')]",
                                            help="Upload property photos and documents.")
    sales_person = fields.Many2one('res.users', string="Salesman", default=lambda self: self.env.user, tracking=True,
                                   ondelete='cascade')

    sale_buyer = fields.Many2one('res.partner', string="Buyer", tracking=True, ondelete='cascade')
    sale_buyer_email = fields.Char(string='Buyer Mail')
    total_area = fields.Integer(string="Total Area(sqm)", compute='_compute_total_area', tracking=True, readonly=True,
                                store=True)
    ''' contract info '''
    contract_ids = fields.One2many('pms.contract', 'property_id', ondelete='cascade', store=True)
    # convert total area into Gereb, Beswa, Beswasa
    gereb = fields.Float(string="Gereb", compute="_compute_area_values", store=True)
    beswa = fields.Float(string="Beswa", compute="_compute_area_values", store=True)
    beswasa = fields.Float(string="Beswasa", compute="_compute_area_values", store=True)
    remaining_meters = fields.Integer(string="Meters", compute="_compute_area_values", store=True)

    ''' building part info '''
    building_part_id = fields.One2many('building.part', 'property_id', ondelete='cascade')

    image = fields.Image(string="Upload Property Image")

    '''below field For smart button '''
    count_tags = fields.Integer(compute="_compute_count_tags")
    property_types = fields.Integer(compute="_compute_count_property_types")
    total_properties = fields.Integer(string="Total Properties")

    ''' add for payment section '''
    tenant_ids = fields.One2many('tenant.payment', 'property_id', string="Tenants")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        total = 0
        for rec in self:
            total = rec.living_area + rec.garden_area
        self.total_area = total

    @api.onchange('garden')
    def _onchange_garden(self):
        for rec in self:
            if rec.garden == 1:
                self.garden_area = 10
                self.garden_orientation = "north"
            if rec.garden == 0:
                self.garden_area = 0
                rec.garden_orientation = False

    def action_cancel(self):
        for rec in self:
            if self.state == 'offer_accepted':
                raise ValidationError(_("You can not Cancel a Property After property in Use!!"))
            else:
                self.state = 'cancel'
        return True

    def action_reset_new(self):
        for rec in self:
            if self.state != 'cancel':
                raise ValidationError(_("RESET is Possible only in Cancel State"))
            else:
                self.state = 'new'
        return True


    @api.constrains('living_area')
    def check_living_area(self):
        for rec in self:
            if rec.living_area <= 0:
                raise ValidationError(_("INVALID LIVING AREA ,\n The living area must be positive and greater than 0"))

    # @api.constrains('expected_price')
    # def check_expected_price(self):
    #     for rec in self:
    #         if rec.expected_price <= 0:
    #             raise ValidationError(_("WARNING....Expected Price Must be Positive Number!!🚫"))

    def unlink(self):
        for rec in self:
            if rec.state not in ['new', 'cancel']:
                raise ValidationError(_("WARNING....\n Deletion is possible only in New or Cancel State"))
            return super(RealEstate, self).unlink()

    @api.model
    def create(self, vals):
        if not vals.get('state'):
            vals['state'] = 'offer_received'
        return super(RealEstate, self).create(vals)

    @api.depends('tag_ids')
    def _compute_count_tags(self):
        # local = 0
        for rec in self:
            result = len(rec.tag_ids)
        self.count_tags = result

    @api.depends('property_type')
    def _compute_count_property_types(self):
        # local = 0
        for rec in self:
            result = len(rec.property_type)
        self.property_types = result

    def action_count_tags(self):
        return {
            'name': _('Tags'),
            'view_mode': 'list',
            'type': 'ir.actions.act_window',
            # 'domain': [('tag_ids', 'in', self.id)],
            'res_model': 'property.type.tag',
            'target': 'current',
        }

    # return into property type model
    def action_count_property_types(self):
        return {
            'name': _('Property Types'),
            'view_mode': 'list',
            'type': 'ir.actions.act_window',
            # 'domain': [],
            'res_model': 'estate.property.type',
            'target': 'current',
        }

    # convert total area into automatic gereb, beswa, beswasa and meters
    @api.depends('living_area')
    def _compute_area_values(self):
        for record in self:
            record.gereb = int(record.living_area // 2000.0)
            # Calculate the remaining area after gereb
            remaining_area = record.living_area % 2000.0
            record.beswa = int(remaining_area // 100)
            remaining_area %= 100
            record.beswasa = int(remaining_area // 5)
            remaining_meters = remaining_area % 5
            record.remaining_meters = remaining_meters

    def _default_date():
        today = fields.Date.today()
        default_date = today + timedelta(days=90)
        return default_date

    # check property attachments files
    @api.constrains('property_attachments')
    def _check_attachment_types(self):
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'doc', 'docx', 'pdf', 'txt']
        for attachment in self.property_attachments:
            filename, extension = attachment.name.lower().rsplit('.', 1)
            if extension not in allowed_extensions:
                raise ValidationError(
                    "Sorry, only pictures and documents files are allowed. Please upload only pictures (jpg, jpeg, "
                    "png, gif, bmp) and documents (doc, docx, pdf, txt).")

    # def _check_attachment_types_and_size(self):
    #     for record in self:
    #         for attachment in record.attachment_ids:
    #             if attachment.file_size > 1048576:  # 1 MB limit
    #                 raise ValidationError("The selected file is over the maximum allowed file size (1MB).")
    #
    #             if attachment.name:
    #                 filename, extension = os.path.splitext(attachment.name.lower())
    #                 # Validate file extension or perform other checks if needed
    #             else:
    #                 raise ValidationError("Attachment name is empty.")

    # Check garden area
    @api.constrains('garden', 'garden_area')
    def _check_garden_area(self):
        for record in self:
            if record.garden == True and record.garden_area <= 0:
                raise ValidationError("The garden area must be greater than 0")


"""forPrint PDF report through custom button created"""
# def print_reports(self):
#     return self.env.ref('egp_property.action_report_property').report_action(self)
