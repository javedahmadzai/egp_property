# -*- coding: utf-8 -*-
# Part of Odoo.

from random import randint

from odoo import fields, models


class AgentCategory(models.Model):

    _name = "epg.agent.category"
    _description = "EGP Agent Category"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)
    agent_ids = fields.Many2many('agent.view', 'category_id', string='Agents')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
