# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from random import randint
from odoo.exceptions import UserError, ValidationError


def _get_default_color(self):
    return randint(1, 11)


class PmsDepartment(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'pms.department'
    _description = 'PMS Department'
    _rec_name = "department_name"

    department_name = fields.Char(string="Department Name")
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string="Color", default=_get_default_color)

    _sql_constraints = [
        ('unique_department_name', "unique(department_name)", "WARNING..\n Department Name Must Be Unique from Each "
                                                              "Other.")
    ]
