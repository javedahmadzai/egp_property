from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _, SUPERUSER_ID
import random
import re
from markupsafe import Markup


class AgentView(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'agent.view'
    _description = 'Agent Commission View'
    _rec_name = "agent_name"
    reference = fields.Char(string='Agent ID', required=True, copy=False, readonly=True, default=lambda self: _('New'))

    # property_name=fields.Many2one('real.estate',ondelete='cascade',tracking=True)
    # property_id=fields.Many2one('estate.property.offer',ondelete='cascade',tracking=True)

    agent_property_id = fields.Many2one('estate.property.type', string="Property Involved:", tracking=True)
    agent_name = fields.Char(string="Agent", tracking=True)
    agent_position_title = fields.Char(string="Position Title")
    agent_mail = fields.Char(string="Agent mail Id", tracking=True)
    agent_address = fields.Char(string="Agent Address", tracking=True)
    agent_phone = fields.Char(string="Agent Phone:", tracking=True)
    agent_pic = fields.Image(string="Agent Image", tracking=True)
    color = fields.Integer("Color Index", default=0)
    agent_exp = fields.Selection([
        ('fresher', 'FRESHER'),
        ('less_one', 'Less Than 1 Yr'),
        ('one_two', 'EXP > 1 year'),
        ('three_four', 'EXP > 3Year'),
        ('professional', 'Professional'),
    ], string="Agent Experience", default='one_two', tracking=True)
    agent_type = fields.Selection([('full_time', 'Full Time'), ('part_time', 'Part Time'), ('intern', 'Intern')],
                                  string="Agent Type", default="full_time")
    agent_language_ids = fields.Many2many('agent.language', string="Agent Language Known", tracking=True,
                                          ondelete="cascade")
    agent_residential = fields.Selection(
        [
            ('east_kbl', 'BR-UP-MP'),
            ('west_kbl', 'HR-AP'),
            ('south_kbl', 'HYD-BNG-KER'),
            ('others', 'OTHERS'),
            ('foreign', 'FOREIGN'),
        ], string="Agent Residential"
    )
    department_id = fields.Many2one('pms.department', string="Agent Department")

    # agents_ids = fields.One2many('real.estate', 'offer_agent_id', string='Agents')
    agent_id = fields.Many2one('agent.view', string="Agent", ondelte='cascade', tracking=True)
    offer_agent_ghoshai_id = fields.Many2one('pms.offerghoshai', string="Offer Ghoshai Agent")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    efficiency = fields.Integer(string="Language Efficiency", compute='_compute_efficiency')
    proficient_level = fields.Selection([
        ('intermediate', 'Intermediate'),
        ('beginner', 'Beginner'),
        ('professional', 'Professional'),
    ], string="Language Efficiency", required=True, Tracking=True, default='professional')
    agent_offers_ids = fields.One2many('real.estate', 'agent_id', ondelete='cascade', tracking=True)

    # implements sql constraints to check agent mail ID
    _sql_constraints = [
        ('check_unique_email', 'UNIQUE(agent_mail)', "The Agent Email must be unique"),
    ]

    # For creating a Sequence Number
    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('agent.view')
        return super(AgentView, self).create(vals)

    @api.depends('proficient_level')
    def _compute_efficiency(self):
        for rec in self:
            if rec.proficient_level == 'intermediate':
                efficiency = random.randrange(45, 70)
            elif rec.proficient_level == 'beginner':
                efficiency = random.randrange(20, 45)
            elif rec.proficient_level == 'professional':
                efficiency = random.randrange(70, 100)
            else:
                efficiency = 0
            rec.efficiency = efficiency

    # implement mail validation regex for agent mail
    @api.onchange('agent_mail')
    def validate_mail(self):
        if self.agent_mail:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.agent_mail)
            if match is None:
                raise ValidationError('Not a valid Agent E-mail ID')

    # get Employee info
    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.agent_name = self.employee_id.name
            self.agent_mail = self.employee_id.work_email
            self.agent_phone = self.employee_id.work_phone
            self.agent_position_title = self.employee_id.private_street
            # self.department_id = self.employee_id.department_id.id if self.employee_id.department_id else False
            self.agent_position_title = self.employee_id.job_id.name if self.employee_id.job_id else False
            self.agent_address = self.employee_id.private_street or ""


class AgentLangauge(models.Model):
    _name = 'agent.language'
    _rec_name = 'language'
    _description = 'Agent Info'
    language = fields.Char(string="Language", required=True)
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string="Color")
