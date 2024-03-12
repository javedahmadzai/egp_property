# -*- coding: utf-8 -*-
# Part of Odoo.

from odoo import api, fields, models


class ContractType(models.Model):
    _name = 'pms.contract.type'
    _description = 'EGP PMS Contract Type'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(compute='_compute_code', store=True, readonly=False)
    sequence = fields.Integer()

    @api.depends('name')
    def _compute_code(self):
        for contract_type in self:
            if contract_type.code:
                continue
            contract_type.code = contract_type.name
