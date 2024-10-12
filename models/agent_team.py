import ast
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _


class AgentTeam(models.Model):
    _name = 'agent.team'
    _description = 'Agent Teams'

    name = fields.Char('Team Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    member_ids = fields.Many2many('agent.view', string="Team Members")
    color = fields.Integer("Color Index", default=0)

