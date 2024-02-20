# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class PmsDepartment(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'pms.department'
    _description = 'PMS Department'
    _rec_name = "department_name"

    department_name = fields.Char(string="Department Name")
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        ('unique_department_name', 'unique(department_name)', 'WARNING..\n Department Name Must Be Unique from Each Other.')
    ]