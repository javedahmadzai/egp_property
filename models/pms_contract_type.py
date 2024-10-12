# -*- coding: utf-8 -*-
# Part of Odoo.

from odoo import api, fields, models
from random import randint


def _get_default_color(self):
    return randint(1, 11)


class ContractType(models.Model):
    _name = 'pms.contract.type'
    _description = 'EGP PMS Contract Type'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(compute='_compute_code', store=True, readonly=False)
    active = fields.Boolean(default=True)
    color = fields.Integer(string="Color", default=_get_default_color)
    sequence = fields.Integer()

    @api.depends('name')
    def _compute_code(self):
        for contract_type in self:
            if contract_type.code:
                continue
            contract_type.code = contract_type.name
