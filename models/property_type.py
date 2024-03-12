# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from random import randint


def _get_default_color(self):
    return randint(1, 11)


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = "property_type"
    _rec_name = "property_type"
    property_type = fields.Char(string="Location Type", required=True)
    sequence = fields.Integer(string="Sequence", default=1, help="Used to order stages. Lower is better.")
    property_ids = fields.One2many('real.estate', 'property_type_id', readonly=True, ondelete='cascade')
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string="Color", default=_get_default_color)
    offer_counts = fields.Integer(compute="_compute_offer")

    @api.depends('property_ids.name')
    def _compute_offer(self):
        for rec in self:
            rec.offer_counts = self.env['estate.property.offer'].search_count([('property_type_id', '=', rec.id)])

    def action_offer_count(self):
        return {
            'name': _('Offers'),
            'view_mode': 'list',
            'type': 'ir.actions.act_window',
            'domain': [('property_type_id', '=', self.id)],
            'res_model': 'estate.property.offer',
            'target': 'current',
        }


class PropertyTypeTag(models.Model):
    _name = 'property.type.tag'
    _rec_name = 'tag_name'
    _description = 'Property Type Tag'
    _order = "tag_name"
    tag_name = fields.Char(string="Tags", required=True)
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string="Color", default=_get_default_color)
    _sql_constraints = [
        ('unique_tag_name', 'unique(tag_name)', 'WARNING..\n Tag Name Must Be Unique from Each Other.')
    ]
