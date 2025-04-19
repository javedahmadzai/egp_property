from odoo import models, fields, api


class ResUser(models.Model):
    _inherit = 'res.users'
    property_ids = fields.One2many('real.estate', 'sales_person',
                                   domain=[('state', 'in', ['offer_received', 'offer_accepted'])])


class AccountMove(models.Model):
    _inherit = 'account.move'  # Inherit account.move model

    property_id = fields.Many2one('real.estate', string='Properties')

    contract_id = fields.Many2one('pms.contract', string="Contract")


#  remove error when Two or more than two users added into same groups for ir.attachment model
class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def read(self, fields=None, load='_classic_read'):
        self = self.sudo()
        return super(IrAttachment, self).read(fields=fields, load=load)

    # make code field un-required in res.country.state model
class StateCountry(models.Model):
    _inherit = "res.country.state"

    code = fields.Char(required=False)