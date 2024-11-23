from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _, SUPERUSER_ID
import random
import re
from markupsafe import Markup
from random import randint


class AgentView(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'agent.view'
    _description = 'Agent View'
    _rec_name = "agent_name"
    reference = fields.Char(string='Agent ID', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    agent_type = fields.Selection([('employee', 'Employee'),
                                   ('external', 'External')
                                   ],
                                  string="Agent Type",
                                  required=True,
                                  default='employee')
    # agent_property_id = fields.Many2one('estate.property.type', string="Property Involved:", tracking=True)
    agent_name = fields.Char(string="Agent", tracking=True, required=True)
    agent_position_title = fields.Char(string="Position Title",required=True)
    agent_mail = fields.Char(string="Agent mail Id", tracking=True,)
    agent_address = fields.Char(string="Agent Address", tracking=True)
    agent_phone = fields.Char(string="Agent Phone:", tracking=True, required=True)
    agent_pic = fields.Binary(string="Agent Image")
    department_id = fields.Many2one('pms.department', string="Department")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    # emp_dep = fields.Many2one('hr.department', string="Department")

    # implements sql constraints to check agent mail ID
    _sql_constraints = [
        ('check_unique_email', 'UNIQUE(agent_mail)', "The Agent Email must be unique"),
    ]

    # For creating a Sequence Number
    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('agent.view')
        return super(AgentView, self).create(vals)

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
            # self.agent_address = self.employee_id.private_street
            # self.emp_dep = self.employee_id.department_id.id if self.employee_id.department_id else False
            self.agent_position_title = self.employee_id.job_id.name if self.employee_id.job_id else False
            # self.agent_address = self.employee_id.private_street or ""
            self.agent_pic = self.employee_id.image_1920

    @api.constrains('agent_phone')
    def check_agent_phone(self):
        for rec in self:
            if rec.agent_phone and len(str(rec.agent_phone)) > 14:
                raise ValidationError(
                    _("INVALID agent phone number ,\n The agent phone number cannot exceed 14 characters."))
