from odoo import models, fields, api


class ResUser(models.Model):
    _inherit = 'res.users'
    property_ids = fields.One2many('real.estate', 'sales_person',
                                   domain=[('state', 'in', ['offer_received', 'offer_accepted'])])


class AccountMove(models.Model):
    _inherit = 'account.move'  # Inherit account.move model

    property_id = fields.Many2one('real.estate', string='Properties')
