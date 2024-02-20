from odoo import api, fields, models, _, tools
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class PmsOfferGhoshai(models.Model):
    _name = "pms.offerghoshai"
    _description = "Offer Ghoshai information"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "property_id"

    contract_status = fields.Selection(
        [('new', 'New'), ('draft', 'Draft'), ('running', 'Running'), ('close', 'Closed')],
        string="State", copy=False, store=True, default='new')
    offer_ghoshai_date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    contract_start_date = fields.Date(string='Contract Start Date', default=fields.Date.context_today)
    contract_end_date = fields.Date(string='Contract End Date', compute='_compute_one_year_contract',
                                    inverse='_set_contract_end_date', store=True, readonly=False)
    meeting_address = fields.Char(string='Meeting Address', default='MCIT 14 Floor Procurement Office Meeting Room', )
    start_hour = fields.Datetime(string='Start Hour')
    start_hour1 = fields.Char(string='Start Time', compute='_compute_time', store=True)
    finish_hour1 = fields.Char(string='Finish Time', compute='_compute_time', store=True)
    end_hour = fields.Datetime(string='End Hour')
    day_name = fields.Char(string='Day Name', compute='_compute_day_name', store=True)
    note = fields.Text(string='Comments')
    property_id = fields.Many2one('real.estate', required=True, ondelete='cascade')
    bedrooms = fields.Integer(related='property_id.bedrooms', tracking=True, readonly=True)
    deed_number = fields.Text(related='property_id.deed_number', tracking=True, readonly=True)
    garden_area = fields.Integer(related='property_id.garden_area', tracking=True, readonly=True)
    living_area = fields.Integer(related='property_id.living_area', string="Living Area(sqm)", tracking=True,
                                 readonly=True)
    garden = fields.Boolean(related='property_id.garden', string='Garden', readonly=True)
    garage = fields.Boolean(related='property_id.garage', string='Garage', readonly=True)
    total_area = fields.Integer(related='property_id.total_area', string="Total Area(sqm)", tracking=True,
                                readonly=True)
    property_type = fields.Many2many(related='property_id.property_type', tracking=True,
                                     ondelete='cascade', readonly=True)
    expected_price = fields.Float(related='property_id.expected_price', tracking=True, readonly=True)
    tag_ids = fields.Many2many(related='property_id.tag_ids', tracking=True, ondelete='cascade')
    # add column for property monthly rent payment
    monthly_rent = fields.Float(string="Monthly Rent", store=True, readonly=True, help="Monthly rent amount for the property")
    ''' Winner info '''
    winner_id = fields.Many2one('res.partner', string="Winner")

    ''' displaying all offers'''
    offer_id = fields.One2many('estate.property.offer', 'offer_property_id', ondelete='cascade', store=True)

    ''' displaying Agent Teams '''
    agent_team_id = fields.Many2one('agent.team', string='Agent Team', store=True, readonly=False, ondelte='cascade')

    ''' Displaying Tenant Payment info '''
    # add columns for a rent section
    tenant_ids = fields.One2many('tenant.payment', 'property_id', string="Tenants")

    # getting time
    @api.depends('start_hour', 'end_hour')
    def _compute_time(self):
        for record in self:
            start_hour1 = 0
            finish_hour1 = 0
            if record.start_hour:
                start_hour1 = record.start_hour.strftime('%H:%M:%S')
                record.start_hour1 = start_hour1
            else:
                record.start_hour1 = False
            if record.end_hour:
                finish_hour1 = record.end_hour.strftime('%H:%M:%S')
                record.finish_hour1 = finish_hour1
            else:
                record.finish_hour1 = False

    # getting day name
    def _compute_day_name(self):
        for record in self:
            if record.offer_ghoshai_date:
                # Calculate the day name using strftime('%A')
                day_name = record.offer_ghoshai_date.strftime('%A')
                record.day_name = day_name
            else:
                record.day_name = False

    # getting contract for 1-year
    @api.depends('contract_start_date')
    def _compute_one_year_contract(self):
        for rec in self:
            if rec.contract_start_date:
                start_datetime = datetime.combine(rec.contract_start_date, datetime.min.time())
                rec.contract_end_date = start_datetime + timedelta(days=365)
            else:
                rec.contract_end_date = False

    def _set_contract_end_date(self):
        for rec in self:
            if rec.contract_end_date and not rec._context.get('from_ui', False):
                # Do not update contract_start_date when changing contract_end_date
                pass

    ''' Share Whatsapp msg with Tenant '''
