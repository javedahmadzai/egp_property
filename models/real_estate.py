# -*- coding: utf-8 -*-
import datetime
import random
import calendar
import re
from datetime import timedelta
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RealEstate(models.Model):
    _name = 'real.estate'
    _inherit = ['mail.thread', 'mail.activity.mixin', ]
    _description = 'Real Estate'
    _order = "state, id desc"
    _rec_name = "name"

    name = fields.Char(required=True, string="Title", tracking=True)
    property_type_id = fields.Many2one('estate.property.type', tracking=True, ondelete='cascade')
    # for many selections
    property_type = fields.Many2many('estate.property.type', tracking=True, ondelete='cascade')
    description = fields.Text(tracking=True)
    # postcode = fields.Char(tracking=True)
    # date_availability = fields.Date(default=lambda self: _default_date())
    date_availability = fields.Date(default=fields.Date.context_today)
    deed_number = fields.Text(string="Deed or title deed number")
    # add four sides fields
    north = fields.Char(string="North")
    east = fields.Char(string="Est")
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
    bedrooms = fields.Integer(default=2, tracking=True)
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
    current_status = fields.Selection([
        ('use', 'مازاد'),
        ('not_use', 'غير مازاد')
    ], required=True, default='not_use', string='Current Status')

    # add columns for a rent section
    tenant_ids = fields.One2many('tenant.payment', 'property_id', string="Tenants")
    # add column for property monthly rent payment
    monthly_rent = fields.Float(string="Monthly Rent", help="Monthly rent amount for the property")

    garage = fields.Boolean()
    garden = fields.Boolean()
    tag_ids = fields.Many2many('property.type.tag', tracking=True, ondelete='cascade')
    garden_area = fields.Integer(string="Garden Area(sqm)", tracking=True)
    garden_orientation = fields.Selection([('north', 'شمال'), ('south', 'جنوب'), ('east', 'ختيځ'), ('west', 'لويديځ')],
                                          tracking=True)
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancel', 'Cancelled')],
        string="Status", tracking=True, default='new', readonly=True)
    floors = fields.Char(string="Floors")
    grade_type_property = fields.Selection([
        ('first_grade', 'درجه اول'),
        ('second_grade', 'درجه دوم'),
        ('third_grade', 'درجه سوم'),
    ])
    # Define a Many2many field to store attachments/files for each Property
    property_attachments = fields.Many2many('ir.attachment', string='Attachments',
                                            domain="[('res_model', '=', 'real.estate')]")

    # property_attachments = fields.Many2many(
    #     'ir.attachment',
    #     string='ضميمه اسناد زمين',
    #     domain="[('res_model', '=', 'real.estate')]",
    #     file_mime="image/*,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    #     file_size=1048576,  # 1 MB in bytes
    # )

    email_id = fields.Char(string="Email")
    sales_person = fields.Many2one('res.users', string="Salesman", default=lambda self: self.env.user, tracking=True,
                                   ondelete='cascade')

    # sales_person_email = fields.Char(string="Seller_Email", related='sales_person.email', tracking=True)
    sale_buyer = fields.Many2one('res.partner', string="Buyer", tracking=True, ondelete='cascade')
    sale_buyer_email = fields.Char(string='Buyer Mail')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', ondelete='cascade', store=True)
    total_area = fields.Integer(string="Total Area(sqm)", compute='_compute_total_area', tracking=True, readonly=True,
                                store=True)
    ''' contract info '''
    contract_ids = fields.One2many('pms.offerghoshai', 'property_id', ondelete='cascade', store=True)
    # convert total area into Gereb, Beswa, Beswasa
    gereb = fields.Float(string="Gereb", compute="_compute_area_values", store=True)
    beswa = fields.Float(string="Beswa", compute="_compute_area_values", store=True)
    beswasa = fields.Float(string="Beswasa", compute="_compute_area_values", store=True)
    best_offer = fields.Float(compute='_compute_best_offer', string="Best Offered", readonly=True, deafult=0.0,
                              store=True)
    ''' building part info '''
    building_part_id = fields.One2many('building.part', 'property_id', ondelete='cascade')

    progress = fields.Integer(string="progress", compute="_compute_progress", store=True)
    price = fields.Float(related='offer_ids.price')  # For Demonstrate > Not Uses
    image = fields.Image(string="Upload Property Image")

    '''Agents Details Fields'''
    agent_id = fields.Many2one('agent.view', string="Agent", ondelte='cascade', tracking=True)
    agent_mail = fields.Char(string="Agent mail Id", related="agent_id.agent_mail", tracking=True)
    agent_address = fields.Char(string="Agent Address", related='agent_id.agent_address', tracking=True)
    agent_phone = fields.Char(string="Agent Phone:", related='agent_id.agent_phone', tracking=True)
    agent_pic = fields.Image(string="Agent Image", related='agent_id.agent_pic', tracking=True)
    # password = fields.Char(string="Password")

    '''below field For smart button '''
    count_offer = fields.Integer(compute="_compute_count_offer", store=True)
    count_tags = fields.Integer(compute="_compute_count_tags")
    property_types = fields.Integer(compute="_compute_count_property_types")
    total_properties = fields.Integer(string="Total Properties")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        total = 0
        for rec in self:
            total = rec.living_area + rec.garden_area
        self.total_area = total

    #  1st way for check maximum best offer give by Clients(Create Button Not Work When it apply)
    # @api.depends('offer_ids.price')
    # def _compute_best_offer(self):
    #     for rec in self:
    #         self.best_offer = max(rec.offer_ids.mapped('price'))

    # 2nd way for check maximum best offer give by Clients
    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        com = 0.0
        for rec in self.offer_ids:
            if rec.price > com:
                com = rec.price
        self.best_offer = com

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
            if self.state == 'sold':
                raise ValidationError(_("You can not Cancel a Property After Sold!!"))
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

    def action_offer_received(self):
        for rec in self:
            if self.state in ['sold', 'cancel']:
                raise ValidationError(_("You can not Cancel a Property After Sold!!"))
            else:
                self.state = 'offer_received'
        return True

    def action_offer_accept(self):
        for rec in self:
            if self.state in ['sold', 'cancel']:
                raise ValidationError(_("You can not Cancel a Property After Sold!!"))
            else:
                self.state = 'offer_accepted'
        return True

    # @api.constrains('postcode')
    # def check_postcode(self):
    #     for rec in self:
    #         if len(rec.postcode) != 6:
    #             raise ValidationError(_("INVALID POSTCODE ,\n Please Enter Correct Postcode"))

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

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'new':
                progress = random.randrange(1, 25)
            elif rec.state == 'offer_received':
                progress = random.randrange(25, 50)
            elif rec.state == 'offer_accepted':
                progress = random.randrange(50, 75)
            elif rec.state == "sold":
                progress = 100
            else:
                progress = 0
            rec.progress = progress

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

    @api.depends('offer_ids.partner_id')
    def _compute_count_offer(self):
        for rec in self:
            rec.count_offer = self.env['estate.property.offer'].search_count([('property_id', '=', rec.id)])

    def action_count_offer(self):
        return {
            'name': _('Total Offered'),
            'view_mode': 'list',
            'type': 'ir.actions.act_window',
            'domain': [('property_id', '=', self.id)],
            'res_model': 'estate.property.offer',
            'target': 'current',
        }

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

    # convert total area into automatic gereb, beswa, beswasa
    @api.depends('living_area')
    def _compute_area_values(self):
        for record in self:
            # Assuming 1 gereb = 2000 square meters
            record.gereb = int(record.living_area / 2000.0)

            # Assuming 1 gereb = 20 beswa
            record.beswa = int(record.gereb * 20)

            # Assuming 1 beswa = 20 beswasa
            record.beswasa = int(record.beswa * 20)

    def _default_date():
        today = fields.Date.today()
        default_date = today + timedelta(days=90)
        return default_date

    # implement email validation regex
    @api.onchange('email_id')
    def validate_mail(self):
        if self.email_id:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email_id)
            if match is None:
                raise ValidationError('Not a valid E-mail ID')

    # Check garden area
    @api.constrains('garden', 'garden_area')
    def _check_garden_area(self):
        for record in self:
            if record.garden == True and record.garden_area <= 0:
                raise ValidationError("The garden area must be greater than 0")


"""forPrint PDF report through custom button created"""
# def print_reports(self):
#     return self.env.ref('egp_property.action_report_property').report_action(self)
