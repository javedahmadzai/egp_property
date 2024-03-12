from odoo import api, fields, models, _, tools
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class PmsContract(models.Model):
    _name = "pms.contract"
    _description = "Contract information"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "property_id"

    name = fields.Char('Contract Reference', required=True)
    active = fields.Boolean(default=True)

    date_start = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date(string='End Date', tracking=True, compute='_compute_one_year_contract',
                           inverse='_set_contract_end_date', store=True, readonly=False,
                           help="End date of the contract (if it's a fixed-term contract).")

    notes = fields.Html('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Running'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
        tracking=True, help='Status of the contract', default='draft')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')
    ], string='Kanban State', default='normal', tracking=True, copy=False)
    contract_type_id = fields.Many2one('pms.contract.type', "Contract Type")

    contract_status = fields.Selection(
        [('new', 'New'), ('draft', 'Draft'), ('running', 'Running'), ('close', 'Closed')],
        string="State", copy=False, store=True, default='new')

    meeting_address = fields.Char(string="Meeting Address", default='MCIT 14 Floor Procurement Office Meeting Room')
    property_id = fields.Many2one('real.estate', ondelete='cascade')
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
    monthly_rent = fields.Float(string="Monthly Rent", store=True, readonly=False,
                                help="Monthly rent amount for the property")
    ''' Winner info '''
    winner_id = fields.Many2one('res.partner', string="Winner")

    ''' displaying all offers'''
    offer_id = fields.One2many('estate.property.offer', 'offer_property_id', ondelete='cascade', store=True)

    ''' displaying Agent Teams '''
    agent_team_id = fields.Many2one('agent.team', string='Agent Team', store=True, readonly=False, ondelte='cascade')

    ''' Displaying winner or Tenant Payment info '''
    tenant_payment_ids = fields.One2many('tenant.payment', 'contract_id', string="Tenants")

    selling_price = fields.Float(string="Contracted Price", readonly=True, tracking=True)
    best_offer = fields.Float(compute='_compute_best_offer', string="Best Offered", readonly=True, default=0.0,
                              store=True)
    # New field to store the name of the agent who brought the best offer
    best_offer_agent_id = fields.Many2one('res.partner', string='Best Offer Agent', compute='_compute_best_offer_agent',
                                          store=True)
    offer_ids = fields.One2many('estate.property.offer', 'offer_property_id', string="Offers")

    '''below field For smart button '''
    count_offer = fields.Integer(compute="_compute_count_offer", store=True)

    # expand_states for state in search view
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    # getting contract for 1-year
    @api.depends('date_start')
    def _compute_one_year_contract(self):
        for rec in self:
            if rec.date_start:
                start_datetime = datetime.combine(rec.date_start, datetime.min.time())
                rec.date_end = start_datetime + timedelta(days=365)
            else:
                rec.date_end = False

    def _set_contract_end_date(self):
        for rec in self:
            if rec.date_end and not rec._context.get('from_ui', False):
                # Do not update contract_start_date when changing contract_end_date
                pass

    # compute or show best offer
    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for contract in self:
            max_price = max(contract.offer_ids.mapped('price')) if contract.offer_ids else 0.0
            contract.best_offer = max_price

    # display best offer Agent
    @api.depends('offer_ids.price')
    def _compute_best_offer_agent(self):
        for contract in self:
            best_offer = contract.offer_ids.sorted(key=lambda r: r.price, reverse=True)[:1]
            if best_offer:
                contract.best_offer_agent_id = best_offer[0].partner_id.id
            else:
                contract.best_offer_agent_id = False

    @api.depends('offer_id.partner_id')
    def _compute_count_offer(self):
        for rec in self:
            rec.count_offer = self.env['estate.property.offer'].search_count([('offer_property_id', '=', rec.id)])

    # return into offers
    def action_count_offer(self):
        return {
            'name': _('Total Offered'),
            'view_mode': 'list',
            'type': 'ir.actions.act_window',
            'domain': [('offer_property_id', '=', self.id)],
            'res_model': 'estate.property.offer',
            'target': 'current',
        }

    # 1st way for check maximum best offer give by Clients(Create Button Not Work When it apply)
    # @api.depends('offer_ids.price')
    # def _compute_best_offer(self):
    #     for rec in self:
    #         self.best_offer = max(rec.offer_ids.mapped('price'))

    # 2nd way for check maximum best offer give by Clients
    # @api.depends('offer_ids.price')
    # def _compute_best_offer(self):
    #     com = 0.0
    #     for rec in self.offer_ids:
    #         if rec.price > com:
    #             com = rec.price
    #     self.best_offer = com
